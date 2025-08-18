from abc import ABC
from dataclasses import dataclass
from pathlib import Path
import os

from sqlalchemy import create_engine, Engine, Connection
from geoalchemy2 import Geometry

from matchmakeo.utils import setUpLogging

log = setUpLogging(__name__)

class Database(ABC):

    """Abstract class for database connections.

    db_url (str): full custom connect string for database, will be used if specified
    """
    def __init__(self,
                database: str,
                username: str,
                password: str,
                host: str = "localhost",
                port: int = 5432,
                dialect: str = None,
                driver: str = None,
                db_url: str = None,
            ):
        self.database = database
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.dialect = dialect
        self.driver = driver
        self.db_url = db_url
        
        self.engine = None
        self.connection = None
        
    @property
    def url(self):
        if self.db_url:
            return self.db_url
        else:
            if self.driver:
                dialect_driver = f"{self.dialect}+{self.driver}"
            else:
                dialect_driver = self.dialect

            return f"{dialect_driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def create_engine(self) -> Engine:
        self.engine = create_engine(
            self.url,
            echo=False,
            plugins=["geoalchemy2"],
        )
        return self.engine
    
    def connect(self) -> Connection:
        if self.engine:
            try:
                self.connection = self.engine.connect()
            except ConnectionError:
                raise ConnectionError(f"Database connection failed. Aborting.")
            
            return self.connection
        
        else:
            log.info(f"No connection available yet. Trying to connect to {self.url}")
            self.create_engine()
            return self.connect()

    def execute(self):
        pass

class PostGISDatabase(Database):
    """Database connection for PostGIS databases.
    """

    def __init__(
            self,
            database,
            username,
            password,
            host = "localhost",
            port = 5432,
            db_url = None,
            dialect = "postgresql",
            driver = "psycopg",
            ):

        super().__init__(
            database,
            username,
            password,
            host,
            port,
            db_url=db_url,
            dialect=dialect,
            driver=driver,
            )
        
class SpatialiteDatabase(Database):

    def __init__(
        self,
        filename: str|Path,
        db_url = None,
        dialect = "sqlite",
        ):

        self.filename = filename

        os.environ["SPATIALITE_LIBRARY_PATH"] = "mod_spatialite"

        super().__init__(
            database=None,
            username=None,
            password=None,
            host=None,
            port=None,
            db_url=db_url,
            dialect=dialect,
            driver=None,
            )
        
    @property
    def url(self):
        # sqlite/spatialite connect strings/urls take a different format to standard so this class has a custom url prop method
        if self.db_url:
            return self.db_url
        else:

            return f"sqlite:///{self.filename}"
        
    def connect(self):
        log.info(f"Connecting to {self.url}. Note that creating a new db can take a few minutes.")
        return super().connect()
        