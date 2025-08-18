from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

__all__ = [
    "Product"
]

@dataclass
class Product:

    short_name: str
    table: str
    # data_dir: str | Path = TemporaryDirectory(),
    extra_fields: dict

