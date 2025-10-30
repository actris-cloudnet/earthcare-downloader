import argparse
import asyncio
import logging
from pathlib import Path

from earthcare_downloader import dl
from earthcare_downloader.metadata import Prod

from . import utils
from .utils import SearchParams, TaskParams


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Download EarthCARE satellite data.")
    parser.add_argument(
        "-p",
        "--product",
        type=str,
        choices=Prod.__args__,
        help="Product type to download.",
        required=True,
    )
    parser.add_argument(
        "--lat",
        type=float,
        help="Latitude of the location to download data for.",
    )
    parser.add_argument(
        "--lon",
        type=float,
        help="Longitude of the location to download data for.",
    )
    parser.add_argument(
        "-d",
        "--distance",
        type=float,
        default=200,
        help="Distance [km] from the location to search for data (default: 200 km).",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=5,
        help="Maximum number of concurrent downloads (default: 5).",
    )
    parser.add_argument(
        "-o",
        "--output-path",
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
        type=lambda s: utils.str2date(s),
        help="Start date (inclusive) for data search in YYYY-MM-DD format.",
        default=utils.MISSION_START,
    )
    parser.add_argument(
        "--stop",
        type=lambda s: utils.str2date(s),
        help="Stop date (inclusive) for data search in YYYY-MM-DD format.",
        default=utils.today(),
    )
    parser.add_argument(
        "--unzip",
        action="store_true",
        help="Unzip downloaded files after download.",
        default=False,
    )
    parser.add_argument(
        "--orbit-min",
        type=int,
        help="Minimum orbit number.",
        default=0,
    )
    parser.add_argument(
        "--orbit-max",
        type=int,
        help="Maximum orbit number.",
        default=None,
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Disable progress bars during download.",
        default=False,
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Disable prompt for confirmation before downloading files.",
        default=False,
    )

    args = parser.parse_args()

    search_params = SearchParams(
        lat=args.lat,
        lon=args.lon,
        distance=args.distance,
        product=args.product,
        start=args.start,
        stop=args.stop,
        orbit_min=args.orbit_min,
        orbit_max=args.orbit_max or utils.MAX_ORBITS,
    )

    task_params = TaskParams(
        max_workers=args.max_workers,
        output_path=Path(args.output_path),
        unzip=args.unzip,
        show=args.show,
        quiet=args.quiet,
        no_prompt=args.no_prompt,
    )

    asyncio.run(
        dl.download_overpass_data(
            search_params,
            task_params,
        )
    )


if __name__ == "__main__":
    main()
