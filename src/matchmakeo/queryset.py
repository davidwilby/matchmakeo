from dataclasses import dataclass
from datetime import date

__all__ = [
    "Queryset",
    "NasaCMRQueryset",
]

@dataclass(kw_only=True)
class Queryset:
    "Generic query parameters to be used in a catalogue request."

    start_date: date
    end_date: date
    #  spatial range
    page_size: int = 200


@dataclass(kw_only=True)
class NasaCMRQueryset(Queryset):
    "Extends the base Queryset with parameters specific to NASA CMR queries."
    
    version: str = None
