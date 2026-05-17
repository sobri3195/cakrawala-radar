"""Trajectory generation and anomaly injection for synthetic routes."""

from __future__ import annotations

import math
import random
from datetime import timedelta
from typing import Iterable, List, Sequence, Tuple

from .constants import INDONESIA_CITY_COORDINATES
from .geospatial import bearing_deg, destination_point, interpolate_route
from .models import AirObject, RadarObservation, utc_now
from .sensors import RadarSensor


class TrajectorySimulator:
    """Generate synthetic air-object trajectories for education and research."""

    def __init__(self, seed: int = 42) -> None:
        self.random = random.Random(seed)

    def _objects_from_points(
        self,
        object_id: str,
        points: Sequence[Tuple[float, float]],
        altitude_m: float = 9000.0,
        speed_mps: float = 230.0,
        has_transponder: bool = True,
    ) -> List[AirObject]:
        timestamp = utc_now()
        objects: List[AirObject] = []
        for idx, (lat, lon) in enumerate(points):
            if idx < len(points) - 1:
                heading = bearing_deg(lat, lon, points[idx + 1][0], points[idx + 1][1])
            elif objects:
                heading = objects[-1].heading_deg
            else:
                heading = 0.0
            objects.append(
                AirObject(
                    object_id=object_id,
                    latitude=lat,
                    longitude=lon,
                    altitude_m=altitude_m,
                    speed_mps=speed_mps,
                    heading_deg=heading,
                    timestamp=timestamp + timedelta(seconds=idx * 60),
                    callsign=f"CKR{object_id[-3:]}",
                    has_transponder=has_transponder,
                    object_type="synthetic",
                )
            )
        return objects

    def generate_linear_route(
        self,
        object_id: str,
        start: Tuple[float, float],
        end: Tuple[float, float],
        steps: int = 20,
        altitude_m: float = 9000.0,
        speed_mps: float = 230.0,
    ) -> List[AirObject]:
        """Generate a straight synthetic route."""
        steps = max(2, steps)
        points = interpolate_route([start, end], steps_per_segment=steps - 1)
        return self._objects_from_points(object_id, points, altitude_m, speed_mps)

    def generate_curved_route(
        self,
        object_id: str,
        start: Tuple[float, float],
        end: Tuple[float, float],
        steps: int = 20,
        curve_strength: float = 0.8,
    ) -> List[AirObject]:
        """Generate a simple sinusoidal route between two points."""
        steps = max(2, steps)
        points: List[Tuple[float, float]] = []
        for idx in range(steps):
            fraction = idx / (steps - 1)
            lat = start[0] + (end[0] - start[0]) * fraction
            lon = start[1] + (end[1] - start[1]) * fraction
            offset = math.sin(math.pi * fraction) * curve_strength
            points.append((lat + offset * 0.2, lon + offset * 0.2))
        return self._objects_from_points(object_id, points)

    def generate_random_patrol_like_route(
        self,
        object_id: str,
        center: Tuple[float, float] = (-6.2, 106.8),
        radius_km: float = 100,
        steps: int = 20,
    ) -> List[AirObject]:
        """Generate a non-tactical random loiter-like route for simulation."""
        points = [
            destination_point(
                center[0],
                center[1],
                self.random.uniform(0, 360),
                self.random.uniform(radius_km * 0.2, radius_km),
            )
            for _ in range(max(2, steps))
        ]
        return self._objects_from_points(object_id, points)

    def generate_archipelago_route(
        self,
        object_id: str,
        route_name: str = "jakarta_natuna",
        steps: int = 20,
    ) -> List[AirObject]:
        """Generate one of several public-coordinate Indonesia demo routes."""
        routes = {
            "jakarta_natuna": ["jakarta", "natuna"],
            "makassar_papua": ["makassar", "papua"],
            "batam_pontianak": ["batam", "pontianak"],
            "ambon_sorong": ["ambon", "sorong"],
        }
        names = routes.get(route_name.lower())
        if names is None:
            raise ValueError(f"unknown route_name {route_name!r}")
        base_points = [INDONESIA_CITY_COORDINATES[name] for name in names]
        points = interpolate_route(base_points, steps_per_segment=max(1, steps - 1))
        return self._objects_from_points(object_id, points)

    def inject_anomaly(
        self,
        track: List[AirObject],
        anomaly_type: str,
        index: int | None = None,
    ) -> List[AirObject]:
        """Inject a supported synthetic anomaly into a copied track."""
        if anomaly_type == "sudden_heading_change":
            return self.simulate_heading_change(track, index=index, delta_deg=90)
        if anomaly_type == "altitude_inconsistency":
            return self.simulate_altitude_jump(track, index=index, delta_m=2500)
        if anomaly_type == "speed_spike":
            return self.simulate_speed_spike(track, index=index, multiplier=1.8)
        if anomaly_type == "sensor_dropout":
            return self.simulate_dropout(track, start=index, length=2)
        if anomaly_type == "missing_transponder":
            return self.simulate_unidentified_object(track, start=index)
        if anomaly_type == "unusual_route_deviation":
            copied = list(track)
            idx = self._safe_index(copied, index)
            copied[idx] = self._replace_position(copied[idx], copied[idx].latitude + 1.0, copied[idx].longitude + 1.0)
            return copied
        return list(track)

    def _safe_index(self, track: Sequence[AirObject], index: int | None) -> int:
        if not track:
            raise ValueError("track must not be empty")
        if index is None:
            return max(0, len(track) // 2)
        return max(0, min(len(track) - 1, index))

    def _replace_position(self, obj: AirObject, latitude: float, longitude: float) -> AirObject:
        return AirObject(
            obj.object_id,
            latitude,
            longitude,
            obj.altitude_m,
            obj.speed_mps,
            obj.heading_deg,
            obj.timestamp,
            obj.callsign,
            obj.has_transponder,
            obj.object_type,
        )

    def simulate_dropout(
        self,
        track: List[AirObject],
        start: int | None = None,
        length: int = 2,
    ) -> List[AirObject]:
        """Remove a short interval to simulate missing observations."""
        idx = self._safe_index(track, start)
        return [obj for i, obj in enumerate(track) if not idx <= i < idx + max(1, length)]

    def simulate_heading_change(
        self,
        track: List[AirObject],
        index: int | None = None,
        delta_deg: float = 90.0,
    ) -> List[AirObject]:
        """Inject a sudden heading change at one point."""
        copied = list(track)
        idx = self._safe_index(copied, index)
        obj = copied[idx]
        copied[idx] = AirObject(
            obj.object_id,
            obj.latitude,
            obj.longitude,
            obj.altitude_m,
            obj.speed_mps,
            (obj.heading_deg + delta_deg) % 360,
            obj.timestamp,
            obj.callsign,
            obj.has_transponder,
            obj.object_type,
        )
        return copied

    def simulate_altitude_jump(
        self,
        track: List[AirObject],
        index: int | None = None,
        delta_m: float = 2000.0,
    ) -> List[AirObject]:
        """Inject an abrupt altitude jump."""
        copied = list(track)
        idx = self._safe_index(copied, index)
        obj = copied[idx]
        copied[idx] = AirObject(
            obj.object_id,
            obj.latitude,
            obj.longitude,
            max(0.0, obj.altitude_m + delta_m),
            obj.speed_mps,
            obj.heading_deg,
            obj.timestamp,
            obj.callsign,
            obj.has_transponder,
            obj.object_type,
        )
        return copied

    def simulate_unidentified_object(
        self,
        track: List[AirObject],
        start: int | None = None,
    ) -> List[AirObject]:
        """Remove transponder/callsign identity from track points after start."""
        idx = self._safe_index(track, start)
        copied: List[AirObject] = []
        for i, obj in enumerate(track):
            copied.append(
                AirObject(
                    obj.object_id,
                    obj.latitude,
                    obj.longitude,
                    obj.altitude_m,
                    obj.speed_mps,
                    obj.heading_deg,
                    obj.timestamp,
                    None if i >= idx else obj.callsign,
                    False if i >= idx else obj.has_transponder,
                    obj.object_type,
                )
            )
        return copied

    def simulate_speed_spike(
        self,
        track: List[AirObject],
        index: int | None = None,
        multiplier: float = 1.6,
    ) -> List[AirObject]:
        """Inject a sudden speed spike."""
        copied = list(track)
        idx = self._safe_index(copied, index)
        obj = copied[idx]
        copied[idx] = AirObject(
            obj.object_id,
            obj.latitude,
            obj.longitude,
            obj.altitude_m,
            obj.speed_mps * multiplier,
            obj.heading_deg,
            obj.timestamp,
            obj.callsign,
            obj.has_transponder,
            obj.object_type,
        )
        return copied

    def simulate_sensor_observations(
        self,
        track: Iterable[AirObject],
        sensors: Iterable[RadarSensor],
    ) -> List[RadarObservation]:
        """Generate observations from all sensors for a synthetic track."""
        observations: List[RadarObservation] = []
        for obj in track:
            for sensor in sensors:
                observation = sensor.observe(obj)
                if observation is not None:
                    observations.append(observation)
        return observations
