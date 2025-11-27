import datetime

import pytest

from earthcare_downloader import search
from earthcare_downloader.products import VALID_PRODUCTS

VALID_RANGE = (20.0, 30.0)
VALID_COORD = 25.0


@pytest.mark.parametrize(
    "lat, lon, lat_range, lon_range",
    [
        (VALID_COORD, None, None, None),
        (None, VALID_COORD, None, None),
        (95, VALID_COORD, None, None),
        (VALID_COORD, -190, None, None),
        (None, None, VALID_RANGE, None),
        (None, None, None, VALID_RANGE),
        (None, None, (-95, 10), VALID_RANGE),
        (None, None, (80, 92), VALID_RANGE),
        (None, None, VALID_RANGE, (170, 250)),
        (None, None, VALID_RANGE, (170, 100)),
        (VALID_COORD, VALID_COORD, VALID_RANGE, VALID_RANGE),
        (VALID_COORD, None, VALID_RANGE, VALID_RANGE),
        (None, VALID_COORD, VALID_RANGE, VALID_RANGE),
        (VALID_COORD, VALID_COORD, None, VALID_RANGE),
        (VALID_COORD, VALID_COORD, VALID_RANGE, None),
    ],
)
def test_invalid_coordinates(
    lat: float | None,
    lon: float | None,
    lat_range: tuple[float, float] | None,
    lon_range: tuple[float, float] | None,
):
    with pytest.raises(ValueError):
        search(
            product="CPR_TC__2A",
            lat=lat,
            lon=lon,
            lat_range=lat_range,
            lon_range=lon_range,
        )


def test_all_products_search():
    files = search(product=VALID_PRODUCTS, orbit=500)
    assert len(files) > 500


def test_date_search():
    date = datetime.date(2025, 1, 17)
    files = search(product="CPR_TC__2A", date=date)
    assert len(files) > 100
    for file in files:
        assert file.frame_start_time.date() == date


def test_lat_lon_search():
    date = datetime.date(2025, 1, 17)
    files = search(product="CPR_TC__2A", date=date, lat=52, lon=5, radius=100)
    assert len(files) == 1


def test_lat_lon_range_search():
    date = datetime.date(2025, 1, 17)
    files = search(
        product="CPR_TC__2A", date=date, lat_range=(50, 54), lon_range=(3, 7)
    )
    assert len(files) == 1


def test_start_and_stop():
    start = datetime.date(2025, 1, 17)
    stop = datetime.date(2025, 1, 19)
    files = search(product="CPR_TC__2A", start=start, stop=stop)
    assert len(files) > 300
    for file in files:
        assert start <= file.frame_start_time.date() <= stop
    dates_found = {file.frame_start_time.date() for file in files}
    assert start in dates_found
    assert stop in dates_found


def test_date_overrides_start_stop():
    start = datetime.date(2025, 1, 17)
    stop = datetime.date(2025, 1, 19)
    date = datetime.date(2025, 1, 18)
    files = search(product="CPR_TC__2A", start=start, stop=stop, date=date)
    for file in files:
        assert file.frame_start_time.date() == date
