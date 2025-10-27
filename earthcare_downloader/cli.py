import argparse
import asyncio
import datetime
import logging
from pathlib import Path

from earthcare_downloader import dl
from earthcare_downloader.metadata import Prod

from .utils import SearchParams, TaskParams


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Download EarthCARE satellite data.")
    parser.add_argument(
        "--lat",
        type=float,
        help="Latitude of the location to download data for.",
        required=True,
    )
    parser.add_argument(
        "--lon",
        type=float,
        help="Longitude of the location to download data for.",
        required=True,
    )
    parser.add_argument(
        "-p",
        "--product",
        type=str,
        choices=Prod.__args__,
        help="Product type to download.",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--distance",
        type=float,
        default=200,
        help="Distance [km] from the location to search for data (default: 200 km).",
    )
    parser.add_argument(
        "--max_workers",
        type=int,
        default=5,
        help="Maximum number of concurrent downloads (default: 5).",
    )
    parser.add_argument(
        "-o",
        "--output_path",
        type=str,
        default=Path("."),
        help="Output directory for downloaded files (default: current directory).",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show files that would be downloaded.",
        default=False,
    )
    parser.add_argument(
        "--start",
        type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d").date(),
        help="Start date (inclusive) for data search in YYYY-MM-DD format.",
        default=datetime.date(2024, 5, 28),
    )
    parser.add_argument(
        "--stop",
        type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d").date(),
        help="Stop date (inclusive) for data search in YYYY-MM-DD format.",
        default=datetime.date.today(),
    )
    parser.add_argument(
        "--unzip",
        action="store_true",
        help="Unzip downloaded files after download.",
        default=False,
    )
    parser.add_argument(
        "--orbit_min",
        type=int,
        help="Minimum orbit number.",
        default=0,
    )
    parser.add_argument(
        "--orbit_max",
        type=int,
        help="Maximum orbit number.",
        default=1_000_000_000,
    )
    parser.add_argument(
        "--disable_progress",
        action="store_true",
        help="Disable progress bars during download.",
        default=False,
    )
    parser.add_argument(
        "--no_prompt",
        action="store_true",
        help="Disable prompt for confirmation before downloading files.",
        default=False,
    )

    args = parser.parse_args()

    params = SearchParams(
        lat=args.lat,
        lon=args.lon,
        distance=args.distance,
        product=args.product,
        start=args.start,
        stop=args.stop,
        orbit_min=args.orbit_min,
        orbit_max=args.orbit_max,
    )

    task_params = TaskParams(
        max_workers=args.max_workers,
        output_path=Path(args.output_path),
        unzip=args.unzip,
        show=args.show,
        disable_progress=args.disable_progress,
        no_prompt=args.no_prompt,
    )

    asyncio.run(
        dl.download_overpass_data(
            params,
            task_params,
        )
    )


if __name__ == "__main__":
    main()
