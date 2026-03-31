import asyncio
import contextlib
import datetime
from collections import defaultdict
from pathlib import Path

import aiohttp

from earthcare_downloader import utils

from .params import File, SearchParams
from .products import PRODUCT_TO_COLLECTIONS

BASE_URL = "https://catalog.maap.eo.esa.int/catalogue"

_COLLECTIONS_WITHOUT_ORBIT = {"EarthCAREOrbitData_MAAP", "EarthCAREAuxiliary_MAAP"}


async def get_files(params: SearchParams) -> list[File]:
    """Query MAAP STAC catalog and return matching files."""
    has_orbit_filter = params.orbit_min > 0 or params.orbit_max < utils.MAX_ORBITS

    collection_products: dict[str, list[str]] = defaultdict(list)
    for product in params.product:
        for collection in PRODUCT_TO_COLLECTIONS.get(product, []):
            if has_orbit_filter and collection in _COLLECTIONS_WITHOUT_ORBIT:
                continue
            collection_products[collection].append(product)

    async with aiohttp.ClientSession() as session:
        tasks = [
            _fetch_items(session, collection, products, params)
            for collection, products in collection_products.items()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=False)

    files = [_create_file(feature) for result in results for feature in result]
    if params.all is False:
        files = _parse_newest_file_versions(files)

    return files


def _create_file(feature: dict) -> File:
    """Parse a STAC feature into a File object."""
    props = feature["properties"]
    assets = feature["assets"]

    asset = assets["enclosure_h5"] if "enclosure_h5" in assets else assets["product"]

    url = asset["href"]
    filename = Path(url).name

    frame_start_time = datetime.datetime.strptime(
        props["datetime"], "%Y-%m-%dT%H:%M:%S.%fZ"
    )

    processing_time = None
    if "processing:datetime" in props and props["processing:datetime"]:
        with contextlib.suppress(ValueError, TypeError):
            processing_time = datetime.datetime.strptime(
                props["processing:datetime"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )

    return File(
        url=url,
        product=props["product:type"],
        filename=filename,
        baseline=props.get("version", ""),
        frame_start_time=frame_start_time,
        processing_time=processing_time,
        identifier=feature["id"],
        orbit=props.get("sat:absolute_orbit"),
        file_size=asset.get("file:size"),
    )


def _parse_newest_file_versions(files: list[File]) -> list[File]:
    files_filtered: dict[str, File] = {}
    for f in files:
        key = f.identifier
        current = files_filtered.get(key)
        if current is None:
            files_filtered[key] = f
        else:
            if f.baseline > current.baseline or (
                f.baseline == current.baseline
                and f.processing_time is not None
                and current.processing_time is not None
                and f.processing_time > current.processing_time
            ):
                files_filtered[key] = f
    return list(files_filtered.values())


async def _fetch_items(
    session: aiohttp.ClientSession,
    collection: str,
    products: list[str],
    params: SearchParams,
) -> list[dict]:
    """Fetch all matching STAC items with pagination."""
    body = _build_search_body(collection, products, params)
    items: list[dict] = []

    async with session.post(f"{BASE_URL}/search", json=body) as response:
        response.raise_for_status()
        data = await response.json()

    items.extend(data.get("features", []))

    next_link = _find_next_link(data.get("links", []))
    while next_link is not None:
        async with session.get(next_link["href"]) as response:
            response.raise_for_status()
            data = await response.json()

        items.extend(data.get("features", []))
        next_link = _find_next_link(data.get("links", []))

    return items


def _build_search_body(
    collection: str,
    products: list[str],
    params: SearchParams,
) -> dict:
    """Build a STAC search POST body."""
    body: dict = {
        "collections": [collection],
        "datetime": f"{params.start}T00:00:00Z/{params.stop}T23:59:59Z",
        "limit": 200,
    }

    bbox = _compute_bbox(params)
    if bbox is not None:
        body["bbox"] = bbox

    has_orbit = collection not in _COLLECTIONS_WITHOUT_ORBIT
    cql_filter = _build_cql_filter(products, params, has_orbit=has_orbit)
    if cql_filter:
        body["filter"] = cql_filter
        body["filter-lang"] = "cql2-text"

    return body


def _compute_bbox(params: SearchParams) -> list[float] | None:
    if params.lat is not None and params.lon is not None:
        lat_buf = utils.distance_to_lat_deg(params.distance)
        lon_buf = utils.distance_to_lon_deg(params.lat, params.distance)
        return [
            max(params.lon - lon_buf, -180),
            max(params.lat - lat_buf, -90),
            min(params.lon + lon_buf, 180),
            min(params.lat + lat_buf, 90),
        ]
    if params.lat_range is not None and params.lon_range is not None:
        return [
            params.lon_range[0],
            params.lat_range[0],
            params.lon_range[1],
            params.lat_range[1],
        ]
    return None


def _build_cql_filter(
    products: list[str],
    params: SearchParams,
    *,
    has_orbit: bool = True,
) -> str:
    """Build CQL2 filter string for product types and orbit constraints."""
    parts: list[str] = []

    if len(products) == 1:
        parts.append(f"\"product:type\"='{products[0]}'")
    elif len(products) > 1:
        clauses = [f"\"product:type\"='{p}'" for p in products]
        parts.append(f"({' OR '.join(clauses)})")

    if has_orbit:
        if params.orbit_min > 0:
            parts.append(f'"sat:absolute_orbit" >= {params.orbit_min}')
        if params.orbit_max < utils.MAX_ORBITS:
            parts.append(f'"sat:absolute_orbit" <= {params.orbit_max}')

    return " AND ".join(parts)


def _find_next_link(links: list[dict]) -> dict | None:
    for link in links:
        if link.get("rel") == "next":
            return link
    return None
