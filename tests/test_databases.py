from matchmakeo.databases import PostGISDatabase

def test_database_url():
    db_name = "test_db"
    username = "test"
    password = "password"
    host = "localhost"
    port = 5432

    db = PostGISDatabase(
        database=db_name,
        username=username,
        password=password,
        host=host,
        port=port
    )

    dialect = "postgresql"

    expected_str = f"{dialect}://{username}:{password}@{host}:{port}/{db_name}"

    assert db._get_db_url() == expected_str