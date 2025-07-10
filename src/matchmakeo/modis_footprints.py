import requests
import json

import os
from datetime import datetime
from datetime import timedelta

"""
download MODIS footprints from NASA's CMR API and save them as GeoJSON files.
"""

def download_modis_footprints(date, out_file):

    # Define API URL
    url = "https://cmr.earthdata.nasa.gov/search/granules.json"

    next_day = date + timedelta(days=1)

    more_data = True
    page_num = 0

    geojson = {
        "type": "FeatureCollection",
        "features": []
    }


    while more_data:

        page_num += 1

        # Query parameters
        params = {
            "short_name": "MOD021KM",  #  MOD021KM - terra (original download in ~April) /  Use MYD021KM - Aqua (new download in May)
            # "version": "61",
            "page_size": "200",
            'temporal': f"{date.strftime('%Y-%m-%d')}T00:00:00Z,{next_day.strftime('%Y-%m-%d')}T00:00:00Z"
        }

        

        # Request granule metadata
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"Error: {response.text}")
            return

        granules = response.json()

        # print(response.text)

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
        print(f"No MODIS footprints found for {date}")
        return


    # Save as GeoJSON file
    with open(out_file, "w") as f:
        json.dump(geojson, f)


    print(f"MODIS footprints saved {date} in {page_num} steps")


def download_all( start_year=2020, end_year=2021):

    loc = "./data/modis_aqua_footprints"
    if not os.path.exists(loc):
        os.makedirs(loc,exist_ok=True)

    # Iterate through years and months
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            for day in range(1, 32):
                try:
                    current_date = datetime(year, month, day)
                except ValueError:
                    continue

                if current_date > datetime.now():
                    continue

                if datetime(year, month, 1) > current_date:
                    continue

                # no data at start of project
                if year < 2000: # or (year == 2002 and month < 5):
                    continue

                out_file = f"{loc}/modis_footprints_{current_date.year}_{current_date.month}_{current_date.day}.geojson"

                if os.path.exists(out_file):
                    print(f"File {out_file} already exists, skipping")
                    continue

                download_modis_footprints(current_date, out_file)


if __name__ == "__main__":
    download_all()