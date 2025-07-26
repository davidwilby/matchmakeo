from abc import ABC, abstractmethod
from datetime import date, timedelta
import json
from pathlib import Path
from tempfile import TemporaryFile

import requests

from .databases import DatabaseConnection
from .product import Product
from .queryset import Queryset, NasaCMRQueryset
from .utils import setUpLogging

log = setUpLogging(__name__)


__all__ = [
    "Catalogue",
    "NasaCMR",
]

class Catalogue(ABC):

    def download(self,
                product: Product,
                queryset: Queryset,
                download_to_file:bool = False,
                download_to_db:bool = True,
                insert_into_db:bool = True,
                ):
        
        self.product = product
        self.queryset = queryset

        if download_to_file:
            self.download_to_file(product, queryset)

            if insert_into_db:
                self.insert_into_db()
        
        if download_to_db:
            self.download_to_file(product, queryset)


    @abstractmethod
    def download_to_file(product, queryset):
        return
        

    def insert_into_db(self,
                db_connection: DatabaseConnection,
                table:str,
                primary_key:str = "id",
                ):
        
        data_dir = self.data_dir

        # if not table:
            # if no table name specified, generate one




class NasaCMR(Catalogue):
    """Interface to download from the NASA Common Metadata Repository (CMR) (<https://cmr.earthdata.nasa.gov/>) for all Earth Observing System Data and Information System (EOSDIS) metadata including MODIS footprints."
    Note: User accounts and hence access to restricted data are not currently supported.
    """

    def __init__(self,
                 client_id: str,
                 url:str = "https://cmr.sit.earthdata.nasa.gov/search/granules.json", #"https://cmr.earthdata.nasa.gov/search/granules.json",
                 ):
        super().__init__()

        """_summary_
        Params:
            client_id(str): Client ids are strongly encouraged by NASA CMR, we suggest using your name or research group.
        """

    def download_to_db(self):
        raise NotImplementedError
    
    def insert_into_db(self, db_connection, table, primary_key = "id"):
        raise NotImplementedError

    def download_to_file(self,
                 ):

        # TODO refactor to use warnings like this for all catalogues
        if type(self.queryset) is not NasaCMRQueryset:
            raise UserWarning(f"For NasaCMR request, queryset of type NasaCMRQueryset is advised. Got {type(self.queryset)} instead. Some features may not work as intended.")
        

        next_day = self.queryset + timedelta(days=1)

        more_data = True

        geojson = {
            "type": "FeatureCollection",
            "features": []
        }


        while more_data:
            # Query parameters
            params = {
                "short_name": self.queryset.shortname, #"MOD021KM",  #  MOD021KM - terra (original download in ~April) /  Use MYD021KM - Aqua (new download in May)
                "page_size": self.queryset.page_size,
                'temporal': f"{date.strftime('%Y-%m-%d')}T00:00:00Z,{next_day.strftime('%Y-%m-%d')}T00:00:00Z"
            }

            if self.queryset.version:
                params.update({"version": self.queryset.version})

            if getattr(self.queryset, "concept_id", None):
                params.update(self.queryset.concept_id)

            # if there is a previous response, check for additional available pagesm
            # as recommended by CMR https://wiki.earthdata.nasa.gov/display/CMR/CMR+Harvesting+Best+Practices
            if 'response' in locals():

                # if previous response has CMR-Search-After header, add details to request headers
                if response.headers.get("CMR-Search-After"):
                    params = params.update({
                        "CMR-Search-After": response.headers.get("CMR-Search-After")
                    })

                else:
                # if there is a previous response and does not have CMR-Search-After header, there is no more data
                    more_data = False
            
            # Request granule metadata
            response = requests.get(self.url, params=params)

            if response.status_code != 200:
                log.info(f"Error: {response.text}")
                return

            granules = response.json()

            log.info(response.text)

            more_data = len(granules["feed"]["entry"]) > 0

            for g in granules["feed"]["entry"]:

                coords = None
                for poly in g["polygons"][0]:
                    vals   =  list ( map (float, poly.split() ) )
                    coords = [list ( zip( vals[1::2], vals[::2] ) )]

                props = {}

                for prop in g:
                    if not prop in ["polygons"]:
                        props[prop] = g[prop]

                if coords:
                    geojson["features"].append({
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": coords
                        },
                        "properties": props
                    })

            if not geojson["features"]:
                print(f"No footprints found for {date}")
                return

            # Save as GeoJSON file
            with open(TemporaryFile(dir=self.data_dir, suffix=".geojson"), "w") as f:
                json.dump(geojson, f)


        # print(f"MODIS footprints saved {date} in {page_num} steps")
