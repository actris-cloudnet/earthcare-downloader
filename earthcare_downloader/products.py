from collections import defaultdict
from collections.abc import Iterable
from enum import Enum
from typing import TypeAlias


class ESAProd(str, Enum):
    # L1 products
    ATL_NOM_1B = "ATL_NOM_1B"
    AUX_JSG_1D = "AUX_JSG_1D"
    BBR_NOM_1B = "BBR_NOM_1B"
    BBR_SNG_1B = "BBR_SNG_1B"
    CPR_NOM_1B = "CPR_NOM_1B"
    MSI_NOM_1B = "MSI_NOM_1B"
    MSI_RGR_1C = "MSI_RGR_1C"
    # L2 products
    ACM_CAP_2B = "ACM_CAP_2B"
    ACM_COM_2B = "ACM_COM_2B"
    ACM_RT__2B = "ACM_RT__2B"
    AC__CLP_2B = "AC__CLP_2B"
    AC__TC__2B = "AC__TC__2B"
    ALL_3D__2B = "ALL_3D__2B"
    ALL_DF__2B = "ALL_DF__2B"
    AM__ACD_2B = "AM__ACD_2B"
    AM__CTH_2B = "AM__CTH_2B"
    ATL_AER_2A = "ATL_AER_2A"
    ATL_ALD_2A = "ATL_ALD_2A"
    ATL_CLA_2A = "ATL_CLA_2A"
    ATL_CTH_2A = "ATL_CTH_2A"
    ATL_EBD_2A = "ATL_EBD_2A"
    ATL_FM__2A = "ATL_FM__2A"
    ATL_ICE_2A = "ATL_ICE_2A"
    ATL_TC__2A = "ATL_TC__2A"
    BMA_FLX_2B = "BMA_FLX_2B"
    BM__RAD_2B = "BM__RAD_2B"
    CPR_CD__2A = "CPR_CD__2A"
    CPR_CLD_2A = "CPR_CLD_2A"
    CPR_FMR_2A = "CPR_FMR_2A"
    CPR_TC__2A = "CPR_TC__2A"
    MSI_AOT_2A = "MSI_AOT_2A"
    MSI_CM__2A = "MSI_CM__2A"
    MSI_COP_2A = "MSI_COP_2A"


class JAXAProd(str, Enum):
    ACM_CLP_2B = "ACM_CLP_2B"
    AC__CLP_2B = "AC__CLP_2B"
    ALL_RAD_2B = "ALL_RAD_2B"
    ATL_CLA_2A = "ATL_CLA_2A"
    CPR_CLP_2A = "CPR_CLP_2A"
    CPR_ECO_2A = "CPR_ECO_2A"
    MSI_CLP_2A = "MSI_CLP_2A"


class OrbitData(str, Enum):
    AUX_ORBPRE = "AUX_ORBPRE"
    MPL_ORBSCT = "MPL_ORBSCT"


class MetData(str, Enum):
    AUX_MET_1D = "AUX_MET_1D"


class AuxData(str, Enum):
    AUX_ORBPRE = "AUX_ORBPRE"
    AUX_ORBRES = "AUX_ORBRES"
    BBR_SOL_1B = "BBR_SOL_1B"
    GEO_ATTOBS = "GEO_ATTOBS"
    GEO_ORBOBS = "GEO_ORBOBS"


Product: TypeAlias = ESAProd | JAXAProd | OrbitData | MetData | AuxData
ProductInput: TypeAlias = str | Product
ProductsInput: TypeAlias = ProductInput | Iterable[ProductInput]

VALID_PRODUCTS = (
    {e.value for e in ESAProd}
    | {e.value for e in JAXAProd}
    | {e.value for e in OrbitData}
    | {e.value for e in MetData}
    | {e.value for e in AuxData}
)

_COLLECTION_PRODUCTS: dict[str, list[str]] = {
    "EarthCAREL1Validated_MAAP": [
        "ATL_NOM_1B",
        "AUX_JSG_1D",
        "BBR_NOM_1B",
        "BBR_SNG_1B",
        "CPR_NOM_1B",
        "MSI_NOM_1B",
        "MSI_RGR_1C",
    ],
    "EarthCAREL2Validated_MAAP": [
        "ACM_CAP_2B",
        "ACM_COM_2B",
        "ACM_RT__2B",
        "AC__CLP_2B",
        "AC__TC__2B",
        "ALL_3D__2B",
        "ALL_DF__2B",
        "AM__ACD_2B",
        "AM__CTH_2B",
        "ATL_AER_2A",
        "ATL_ALD_2A",
        "ATL_CLA_2A",
        "ATL_CTH_2A",
        "ATL_EBD_2A",
        "ATL_FM__2A",
        "ATL_ICE_2A",
        "ATL_TC__2A",
        "BMA_FLX_2B",
        "BM__RAD_2B",
        "CPR_CD__2A",
        "CPR_CLD_2A",
        "CPR_FMR_2A",
        "CPR_TC__2A",
        "MSI_AOT_2A",
        "MSI_CM__2A",
        "MSI_COP_2A",
    ],
    "JAXAL2Validated_MAAP": [
        "ACM_CLP_2B",
        "AC__CLP_2B",
        "ALL_RAD_2B",
        "ATL_CLA_2A",
        "CPR_CLP_2A",
        "CPR_ECO_2A",
        "MSI_CLP_2A",
    ],
    "EarthCAREOrbitData_MAAP": [
        "AUX_ORBPRE",
        "MPL_ORBSCT",
    ],
    "EarthCAREXMETL1DProducts10_MAAP": [
        "AUX_MET_1D",
    ],
    "EarthCAREAuxiliary_MAAP": [
        "AUX_ORBPRE",
        "AUX_ORBRES",
        "BBR_SOL_1B",
        "GEO_ATTOBS",
        "GEO_ORBOBS",
    ],
}

PRODUCT_TO_COLLECTIONS: dict[str, list[str]] = defaultdict(list)
for _collection, _products in _COLLECTION_PRODUCTS.items():
    for _product in _products:
        PRODUCT_TO_COLLECTIONS[_product].append(_collection)
