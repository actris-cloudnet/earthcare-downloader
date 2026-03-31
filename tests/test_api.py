import datetime

from earthcare_downloader import search
from earthcare_downloader.products import VALID_PRODUCTS


def test_all_products_search():
    files = search(product=VALID_PRODUCTS, orbit=3627)
    assert len(files) > 200


def test_date_search():
    date = datetime.date(2025, 1, 17)
    files = search(product="CPR_TC__2A", date=date)
    assert len(files) > 100


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


def test_date_overrides_start_stop():
    start = datetime.date(2025, 1, 17)
    stop = datetime.date(2025, 1, 19)
    date = datetime.date(2025, 1, 18)
    files = search(product="CPR_TC__2A", start=start, stop=stop, date=date)
    assert len(files) > 0
    assert len(files) < 200


def test_new_esa_l2_products():
    date = datetime.date(2025, 1, 17)
    files = search(product="ACM_CAP_2B,ACM_COM_2B,BMA_FLX_2B,ALL_3D__2B", date=date)
    products_found = {f.product for f in files}
    assert products_found == {"ACM_CAP_2B", "ACM_COM_2B", "BMA_FLX_2B", "ALL_3D__2B"}


def test_aux_data_products():
    date = datetime.date(2025, 1, 17)
    files = search(product="GEO_ATTOBS,GEO_ORBOBS,AUX_ORBRES", date=date)
    products_found = {f.product for f in files}
    assert "GEO_ATTOBS" in products_found
    assert "GEO_ORBOBS" in products_found


def test_met_data_search():
    date = datetime.date(2025, 1, 17)
    files = search(product="AUX_MET_1D", date=date)
    assert len(files) > 0
    assert all(f.product == "AUX_MET_1D" for f in files)
