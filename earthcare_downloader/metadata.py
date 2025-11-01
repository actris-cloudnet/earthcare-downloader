import asyncio
from typing import Literal

import aiohttp

from earthcare_downloader import utils

from .params import File, SearchParams

Prod = Literal[
    # L1 products
    "ATL_NOM_1B",
    "AUX_JSG_1D",
    "BBR_NOM_1B",
    "BBR_SNG_1B",
    "CPR_NOM_1B",
    "MSI_NOM_1B",
    "MSI_RGR_1C",
    # L2 products
    "AC__TC__2B",
    "AM__ACD_2B",
    "AM__CTH_2B",
    "ATL_ARE_2A",
    "ATL_ALD_2A",
    "ATL_CTH_2A",
    "ATL_EBD_2A",
    "ATL_FM__2A",
    "ATL_ICE_2A",
    "ATL_TC__2A",
    "BM__RAD_2B",
    "CPR_CD__2A",
    "CPR_CLD_2A",
    "CPR_FMR_2A",
    "CPR_TC__2A",
    "MSI_AOT_2A",
    "MSI_CM__2A",
    "MSI_COP_2A",
]


async def get_files(params: SearchParams) -> list[File]:
    base_url = "https://ec-pdgs-discovery.eo.esa.int/socat"
    query_params = _get_query_params(params)

    product_groups = {
        "1": [p for p in params.product if "1" in p],
        "2": [p for p in params.product if "2" in p],
    }
    urls = {
        "1": f"{base_url}/EarthCAREL1Validated/search",
        "2": f"{base_url}/EarthCAREL2Validated/search",
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
