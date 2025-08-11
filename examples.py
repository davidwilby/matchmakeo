"Example downloads including MODIS footprints."

from pathlib import Path

from matchmakeo.queryset import NasaCMRQueryset
from matchmakeo.product import Product
from matchmakeo.catalogues import NasaCMR

# create a catalogue object
# create dataset and query object
# create a database connection
# run the download
# 


catalogue = NasaCMR(
    client_id="test_BAS",
    url="https://cmr.sit.earthdata.nasa.gov/search/granules.json"
)

queryset = NasaCMRQueryset(
    start_year=2019,
    end_year=2020,
    page_size=200,
    short_name="MOD021KM"
)

product = Product(
    data_dir=Path("./data/modis_aqua"),
)

catalogue.download(
    product=product,
    queryset=queryset,
    download_to_file=True,
    download_to_db=False,
    insert_into_db=False,
)