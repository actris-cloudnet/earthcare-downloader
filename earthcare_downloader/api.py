import asyncio
import datetime
from pathlib import Path

from . import aio
from .params import File
from .products import ProductsInput


def search(
    product: ProductsInput,
    start: str | datetime.date | None = None,
    stop: str | datetime.date | None = None,
    date: str | datetime.date | None = None,
    orbit_min: int = 0,
    orbit_max: int | None = None,
    orbit: int | None = None,
    lat: float | None = None,
    lon: float | None = None,
    radius: float | None = None,
    lat_range: tuple[float, float] | None = None,
    lon_range: tuple[float, float] | None = None,
    all: bool = False,
) -> list[File]:
    """Search for EarthCARE data files matching the given parameters.

    Args:
        product: Product type to search for.
        start: Start date (inclusive) for data search. Default is mission start date.
        stop: Stop date (inclusive) for data search. Default is today's date.
        date: Single date for data search. Overrides start and stop.
        orbit_min: Minimum orbit number. Default is 0.
        orbit_max: Maximum orbit number. Default is None (no limit).
        orbit: Single orbit number. Overrides orbit_min and orbit_max.
        lat: Latitude of the center point (-90 to 90 degrees).
        lon: Longitude of the center point (-180 to 180 degrees).
        radius: Search radius in kilometers. Default is whole Earth.
            Use with lat and lon.
        lat_range: Tuple specifying the latitude range (min_lat, max_lat).
            Use with lon_range.
        lon_range: Tuple specifying the longitude range (min_lon, max_lon).
            Use with lat_range.
        all: Whether to search for all versions (different baselines and/or
            processing runs) of the product. Default is False.

    Returns:
        List of File objects.
    """
    return asyncio.run(
        aio.search(
            product,
            start,
            stop,
            date,
            orbit_min,
            orbit_max,
            orbit,
            lat,
            lon,
            radius,
            lat_range,
            lon_range,
            all,
        )
    )


def download(
    files: list[File],
    output_path: str | Path = Path("."),
    by_product: bool = False,
    unzip: bool = False,
    max_workers: int = 5,
    quiet: bool | None = None,
    credentials: tuple[str, str] | None = None,
) -> list[Path]:
    """Download EarthCARE data files from the given File objects.

    Args:
        files: List of File objects to download.
        output_path: Directory to save the downloaded files. Default is current
            directory.
        by_product: Whether to create subdirectories for each product type.
            Default is False.
        unzip: Whether to unzip the downloaded files. Default is False.
        max_workers: Maximum number of concurrent download workers. Default is 5.
        quiet: Whether to disable progress bars during download. Default is False.
        credentials: Optional tuple of (username, password) for authentication.

    Returns:
        List of Paths to the downloaded files.

    """
    return asyncio.run(
        aio.download(
            files=files,
            output_path=output_path,
            by_product=by_product,
            unzip=unzip,
            max_workers=max_workers,
            quiet=quiet,
            credentials=credentials,
        )
    )
