"""Radar coverage analysis using lightweight haversine calculations."""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

from .geospatial import km_to_degrees_approx
from .models import AirObject, CoverageResult
from .sensors import RadarSensor


class CoverageAnalyzer:
    """Analyze point, route, and grid coverage for synthetic sensors."""

    def __init__(self, sensors: Iterable[RadarSensor] | None = None) -> None:
        self.sensors: List[RadarSensor] = list(sensors or [])

    def add_sensor(self, sensor: RadarSensor) -> None:
        """Add a sensor to the analyzer."""
        self.sensors.append(sensor)

    def compute_point_coverage(
        self,
        latitude: float,
        longitude: float,
        altitude_m: float = 9000.0,
    ) -> CoverageResult:
        """Return coverage information for a point."""
        probe = AirObject("COVERAGE-PROBE", latitude, longitude, altitude_m, 0.0, 0.0)
        covering = [sensor.sensor_id for sensor in self.sensors if sensor.can_detect(probe)]
        return CoverageResult(
            covered=bool(covering),
            coverage_count=len(covering),
            covering_sensors=covering,
            latitude=latitude,
            longitude=longitude,
            altitude_m=altitude_m,
        )

    def compute_route_coverage(
        self,
        route: Sequence[AirObject | Tuple[float, float]],
        altitude_m: float = 9000.0,
    ) -> CoverageResult:
        """Compute fraction of route points covered by at least one sensor."""
        if not route:
            raise ValueError("route must not be empty")
        low_segments: List[int] = []
        covered_count = 0
        all_covering: set[str] = set()
        for idx, point in enumerate(route):
            if isinstance(point, AirObject):
                lat, lon, alt = point.latitude, point.longitude, point.altitude_m
            else:
                lat, lon, alt = point[0], point[1], altitude_m
            result = self.compute_point_coverage(lat, lon, alt)
            all_covering.update(result.covering_sensors)
            if result.covered:
                covered_count += 1
            else:
                low_segments.append(idx)
        ratio = covered_count / len(route)
        return CoverageResult(
            covered=ratio > 0,
            coverage_count=len(all_covering),
            covering_sensors=sorted(all_covering),
            coverage_ratio=ratio,
            low_coverage_segments=low_segments,
        )

    def estimate_coverage_grid(
        self,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
        spacing_km: float = 100.0,
        altitude_m: float = 9000.0,
    ) -> List[CoverageResult]:
        """Estimate coverage over a simple lat/lon grid."""
        spacing_deg = max(0.05, km_to_degrees_approx(spacing_km))
        results: List[CoverageResult] = []
        lat = lat_min
        while lat <= lat_max:
            lon = lon_min
            while lon <= lon_max:
                results.append(self.compute_point_coverage(lat, lon, altitude_m))
                lon += spacing_deg
            lat += spacing_deg
        return results

    def find_low_coverage_segments(
        self,
        route: Sequence[AirObject | Tuple[float, float]],
        min_sensors: int = 1,
    ) -> List[int]:
        """Return route indices covered by fewer than min_sensors."""
        indices: List[int] = []
        for idx, point in enumerate(route):
            if isinstance(point, AirObject):
                result = self.compute_point_coverage(point.latitude, point.longitude, point.altitude_m)
            else:
                result = self.compute_point_coverage(point[0], point[1])
            if result.coverage_count < min_sensors:
                indices.append(idx)
        return indices

    def summarize_coverage(self, route: Sequence[AirObject | Tuple[float, float]] | None = None) -> dict[str, object]:
        """Return a compact coverage summary."""
        summary = {"sensor_count": len(self.sensors), "sensor_ids": [sensor.sensor_id for sensor in self.sensors]}
        if route is not None:
            result = self.compute_route_coverage(route)
            summary.update({"route_coverage_ratio": result.coverage_ratio, "low_segments": result.low_coverage_segments})
        return summary
