import pytest

from earthcare_downloader import search

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
