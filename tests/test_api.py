import datetime

from earthcare_downloader import search
from earthcare_downloader.products import VALID_PRODUCTS


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
