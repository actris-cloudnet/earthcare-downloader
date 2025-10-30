import datetime
from pathlib import Path

from . import utils
from .dl import download_files
from .metadata import get_files
from .utils import SearchParams, TaskParams


async def search(
    product: str,
    lat: float | None = None,
    lon: float | None = None,
    distance: float = 200,
    orbit_min: int = 0,
    orbit_max: int | None = None,
    start: str | datetime.date | None = None,
    stop: str | datetime.date | None = None,
) -> list[str]:
    if start is None:
        start = utils.MISSION_START
    elif isinstance(start, str):
        start = utils.str2date(start)

    if stop is None:
        stop = utils.today()
    elif isinstance(stop, str):
        stop = utils.str2date(stop)

    search_params = SearchParams(
        lat=lat,
        lon=lon,
        distance=distance,
        product=product,
        start=start,
        stop=stop,
        orbit_min=orbit_min,
        orbit_max=orbit_max or utils.MAX_ORBITS,
    )
    return await get_files(search_params)


async def download(
    urls: list[str],
    output_path: str | Path = Path("."),
    unzip: bool = False,
    max_workers: int = 5,
    quiet: bool = True,
    credentials: tuple[str, str] | None = None,
) -> list[Path]:
    if isinstance(output_path, str):
        output_path = Path(output_path)

    output_path.mkdir(parents=True, exist_ok=True)

    task_params = TaskParams(
        max_workers=max_workers,
        output_path=output_path,
        unzip=unzip,
        quiet=quiet,
        no_prompt=False,
        show=False,
    )

    return await download_files(urls, task_params, credentials)
