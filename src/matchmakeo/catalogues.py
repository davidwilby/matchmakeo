from abc import ABC, abstractmethod
from datetime import date, timedelta
import json
from pathlib import Path
from tempfile import TemporaryDirectory, TemporaryFile

import requests

from .databases import DatabaseConnection
from .product import Product
from .queryset import Queryset, NasaCMRQueryset
from .utils import setUpLogging

log = setUpLogging(__name__)

class Catalogue(ABC):

    @abstractmethod
    def download(self,
                product: Product,
                queryset: Queryset,
                data_dir: str | Path = TemporaryDirectory(),
                ):
        
        self.product = product
        self.queryset = queryset

    @abstractmethod
    def insert_db(self,
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

    def download(self,
                 *args,
                 **kwargs
                 ):
        super().download(*args, **kwargs)

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
                params = params.update({
                    "version": self.queryset.version
                })

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


        print(f"MODIS footprints saved {date} in {page_num} steps")
