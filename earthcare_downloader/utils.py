import datetime
import math
from argparse import ArgumentTypeError
from typing import Final, get_args

from .metadata import Prod

MISSION_START: Final = datetime.date(2024, 5, 28)
MAX_ORBITS: Final = 1_000_000_000
EARTH_HALF_CIRCUMFERENCE: Final = 20040


def distance_to_lat_deg(distance: float) -> float:
    return round(distance / 111.32, 3)


def distance_to_lon_deg(lat: float, distance: float) -> float:
    return round(distance / (111.32 * math.cos(math.radians(lat))), 6)


def utctoday() -> datetime.date:
    return datetime.datetime.now(tz=datetime.timezone.utc).date()


def str2date(date_str: str) -> datetime.date:
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


def validate_lat(lat: float | None) -> None:
    if lat is not None and (lat < -90 or lat > 90):
        raise ValueError("Latitude must be between -90 and 90 degrees.")


def validate_lon(lon: float | None) -> None:
    if lon is not None and (lon < -180 or lon > 180):
        raise ValueError("Longitude must be between -180 and 180 degrees.")


def validate_products(products: str | list[str]) -> list[str]:
    if isinstance(products, str):
        products = products.split(",")

    input_products = set(products)
    valid_products = set(get_args(Prod))
    if invalid_products := (input_products - valid_products):
        raise ArgumentTypeError("Invalid product types: " + ", ".join(invalid_products))
    return list(input_products)
