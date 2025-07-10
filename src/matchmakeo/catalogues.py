from abc import ABC, abstractmethod
import json

import requests

class Queryset:
    "Generic query parameters to be used in a catalogue request."

    def __init__(self,
                 start_year: int,
                 end_year: int,
                #  spatial range
                 ):
        pass

class DataProduct:

    def __init__(self):
        pass

class Catalogue(ABC):

    @abstractmethod
    def download(self,
                data_product: DataProduct,
                queryset: Queryset,
                table:str,
                primary_key:str = "id",
                ):
        pass

class EarthEngine(Catalogue):
    def __init__(self):
        raise NotImplementedError


class NasaCMR(Catalogue):
    """Interface to download from the NASA Common Metadata Repository (CMR) (<https://cmr.earthdata.nasa.gov/>) for all Earth Observing System Data and Information System (EOSDIS) metadata including MODIS footprints."
    User accounts and hence access to restricted data are not currently supported.
    """

    def __init__(self,
                 client_id: str,
                 url:str = "https://cmr.sit.earthdata.nasa.gov/search/granules.json", #"https://cmr.earthdata.nasa.gov/search/granules.json",
                 
                 ):
        super().__init__()

        """_summary_
        Params:
            client_id(str): Client Partners are strongly encouraged by NASA CMR, we suggest using your name or research group.
        """

    def download(self,
                 *args,
                 **kwargs
                 ):
        super().download(*args, **kwargs)

        # if not table:
            # if no table name specified, generate one

        raise NotImplementedError