import asyncio

import aiohttp

from earthcare_downloader import utils

from .params import File, SearchParams
from .products import ESAProd, JAXAProd


async def get_files(params: SearchParams) -> list[File]:
    base_url = "https://ec-pdgs-discovery.eo.esa.int/socat"
    query_params = _get_query_params(params)

    product_groups = {
        "esa-lv1": [p for p in params.product if p in ESAProd and "1" in p],
        "esa-lv2": [p for p in params.product if p in ESAProd and "2" in p],
        "jaxa-lv2": [p for p in params.product if p in JAXAProd],
    }
    urls = {
        "esa-lv1": f"{base_url}/EarthCAREL1Validated/search",
        "esa-lv2": f"{base_url}/EarthCAREL2Validated/search",
        "jaxa-lv2": f"{base_url}/JAXAL2Validated/search",
    }

    async with aiohttp.ClientSession() as session:
        tasks = [
            _fetch_files(
                session,
                urls[level],
                {**query_params, "query.productType": prods},
            )
            for level, prods in product_groups.items()
            if prods
        ]
        results = await asyncio.gather(*tasks, return_exceptions=False)

    return [
        File(
            url=url,
            product=product,
            filename=url.split("/")[-1],
            server=url.split("/data/")[0],
        )
        for result in results
        for url in result
        for product in params.product
        if product in url
    ]


async def _fetch_files(
    session: aiohttp.ClientSession, url: str, query_params: dict
) -> list[str]:
    async with session.post(url, data=query_params) as response:
        response.raise_for_status()
        text = await response.text()
        return text.splitlines()


def _get_query_params(params: SearchParams) -> dict:
    query_params = {
        "service": "SimpleOnlineCatalogue",
        "version": "1.2",
        "request": "search",
        "format": "text/plain",
        "query.beginAcquisition.start": params.start,
        "query.endAcquisition.stop": params.stop,
        "query.endAcquisition.start": params.start,
        "query.beginAcquisition.stop": params.stop,
        "query.orbitNumber.min": params.orbit_min,
        "query.orbitNumber.max": params.orbit_max,
    }
    if (
        params.lat is not None
        and params.lon is not None
        and params.distance is not None
    ):
        lat_buffer = utils.distance_to_lat_deg(params.distance)
        lon_buffer = utils.distance_to_lon_deg(params.lat, params.distance)
        query_params["query.footprint.minlat"] = max(params.lat - lat_buffer, -90)
        query_params["query.footprint.minlon"] = max(params.lon - lon_buffer, -180)
        query_params["query.footprint.maxlat"] = min(params.lat + lat_buffer, 90)
        query_params["query.footprint.maxlon"] = min(params.lon + lon_buffer, 180)

    return query_params
