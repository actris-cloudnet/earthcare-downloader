# <img src="logo.png" width="35px"> earthcare-downloader

[![CI](https://github.com/actris-cloudnet/earthcare-downloader/actions/workflows/test.yml/badge.svg)](https://github.com/actris-cloudnet/earthcare-downloader/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/earthcare-downloader.svg)](https://badge.fury.io/py/earthcare-downloader)

A Python tool for downloading [EarthCARE](https://earth.esa.int/eogateway/missions/earthcare) satellite data

## Installation

```bash
python3 -m pip install earthcare-downloader
```

## CLI Usage

### Authentication

Store your [ESA EO Sign In](https://eoiam-idp.eo.esa.int/) credentials in the environment variables `ESA_EO_USERNAME` and `ESA_EO_PASSWORD`.
If these variables are not set, the program will prompt you to enter your credentials.

### Running the program

```
earthcare-downloader -p PRODUCT --lat LAT --lon LON [options]
```

where the arguments are:

| Argument              | Description                                                      |
| --------------------- | ---------------------------------------------------------------- |
| `-p`, `--product`     | Product type to download (see full list below).                  |
| `--lat LAT`           | Latitude of the target location.                                 |
| `--lon LON`           | Longitude of the target location.                                |
| `-d`, `--distance`    | Search radius around the location in km (default: **200**).      |
| `--start`             | Start date (YYYY-MM-DD).                                         |
| `--stop`              | Stop date (YYYY-MM-DD).                                          |
| `--orbit-min`         | Minimum orbit number (default: **0**).                           |
| `--orbit-max`         | Maximum orbit number (default: infinite).                        |
| `-o`, `--output-path` | Directory to save downloaded files (default: current directory). |
| `--max-workers`       | Maximum number of concurrent downloads (default: **5**).         |
| `--show`              | Show filenames before downloading.                               |
| `--unzip`             | Automatically unzip downloaded files.                            |
| `--disable-progress`  | Hide progress bars during download.                              |
| `--no-prompt`         | Skip confirmation prompt before downloading.                     |
| `-h`, `--help`        | Show help message and exit.                                      |

Available products:

| Level        | Product Code                                                                   | Description                                      |
| ------------ | ------------------------------------------------------------------------------ | ------------------------------------------------ |
| **Level 1**  | [ATL_NOM_1B](https://earthcarehandbook.earth.esa.int/catalogue/atl_nom_1b)     | ATLID Nominal Mode                               |
|              | [AUX_JSG_1D](https://earthcarehandbook.earth.esa.int/catalogue/aux_jsg_1d)     | Auxiliary Joint Standard Grid                    |
|              | [BBR_NOM_1B](https://earthcarehandbook.earth.esa.int/catalogue/bbr_nom_1b)     | Broadband Radiometer Nominal Mode                |
|              | [BBR_SNG_1B](https://earthcarehandbook.earth.esa.int/catalogue/bbr_sng_1b)     | Broadband Radiometer Single View                 |
|              | [CPR_NOM_1B](https://earthcarehandbook.earth.esa.int/catalogue/cpr_nom_1b)     | Cloud Profiling Radar Nominal Mode               |
|              | [MSI_NOM_1B](https://earthcarehandbook.earth.esa.int/catalogue/msi_nom_1b)     | Multi-Spectral Imager Nominal Mode               |
|              | [MSI_RGR_1C](https://earthcarehandbook.earth.esa.int/catalogue/msi_rgr_1c)     | Multi-Spectral Imager Re-Gridded                 |
| **Level 2A** | [ATL_ARE_2A](https://earthcarehandbook.earth.esa.int/catalogue/atl_aer_2a)     | ATLID Aerosol Parameters                         |
|              | [ATL_ALD_2A](https://earthcarehandbook.earth.esa.int/catalogue/atl_ald_2a)     | ATLID Aerosol Layer Descriptors                  |
|              | [ATL_CTH_2A](https://earthcarehandbook.earth.esa.int/catalogue/am__cth_2b)     | ATLID Cloud Top Height                           |
|              | [ATL_EBD_2A](https://earthcarehandbook.earth.esa.int/catalogue/atl_ebd_2a)     | ATLID Extinction, Backscatter and Depolarization |
|              | [ATL_FM\_\_2A](https://earthcarehandbook.earth.esa.int/catalogue/atl_fm__2a)   | ATLID Feature Mask                               |
|              | [ATL_ICE_2A](https://earthcarehandbook.earth.esa.int/catalogue/atl_ice_2a)     | ATLID Ice Water Content                          |
|              | [ATL_TC\_\_2A](https://earthcarehandbook.earth.esa.int/catalogue/ac__tc__2b)   | ATLID Target Classification                      |
|              | [CPR_CD\_\_2A](https://earthcarehandbook.earth.esa.int/catalogue/cpr_cd__2a)   | CPR Cloud Droplet                                |
|              | [CPR_CLD_2A](https://earthcarehandbook.earth.esa.int/catalogue/cpr_cld_2a)     | CPR Cloud Parameters                             |
|              | [CPR_FMR_2A](https://earthcarehandbook.earth.esa.int/catalogue/cpr_fmr_2a)     | CPR Feature Mask and Reflectivity                |
|              | [CPR_TC\_\_2A](https://earthcarehandbook.earth.esa.int/catalogue/cpr_tc__2a)   | CPR Target Classification                        |
|              | [MSI_AOT_2A](https://earthcarehandbook.earth.esa.int/catalogue/msi_aot_2a)     | MSI Aerosol Optical Thickness                    |
|              | [MSI_CM\_\_2A](https://earthcarehandbook.earth.esa.int/catalogue/msi_cm__2a)   | MSI Cloud Mask                                   |
|              | [MSI_COP_2A](https://earthcarehandbook.earth.esa.int/catalogue/msi_cop_2a)     | MSI Cloud Optical Properties                     |
| **Level 2B** | [AC\_\_TC\_\_2B](https://earthcarehandbook.earth.esa.int/catalogue/ac__tc__2b) | ATLID-CPR Target Classification                  |
|              | [AM\_\_ACD_2B](https://earthcarehandbook.earth.esa.int/catalogue/am__acd_2b)   | ATLID-MSI Aerosol Column Descriptors             |
|              | [AM\_\_CTH_2B](https://earthcarehandbook.earth.esa.int/catalogue/am__cth_2b)   | ATLID-MSI Cloud Top Height                       |
|              | [BM\_\_RAD_2B](https://earthcarehandbook.earth.esa.int/catalogue/bm__rad_2b)   | BBR-MSI Radiative Fluxes and Heating Rates       |

### Examples

Download all `CPR_TC__2A` overpass data within 5 km of Hyytiälä, Finland:

```bash
earthcare-downloader --lat 61.844 --lon 24.287 --distance 5 --product CPR_TC__2A
```

## Python API

You can also use earthcare-downloader as a Python library:

```python
from earthcare_downloader import search, download

urls = search(product="CPR_TC__2A", lat=61.844, lon=24.287, distance=5)
paths = download(urls, output_path="data/", unzip=True)
```

When working in notebooks, use the asynchronous versions of these functions:

```python
from earthcare_downloader.aio import search, download

urls = await search(product="CPR_TC__2A", lat=61.844, lon=24.287, distance=5)
paths = await download(urls, output_path="data/", unzip=True, disable_progress=True)
```

## License

MIT
