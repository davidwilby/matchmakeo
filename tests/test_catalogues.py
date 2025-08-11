import unittest

from matchmakeo.catalogues import NasaCMR

class TestNasaCmr(unittest.TestCase):

    def test_MODIS_download(self):
        
        catalogue = NasaCMR(
            url = "https://cmr.sit.earthdata.nasa.gov/search/granules.json",
            client_id="bas_matchmakeo_test"
        )

        
