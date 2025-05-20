import argparse
import asyncio
import logging
from pathlib import Path

from earthcare_downloader import dl
from earthcare_downloader.metadata import Prod


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
        "--radius",
        type=float,
        default=200,
        help="Distance [km] from the location to search for data (default: 200 km).",
    )
    parser.add_argument(
        "--product",
        type=str,
        default="CPR_NOM_1B",
        choices=Prod.__args__,
        help="Product type to download (default: CPR_NOM_1B).",
    )
    parser.add_argument(
        "--max_workers",
        type=int,
        default=5,
        help="Maximum number of concurrent downloads (default: 5).",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default=Path("."),
        help="Output directory for downloaded files (default: current directory).",
    )
    args = parser.parse_args()

    asyncio.run(
        dl.download_overpass_data(
            lat=args.lat,
            lon=args.lon,
            distance=args.radius,
            product=args.product,
            max_workers=args.max_workers,
            output_path=args.output_path,
        )
    )


if __name__ == "__main__":
    main()
