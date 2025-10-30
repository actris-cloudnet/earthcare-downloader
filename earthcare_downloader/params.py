import datetime
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SearchParams:
    lat: float | None
    lon: float | None
    distance: float
    product: list[str]
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
