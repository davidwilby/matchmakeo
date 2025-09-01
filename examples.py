"Example downloads including MODIS footprints."

from pathlib import Path

from sqlalchemy import String

from matchmakeo.queryset import NasaCMRQueryset
from matchmakeo.product import Product
from matchmakeo.catalogues import NasaCMR, Field
from matchmakeo.databases import PostGISDatabase

# create a database object
# create a catalogue object
# create dataset and query object
# run the download
# 

database = PostGISDatabase(
    username="postgres",
    password="password",
    database="matchmakeo",
    host="localhost",
    port=5432,
)

catalogue = NasaCMR(
    client_id="test_BAS",
    url="https://cmr.earthdata.nasa.gov/search/granules.json"#"https://cmr.sit.earthdata.nasa.gov/search/granules.json"
)

queryset = NasaCMRQueryset(
    start_date="2020-01-01",
    end_date="2020-01-31",
    page_size=200,
)

product = Product(
    short_name="MOD021KM",#  MOD021KM - terra (original download in ~April) /  Use MYD021KM - Aqua (new download in May)
    # data_dir=Path("./data/modis_aqua"),
    table="modis_aqua",
)

catalogue.download_footprints(
    product=product,
    queryset=queryset,
    database=database,
)