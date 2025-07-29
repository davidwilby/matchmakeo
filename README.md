# `matchmakeo`

**Alpha** - this project is in the early stages of development and should be considered unstable.

`matchmakeo` (*match-make-EE-OH*, [*mæʧ meɪk ee əʊ*]) is a python package to help with finding related earth observation data from two or more different sources. For example, if you wanted to find images from Sentinel-1 and MODIS of overlapping locations that were taken within 1 hour of each other.

## Get started

### Database requirements
`matchmakeo` works using a geospatial database, this can either be a one-off local database or a remote database provided you can connect to it and have permissions to create tables. Databases can either be PostgreSQL with the PostGIS extension, or SQLite with the Libspatialite extension.

For a basic example and for most use cases, we recommend using [docker](https://www.docker.com/get-started/) to spin up a local container with a [PostGIS image](https://hub.docker.com/r/postgis/postgis), this oneliner should do it:

```sh
docker run \
    --name matchmakeo-db \
    --volume ./data/db:/var/lib/postgresql/data \
    -p 5432:5432 \
    -e POSTGRES_DB=matchmakeo \
    -e POSTGRES_PASSWORD=password \
    -d --rm postgis/postgis
```

This will launch a postgis container named `matchmakeo-db` with a database named `matchmakeo` using the default username `postgres`, with data stored at local disk location `./data/db` - run `mkdir -p ./data/db` if you don't already have this location.

## Development

For working on development of `matchmakeo` we use [`pixi`](https://pixi.sh/) for managing PyPI and conda packages as well as for running deveopment tasks such as testing and linting. It isn't necessary for contributing to the package, but it's a nice tool. You can also use whatever python virtual environment manager you prefer + conda or even not use conda at all.