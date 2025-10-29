import asyncio
import datetime
from pathlib import Path

from . import aio


def search(
    product: str,
    lat: float,
    lon: float,
    distance: float = 200,
    orbit_min: int = 0,
    orbit_max: int | None = None,
    start: str | datetime.date | None = None,
    stop: str | datetime.date | None = None,
) -> list[str]:
    """Search for EarthCARE data files matching the given parameters.

    Args:
        product: Product type to search for.
        lat: Latitude of the center point.
        lon: Longitude of the center point.
        distance: Search radius in kilometers. Default is 200 km.
        orbit_min: Minimum orbit number. Default is 0.
        orbit_max: Maximum orbit number. Default is None (no limit).
        start: Start date (inclusive) for data search. Default is mission start date.
        stop: Stop date (inclusive) for data search. Default is today's date.

    Returns:
        List of URLs of the matching data files.
    """
    return asyncio.run(
        aio.search(
            product,
            lat,
            lon,
            distance,
            orbit_min,
            orbit_max,
            start,
            stop,
        )
    )


def download(
    urls: list[str],
    output_path: str | Path = Path("."),
    unzip: bool = False,
    max_workers: int = 5,
    disable_progress: bool = False,
    credentials: tuple[str, str] | None = None,
) -> list[Path]:
    """Download EarthCARE data files from the given URLs.

    Args:
        urls: List of URLs to download.
        output_path: Directory to save the downloaded files. Default is current
            directory.
        unzip: Whether to unzip the downloaded files. Default is False.
        max_workers: Maximum number of concurrent download workers. Default is 5.
        disable_progress: Whether to disable progress bars during download.
            Default is False.
        credentials: Optional tuple of (username, password) for authentication.

    Returns:
        List of Paths to the downloaded files.

    """
    return asyncio.run(
        aio.download(
            urls,
            output_path,
            unzip,
            max_workers,
            disable_progress,
            credentials,
        )
    )
