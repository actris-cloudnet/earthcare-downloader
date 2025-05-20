from typing import Literal

import aiohttp

from earthcare_downloader import utils

Prod = Literal[
    "ATL_NOM_1B",
    "AUX_JSG_1D",
    "BBR_NOM_1B",
    "BBR_SNG_1B",
    "CPR_NOM_1B",
    "MSI_NOM_1B",
    "MSI_RGR_1C",
]


async def get_files(
    product: Prod, lat: float, lon: float, distance: float = 200
) -> list[str]:
    lat_buffer = utils.distance_to_lat_deg(distance)
    lon_buffer = utils.distance_to_lon_deg(lat, distance)
    url = "https://ec-pdgs-discovery.eo.esa.int/socat/EarthCAREL1Validated/search"
    query_params = {
        "service": "SimpleOnlineCatalogue",
        "version": "1.2",
        "request": "search",
        "format": "text/plain",
        "query.footprint.minlat": lat - lat_buffer,
        "query.footprint.minlon": lon - lon_buffer,
        "query.footprint.maxlat": lat + lat_buffer,
        "query.footprint.maxlon": lon + lon_buffer,
        "query.productType": product,
    }

    async with (
        aiohttp.ClientSession() as session,
        session.post(url, data=query_params) as response,
    ):
        response.raise_for_status()
        text = await response.text()
        return text.splitlines()
