import logging

from pandas import Timestamp
import shapely

def setUpLogging(module_name = __name__):
    logger = logging.getLogger(module_name)
    FORMAT = "[%(filename)s . %(funcName)20s() ] %(message)s"
    logging.basicConfig(format=FORMAT)
    return logger

log = setUpLogging(__name__)

def coords_to_polygon(coords:list[tuple[float]]) -> str:
    """Takes an iterable of coordinate pairs and returns a WKT POLYGON string."""
    return shapely.Polygon(coords).wkt

def infer_sql_type(val) -> str:
    """"Takes a value and returns the appropriate SQL type."""

    if isinstance(val, float):
        return "FLOAT"
    elif isinstance(val, bool):
        return "BOOLEAN"
    elif isinstance(val, int):
        return "BIGINT"
    elif isinstance(val, str):
        return "TEXT"
    elif isinstance(val, dict) or isinstance(val, list):
        return "JSON"
    elif isinstance(val, Timestamp):
        return "TIMESTAMP"
    elif isinstance(val, shapely.geometry.Polygon):
        return "GEOMETRY(POLYGON, 4326)"
    elif val is None:
        log.warning("Unknown type for: None")
    else:
        log.warning(f"Unknown type for: {val}")
