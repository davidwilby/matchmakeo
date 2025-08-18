from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
import itertools
from pathlib import Path
import os
from tempfile import TemporaryFile
import warnings

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, DateTime, Float, Connection
from sqlalchemy.sql.type_api import TypeEngine
from geoalchemy2 import Geometry
import requests
from tqdm import tqdm

from .databases import Database
from .product import Product
from .queryset import Queryset, NasaCMRQueryset
from .utils import setUpLogging

log = setUpLogging(__name__)


__all__ = [
    "Catalogue",
    "NasaCMR",
]


class Field(dict):
    """Fields to be created in database."""
    def __init__(self, column_name:str, column_type:TypeEngine):
        self.name = column_name

        if isinstance(column_type, TypeEngine) or issubclass(column_type, TypeEngine):
            self.type = column_type
        else:
            warnings.warn(f"Custom field types must be SQL Alchemy types. Got {type(column_type)} for {column_name}.\n\
                          Unexpected behaviour may occur.")
            
    def _as_column(self):
        return Column(self.name, self.type)

class Catalogue(ABC):

    def __init__(self, url, queryset_type: Queryset = None):
        self.url = url
        
        if queryset_type:
            self.queryset_type = queryset_type

        self.fields = {
            'id': Field('id', String),
            'geometry': Field('geometry', Geometry('POLYGON', srid=4326)),
            'datetime_start': Field('datetime_start', DateTime),
            'datetime_end': Field('datetime_end', DateTime),
        }

    def download_footprints(self,
                product: Product,
                queryset: Queryset,
                database: Database,
                primary_key:str = "id",
                ):
        """Abstract method"""
        self._check_queryset_type(queryset=queryset)
    
    def _check_queryset_type(self, queryset:Queryset):
        """Raise UserWarning if queryset type does not match catalogue type."""
        if type(queryset) is not self.queryset_type:
            warnings.warn(f"Queryset of type {self.queryset_type} is advised. Got {type(queryset)} instead. Some features may not work as intended.",
                          UserWarning)
            
    def _create_table(self, connection:Connection, product:Product, primary_key:str='pk'):

        metadata = MetaData()
        table = Table(product.table, metadata,
            Column(primary_key, Integer, primary_key=True),
            *[v._as_column() for v in {**self.fields, **product.extra_fields}.values()]
        )

        table.create(connection, checkfirst=True)
        connection.commit()


