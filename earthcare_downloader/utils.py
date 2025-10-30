import datetime
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Final

MISSION_START: Final = datetime.date(2024, 5, 28)
MAX_ORBITS: Final = 1_000_000_000
EARTH_HALF_CIRCUMFERENCE: Final = 20040


@dataclass
class SearchParams:
    lat: float | None
    lon: float | None
    distance: float
    product: str
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
    quiet: bool
    no_prompt: bool


def distance_to_lat_deg(distance: float) -> float:
    return round(distance / 111.32, 3)


def distance_to_lon_deg(lat: float, distance: float) -> float:
    return round(distance / (111.32 * math.cos(math.radians(lat))), 6)


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.timezone.utc)


def today() -> datetime.date:
    return utcnow().date()


def str2date(date_str: str) -> datetime.date:
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


def dt2str(dt: datetime.datetime) -> str:
    return dt.date().isoformat()


def validate_lat(lat: float | None) -> None:
    if lat is not None and (lat < -90 or lat > 90):
        raise ValueError("Latitude must be between -90 and 90 degrees.")


def validate_lon(lon: float | None) -> None:
    if lon is not None and (lon < -180 or lon > 180):
        raise ValueError("Longitude must be between -180 and 180 degrees.")
