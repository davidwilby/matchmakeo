"Example downloads including MODIS footprints."

from pathlib import Path

from matchmakeo.queryset import NasaCMRQueryset
from matchmakeo.product import Product
from matchmakeo.catalogues import NasaCMR
from matchmakeo.databases import PostGISDatabase

# create a catalogue object
# create dataset and query object
# create a database connection
# run the download
# 

database = PostGISDatabase(
    
)

catalogue = NasaCMR(
    client_id="test_BAS",
    url="https://cmr.earthdata.nasa.gov/search/granules.json"#"https://cmr.sit.earthdata.nasa.gov/search/granules.json"
)

queryset = NasaCMRQueryset(
    start_year=2020,
    end_year=2020,
    page_size=200,
)

product = Product(
    short_name="MOD021KM",  #"MOD021KM",  #  MOD021KM - terra (original download in ~April) /  Use MYD021KM - Aqua (new download in May)
    data_dir=Path("./data/modis_aqua"),
)

catalogue.download(
    product=product,
    queryset=queryset,
    download_to_file=True,
    download_to_db=False,
    insert_into_db=False,
)