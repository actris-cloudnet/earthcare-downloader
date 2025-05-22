# earthcare-downloader

[![CI](https://github.com/actris-cloudnet/earthcare-downloader/actions/workflows/test.yml/badge.svg)](https://github.com/actris-cloudnet/earthcare-downloader/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/earthcare-downloader.svg)](https://badge.fury.io/py/earthcare-downloader)

Python tool for downloading EarthCARE satellite data

## Installation

```bash
python3 -m pip install earthcare-downloader
```

## Usage

### Authentication

Store your [ESA EO Sign In](https://eoiam-idp.eo.esa.int/) credentials in the environment variables `ESA_EO_USERNAME` and `ESA_EO_PASSWORD`.
If these variables are not set, the program will prompt you to enter your credentials.

### Level 1B overpasses

```bash
earthcare-downloader [-h] --lat LAT --lon LON [--radius RADIUS]
[--product  {ATL_NOM_1B,AUX_JSG_1D,BBR_NOM_1B,BBR_SNG_1B,CPR_NOM_1B,MSI_NOM_1B MSI_RGR_1C}]
[--max_workers MAX_WORKERS] [--output_path OUTPUT_PATH]
```

For example, to download all `CPR_NOM_1B` overpass data within 5 km of Hyytiälä, Finland:

```bash
earthcare-downloader --lat 61.844 --lon 24.287 --radius 5 --product CPR_NOM_1B
```

## License

MIT
