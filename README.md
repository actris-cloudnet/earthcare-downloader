# earthcare-downloader

[![CI](https://github.com/actris-cloudnet/earthcare-downloader/actions/workflows/test.yml/badge.svg)](https://github.com/actris-cloudnet/earthcare-downloader/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/earthcare-downloader.svg)](https://badge.fury.io/py/earthcare-downloader)

A command-line tool for downloading [EarthCARE](https://earth.esa.int/eogateway/missions/earthcare) satellite data

## Installation

```bash
python3 -m pip install earthcare-downloader
```

## Usage

### Authentication

Store your [ESA EO Sign In](https://eoiam-idp.eo.esa.int/) credentials in the environment variables `ESA_EO_USERNAME` and `ESA_EO_PASSWORD`.
If these variables are not set, the program will prompt you to enter your credentials.

### Running the tool

```
earthcare-downloader --lat LAT --lon LON -p PRODUCT [options]
```

where options are:

| Argument              | Description                                                      |
| --------------------- | ---------------------------------------------------------------- |
| `-h`, `--help`        | Show help message and exit.                                      |
| `--lat LAT`           | Latitude of the target location.                                 |
| `--lon LON`           | Longitude of the target location.                                |
| `-p`, `--product`     | Product type to download (see full list below).                  |
| `-d`, `--distance`    | Search radius around the location in km (default: **200**).      |
| `--start`             | Start date (YYYY-MM-DD).                                         |
| `--stop`              | Stop date (YYYY-MM-DD).                                          |
| `--orbit_min`         | Minimum orbit number (default: 0).                               |
| `--orbit_max`         | Maximum orbit number (default: infinite).                        |
| `-o`, `--output_path` | Directory to save downloaded files (default: current directory). |
| `--max_workers`       | Maximum number of concurrent downloads (default: **5**).         |
| `--show`              | Show filenames before downloading.                               |
| `--unzip`             | Automatically unzip downloaded files.                            |
| `--disable_progress`  | Hide progress bars during download.                              |
| `--no_prompt`         | Skip confirmation prompt before downloading.                     |

Available products:

| Level        | Product Code   | Description                                      |
| ------------ | -------------- | ------------------------------------------------ |
| **Level 1**  | ATL_NOM_1B     | ATLID Nominal Mode                               |
|              | AUX_JSG_1D     | Auxiliary Joint Standard Grid                    |
|              | BBR_NOM_1B     | Broadband Radiometer Nominal Mode                |
|              | BBR_SNG_1B     | Broadband Radiometer Single View                 |
|              | CPR_NOM_1B     | Cloud Profiling Radar Nominal Mode               |
|              | MSI_NOM_1B     | Multi-Spectral Imager Nominal Mode               |
|              | MSI_RGR_1C     | Multi-Spectral Imager Re-Gridded                 |
| **Level 2A** | ATL_ALD_2A     | ATLID Aerosol Layer Descriptors                  |
|              | ATL_ARE_2A     | ATLID Aerosol Parameters                         |
|              | ATL_CTH_2A     | ATLID Cloud Top Height                           |
|              | ATL_EBD_2A     | ATLID Extinction, Backscatter and Depolarization |
|              | ATL_FM\_\_2A   | ATLID Feature Mask                               |
|              | ATL_ICE_2A     | ATLID Ice Water Content                          |
|              | ATL_TC\_\_2A   | ATLID Target Classification                      |
|              | CPR_CD\_\_2A   | CPR Cloud Droplet                                |
|              | CPR_CLD_2A     | CPR Cloud Parameters                             |
|              | CPR_FMR_2A     | CPR Feature Mask and Reflectivity                |
|              | CPR_TC\_\_2A   | CPR Target Classification                        |
|              | MSI_AOT_2A     | MSI Aerosol Optical Thickness                    |
|              | MSI_CM\_\_2A   | MSI Cloud Mask                                   |
|              | MSI_COP_2A     | MSI Cloud Optical Properties                     |
| **Level 2B** | AC\_\_TC\_\_2B | ATLID-CPR Target Classification                  |
|              | AM\_\_ACD_2B   | ATLID-MSI Aerosol Column Descriptors             |
|              | AM\_\_CTH_2B   | ATLID-MSI Cloud Top Height                       |
|              | BM\_\_RAD_2B   | BBR-MSI Radiative Fluxes and Heating Rates       |

## Examples

Download all `CPR_NOM_1B` overpass data within 5 km of Hyytiälä, Finland:

```bash
earthcare-downloader --lat 61.844 --lon 24.287 --distance 5 --product CPR_NOM_1B
```

## License

MIT
