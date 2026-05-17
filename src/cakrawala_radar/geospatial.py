"""Small geospatial helpers without heavy GIS dependencies."""

from __future__ import annotations

import math
from typing import Iterable, List, Sequence, Tuple

from .constants import EARTH_RADIUS_KM


def validate_lat_lon(latitude: float, longitude: float) -> None:
    """Raise ValueError when latitude or longitude is outside valid ranges."""
    if not -90.0 <= latitude <= 90.0:
        raise ValueError(f"latitude must be between -90 and 90, got {latitude}")
    if not -180.0 <= longitude <= 180.0:
        raise ValueError(f"longitude must be between -180 and 180, got {longitude}")


def normalize_longitude(longitude: float) -> float:
    """Normalize longitude to the [-180, 180] interval."""
    return ((longitude + 180.0) % 360.0) - 180.0


def haversine_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """Return great-circle distance in kilometers."""
    validate_lat_lon(lat1, lon1)
    validate_lat_lon(lat2, lon2)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return initial bearing from point one to point two in degrees."""
    validate_lat_lon(lat1, lon1)
    validate_lat_lon(lat2, lon2)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_lambda = math.radians(lon2 - lon1)
    y = math.sin(d_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(d_lambda)
    return (math.degrees(math.atan2(y, x)) + 360.0) % 360.0


def destination_point(
    latitude: float,
    longitude: float,
    bearing: float,
    distance_km: float,
) -> Tuple[float, float]:
    """Project a destination from a start point, bearing, and distance."""
    validate_lat_lon(latitude, longitude)
    angular_distance = distance_km / EARTH_RADIUS_KM
    theta = math.radians(bearing)
    phi1 = math.radians(latitude)
    lambda1 = math.radians(longitude)
    phi2 = math.asin(
        math.sin(phi1) * math.cos(angular_distance)
        + math.cos(phi1) * math.sin(angular_distance) * math.cos(theta)
    )
    lambda2 = lambda1 + math.atan2(
        math.sin(theta) * math.sin(angular_distance) * math.cos(phi1),
        math.cos(angular_distance) - math.sin(phi1) * math.sin(phi2),
    )
    return math.degrees(phi2), normalize_longitude(math.degrees(lambda2))


def interpolate_route(
    points: Sequence[Tuple[float, float]],
    steps_per_segment: int = 10,
) -> List[Tuple[float, float]]:
    """Linearly interpolate latitude/longitude waypoints."""
    if len(points) < 2:
        raise ValueError("at least two route points are required")
    if steps_per_segment < 1:
        raise ValueError("steps_per_segment must be >= 1")
    route: List[Tuple[float, float]] = []
    for start, end in zip(points[:-1], points[1:]):
        validate_lat_lon(*start)
        validate_lat_lon(*end)
        for idx in range(steps_per_segment):
            fraction = idx / steps_per_segment
            lat = start[0] + (end[0] - start[0]) * fraction
            lon = start[1] + (end[1] - start[1]) * fraction
            route.append((lat, normalize_longitude(lon)))
    route.append(points[-1])
    return route


def km_to_degrees_approx(km: float) -> float:
    """Approximate kilometers as latitude/longitude degrees near the equator."""
    return km / 111.32


def route_length_km(points: Iterable[Tuple[float, float]]) -> float:
    """Return total route length in kilometers."""
    total = 0.0
    previous = None
    for point in points:
        if previous is not None:
            total += haversine_distance_km(previous[0], previous[1], point[0], point[1])
        previous = point
    return total