class NasaCMR(Catalogue):
    """Interface to download from the NASA Common Metadata Repository (CMR) (<https://cmr.earthdata.nasa.gov/>) for all Earth Observing System Data and Information System (EOSDIS) metadata including MODIS footprints."
    Note: User accounts and hence access to restricted data are not currently supported.
    """

    def __init__(self,
                 client_id: str = None,
                 url:str = "https://cmr.sit.earthdata.nasa.gov/search/granules.json", #"https://cmr.earthdata.nasa.gov/search/granules.json",
                 queryset_type: Queryset = NasaCMRQueryset,
                 ):
        """_summary_
        Params:
            client_id(str): Client ids are strongly encouraged by NASA CMR, we suggest using your name or research group.
        """

        super().__init__(url=url, queryset_type=queryset_type)

        if client_id is None:
            log.warning("No client_id set. Client ids are strongly encouraged by NASA CMR, we suggest using your name or research group's name, for example.")

        # add fields specific to this catalogue
        additional_fields = {}
        self.fields.update(additional_fields)

    def download_footprints(self,
                product: Product,
                queryset: Queryset,
                database: Database,
                primary_key:str = "id",
                ):
        super().download_footprints(product=product, queryset=queryset, database=database, primary_key=primary_key)
       
        # data_dir = product.data_dir

        # if not os.path.exists(data_dir):
        #     os.makedirs(data_dir, exist_ok=True)



        try:
            connection = database.connect()
        except ConnectionError:
            raise ConnectionError(f"Database connection failed. Aborting.")

        self._create_table(connection, product)

        # Iterate through years and months
        for year, month, day in tqdm(itertools.product(
            range(queryset.start_year, queryset.end_year + 1),
            range(1,13),
            range(1,32)),
            desc="Days to query ",
            unit=" day",
            colour="green",
        ):
            try:
                current_date = datetime(year, month, day)
            except ValueError:
                continue

            if current_date > datetime.now():
                continue

            if datetime(year, month, 1) > current_date:
                continue

            # no data at start of project
            # TODO: is this universal for this catalogue?
            if year < 2000: # or (year == 2002 and month < 5):
                continue

            granules = self._download_single_date(product=product, queryset=queryset, date=current_date)
            log.info(f"{len(granules)} found for {current_date}")
            insertion = table.insert()
            for granule in granules:
                coords = granule[0][0]
                geometry = f"POLYGON(({coords[0][0]} {coords[0][1]},{coords[1][0]} {coords[1][1]},{coords[2][0]} {coords[2][1]},{coords[3][0]} {coords[3][1]},{coords[4][0]} {coords[4][1]}))"
                insertion = table.insert().values(
                    name=granule[1]['id'],
                    geometry=geometry,
                    producer_granule_id=granule[1]['producer_granule_id'],
                    day_night_flag=granule[1]['day_night_flag'],
                    coordinate_system=granule[1]['coordinate_system'],
                    time_start=granule[1]['time_start'],
                    time_end=granule[1]['time_end'],
                    updated=granule[1]['updated'],
                    granule_size=granule[1]['granule_size'],
                    collection_concept_id=granule[1]['collection_concept_id'],
                    title=granule[1]['title'],
                    )
                connection.execute(insertion)
                connection.commit()


    def _download_single_date(self,
                              product: Product,
                              queryset: Queryset,
                              date: date,
                              ):
        
        next_day = date + timedelta(days=1)

        more_data = True

        geojson = {
            "type": "FeatureCollection",
            "features": []
        }

        # iterate through pages of data
        while more_data:
            # Query parameters
            params = {
                "short_name": product.short_name,
                "page_size": queryset.page_size,
                'temporal': f"{date.strftime('%Y-%m-%d')}T00:00:00Z,{next_day.strftime('%Y-%m-%d')}T00:00:00Z"
            }

            headers = {}

            if queryset.version:
                params.update({"version": self.queryset.version})

            if getattr(queryset, "concept_id", None):
                params.update(self.queryset.concept_id)

            # if there is a previous response, check for additional available pages
            # as recommended by CMR https://wiki.earthdata.nasa.gov/display/CMR/CMR+Harvesting+Best+Practices
            if 'response' in locals():

                # if previous response has CMR-Search-After header, add details to request headers
                search_after = response.headers.get("CMR-Search-After", None)
                if search_after:
                    headers.update({
                        "CMR-Search-After": search_after,
                    })

                else:
                # if there is a previous response and does not have CMR-Search-After header, there is no more data
                    more_data = False
            
            # Request granule metadata
            response = requests.get(self.url, params=params, headers=headers)

            if response.status_code != 200:
                log.info(f"Error: {response.text}")
                return

            granules = response.json()

            log.info(response.text)

            more_data = len(granules["feed"]["entry"]) > 0

            footprints = []
            for g in granules["feed"]["entry"]:

                coords = None
                for poly in g["polygons"][0]:
                    vals   =  list ( map (float, poly.split() ) )
                    coords = [list ( zip( vals[1::2], vals[::2] ) )]

                props = {}

                for prop in g:
                    if not prop in ["polygons"]:
                        props[prop] = g[prop]

                # if coords:
                #     geojson["features"].append({
                #         "type": "Feature",
                #         "geometry": {
                #             "type": "Polygon",
                #             "coordinates": coords
                #         },
                #         "properties": props
                #     })

                footprints.append((coords, props))

            # if not geojson["features"]:
            #     print(f"No footprints found for {date}")
            #     return
            
            return footprints


