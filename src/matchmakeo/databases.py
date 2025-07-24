from abc import ABC

from sqlalchemy import create_engine
from geoalchemy2 import Geometry

from matchmakeo.utils import setUpLogging

log = setUpLogging(__name__)

class DatabaseConnection(ABC):

    """Abstract class for database connections.
    """

    def __init__(self):
        raise NotImplementedError
    
    def connect(self):
        self.conn = create_engine()
        return self.conn
    
    def execute(self):
        pass

class PostGIS(DatabaseConnection):
    """Database connection for PostGIS databases.

    Args:
        DatabaseConnection (_type_): _description_
    """

    pass