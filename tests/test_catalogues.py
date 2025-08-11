import unittest

import pytest
from pytest_databases.docker.postgres import PostgresService

from matchmakeo.catalogues import NasaCMR
from matchmakeo.databases import PostGISDatabase
from matchmakeo.product import Product
from matchmakeo.queryset import Queryset

def test_queryset_type_warning(postgres_service: PostgresService):
    """Test that using the wrong queryset type for the catalogue results in a warning."""
    
    queryset = Queryset(
        start_year=2025,
        end_year=2025
    )
    product = Product(
        short_name="test"
    )
    catalogue = NasaCMR()
    database = PostGISDatabase(
        username=postgres_service.user,
        password=postgres_service.password,
        host=postgres_service.host,
        port=postgres_service.port,
        database=postgres_service.database,
    )
    
    with pytest.warns(UserWarning):
        catalogue._check_queryset_type(queryset)
