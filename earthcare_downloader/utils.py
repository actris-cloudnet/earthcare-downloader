import math


def distance_to_lat_deg(distance: float) -> float:
    return round(distance / 111.32, 3)


def distance_to_lon_deg(lat: float, distance: float) -> float:
    return round(distance / (111.32 * math.cos(math.radians(lat))), 3)
