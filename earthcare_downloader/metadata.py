from typing import Literal

import aiohttp

from earthcare_downloader import utils

from .utils import SearchParams

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


async def get_files(params: SearchParams) -> list[str]:
    lat_buffer = utils.distance_to_lat_deg(params.distance)
    lon_buffer = utils.distance_to_lon_deg(params.lat, params.distance)
    level = "2" if "2" in params.product else "1"
    url = (
        f"https://ec-pdgs-discovery.eo.esa.int/socat/EarthCAREL{level}Validated/search"
    )

    query_params = {
        "service": "SimpleOnlineCatalogue",
        "version": "1.2",
        "request": "search",
        "format": "text/plain",
        "query.footprint.minlat": params.lat - lat_buffer,
        "query.footprint.minlon": params.lon - lon_buffer,
        "query.footprint.maxlat": params.lat + lat_buffer,
        "query.footprint.maxlon": params.lon + lon_buffer,
        "query.productType": params.product,
        "query.beginAcquisition.start": params.start,
        "query.endAcquisition.stop": params.stop,
        "query.endAcquisition.start": params.start,
        "query.beginAcquisition.stop": params.stop,
        "query.orbitNumber.min": params.orbit_min,
        "query.orbitNumber.max": params.orbit_max,
    }

    async with (
        aiohttp.ClientSession() as session,
        session.post(url, data=query_params) as response,
    ):
        response.raise_for_status()
        text = await response.text()
        return text.splitlines()
