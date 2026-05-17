"""Shared constants for Cakrawala Radar."""

EARTH_RADIUS_KM = 6371.0088
DEFAULT_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

INDONESIA_CITY_COORDINATES = {
    "jakarta": (-6.2088, 106.8456),
    "natuna": (3.9500, 108.3833),
    "makassar": (-5.1477, 119.4327),
    "papua": (-2.5489, 140.7181),
    "batam": (1.1301, 104.0529),
    "pontianak": (-0.0263, 109.3425),
    "ambon": (-3.6554, 128.1908),
    "sorong": (-0.8762, 131.2569),
    "surabaya": (-7.2575, 112.7521),
    "balikpapan": (-1.2379, 116.8529),
}

SAFE_RECOMMENDED_ACTIONS = [
    "review track history",
    "request additional sensor confirmation",
    "validate data quality",
    "increase confidence with the next observation",
]
