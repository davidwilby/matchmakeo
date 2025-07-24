
from dataclasses import dataclass

@dataclass
class Queryset:
    "Generic query parameters to be used in a catalogue request."

    start_year: int
    end_year: int
    #  spatial range
    page_size: int = 200


@dataclass
class NasaCMRQueryset(Queryset):
    "Extends the base Queryset with parameters specific to NASA CMR queries."
    
    short_name: str
    version: str = None
