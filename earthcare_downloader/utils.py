import datetime
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SearchParams:
    lat: float
    lon: float
    product: str
    distance: float
    start: datetime.date
    stop: datetime.date
    orbit_min: int
    orbit_max: int


@dataclass
class TaskParams:
    max_workers: int
    output_path: Path
    unzip: bool
    show: bool
    disable_progress: bool
    no_prompt: bool


def distance_to_lat_deg(distance: float) -> float:
    return round(distance / 111.32, 3)


def distance_to_lon_deg(lat: float, distance: float) -> float:
    return round(distance / (111.32 * math.cos(math.radians(lat))), 3)
