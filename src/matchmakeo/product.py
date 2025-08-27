from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory

__all__ = [
    "Product"
]

@dataclass
class Product:

    short_name: str
    table: str
    extra_fields: list = field(default_factory=list)

