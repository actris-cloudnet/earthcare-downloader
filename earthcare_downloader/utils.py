import datetime
import math
from argparse import ArgumentTypeError
from typing import Final

from .products import VALID_PRODUCTS, Product, ProductsInput

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


def validate_coordinates(
    lat: float | None,
    lon: float | None,
    lat_range: tuple[float, float] | None,
    lon_range: tuple[float, float] | None,
) -> None:
    _validate_lat(lat)
    _validate_lon(lon)
    _validate_lat_range(lat_range)
    _validate_lon_range(lon_range)

    has_point = lat is not None or lon is not None
    has_range = lat_range is not None or lon_range is not None
    if has_point and has_range:
        raise ValueError(
            "Cannot use --lat/--lon together with --lat-range/--lon-range."
        )
    if (lat is None and lon is not None) or (lat is not None and lon is None):
        raise ValueError("Both latitude and longitude must be provided together.")
    if (lat_range is None and lon_range is not None) or (
        lat_range is not None and lon_range is None
    ):
        raise ValueError(
            "Both latitude range and longitude range must be provided together."
        )


def _validate_lat(lat: float | None) -> None:
    if lat is not None and (lat < -90 or lat > 90):
        raise ValueError("Latitude must be between -90 and 90 degrees.")


def _validate_lon(lon: float | None) -> None:
    if lon is not None and (lon < -180 or lon > 180):
        raise ValueError("Longitude must be between -180 and 180 degrees.")


def _validate_lat_range(lat_range: tuple[float, float] | None) -> None:
    if lat_range is not None:
        min_lat, max_lat = lat_range
        if min_lat < -90 or max_lat > 90 or min_lat >= max_lat:
            raise ValueError(
                "Latitude range must be between -90 and 90 degrees and min < max."
            )


def _validate_lon_range(lon_range: tuple[float, float] | None) -> None:
    if lon_range is not None:
        min_lon, max_lon = lon_range
        if min_lon < -180 or max_lon > 180 or min_lon >= max_lon:
            raise ValueError(
                "Longitude range must be between -180 and 180 degrees and min < max."
            )


def validate_products(products: ProductsInput) -> list[str]:
    if isinstance(products, str):
        raw_products = products.split(",")
    else:
        raw_products = [p.value if isinstance(p, Product) else p for p in products]

    input_products = set(raw_products)
    if invalid_products := (input_products - VALID_PRODUCTS):
        msg = f"Invalid product types: {', '.join(invalid_products)}."
        raise ArgumentTypeError(msg)
    return list(input_products)
