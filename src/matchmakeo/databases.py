from abc import ABC

from sqlalchemy import create_engine
from geoalchemy2 import Geometry

from matchmakeo.utils import setUpLogging

log = setUpLogging(__name__)

class Database(ABC):

    """Abstract class for database connections.
    """

    def __init__(
            self,
            database: str,
            username: str,
            password: str,
            host: str = "localhost",
            port: int = 5432,
            dialect: str = None,
            db_url: str = None,
            ):
        
        self.database = database
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.db_url = db_url
        self.dialect = dialect
        
    def _get_db_url(self):
        if self.db_url:
            return self.db_url
        else:
            return f"{self.dialect}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def connect(self):
        self.engine = create_engine()
        return self.engine
    
    def execute(self):
        pass

class PostGISDatabase(Database):
    """Database connection for PostGIS databases.
    """

    def __init__(self, database, username, password, host = "localhost", port = 5432, db_url = None):
        super().__init__(database, username, password, host, port, db_url=db_url, dialect="postgresql")