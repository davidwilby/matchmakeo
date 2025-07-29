from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

__all__ = [
    "Product"
]

@dataclass
class Product:

    data_dir: str | Path = TemporaryDirectory(),

