"""Radar-style sensor models for synthetic airspace simulation."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, Optional

from .geospatial import bearing_deg, haversine_distance_km
from .models import AirObject, GeoPoint, RadarObservation


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


@dataclass
class RadarSensor:
    """Generic radar-like sensor for safe synthetic simulation."""

    sensor_id: str
    name: str
    latitude: float
    longitude: float
    coverage_radius_km: float
    min_altitude_m: float
    max_altitude_m: float
    azimuth_start_deg: float = 0.0
    azimuth_end_deg: float = 360.0
    sensor_type: str = "primary"
    reliability_score: float = 0.9
    noise_std: float = 0.01

    def position(self) -> GeoPoint:
        """Return the sensor location."""
        return GeoPoint(self.latitude, self.longitude, 0.0)

    def distance_to_object_km(self, air_object: AirObject) -> float:
        """Return distance to an air object."""
        return haversine_distance_km(
            self.latitude,
            self.longitude,
            air_object.latitude,
            air_object.longitude,
        )

    def is_in_range(self, air_object: AirObject) -> bool:
        """Return True when object is inside coverage radius."""
        return self.distance_to_object_km(air_object) <= self.coverage_radius_km

    def is_altitude_supported(self, air_object: AirObject) -> bool:
        """Return True when object altitude is inside sensor limits."""
        return self.min_altitude_m <= air_object.altitude_m <= self.max_altitude_m

    def is_in_azimuth_sector(self, air_object: AirObject) -> bool:
        """Return True when object bearing is inside configured azimuth sector."""
        if (self.azimuth_end_deg - self.azimuth_start_deg) % 360 == 0:
            return True
        bearing = bearing_deg(self.latitude, self.longitude, air_object.latitude, air_object.longitude)
        start = self.azimuth_start_deg % 360
        end = self.azimuth_end_deg % 360
        if start <= end:
            return start <= bearing <= end
        return bearing >= start or bearing <= end

    def can_detect(self, air_object: AirObject) -> bool:
        """Return True when the object is detectable in this synthetic model."""
        return (
            self.is_in_range(air_object)
            and self.is_altitude_supported(air_object)
            and self.is_in_azimuth_sector(air_object)
        )

    def confidence_for(self, air_object: AirObject) -> float:
        """Estimate observation confidence from distance, altitude, and reliability."""
        distance_ratio = self.distance_to_object_km(air_object) / max(self.coverage_radius_km, 1e-6)
        altitude_span = max(self.max_altitude_m - self.min_altitude_m, 1.0)
        altitude_mid = self.min_altitude_m + altitude_span / 2
        altitude_penalty = abs(air_object.altitude_m - altitude_mid) / altitude_span
        return _clamp(self.reliability_score * (1.0 - 0.55 * distance_ratio - 0.15 * altitude_penalty))

    def simulate_noise(self, value: float, std: Optional[float] = None) -> float:
        """Add Gaussian noise to a numeric value."""
        return value + random.gauss(0.0, self.noise_std if std is None else std)

    def observe(self, air_object: AirObject) -> Optional[RadarObservation]:
        """Return a synthetic radar observation, or None when not detectable."""
        if not self.can_detect(air_object):
            return None
        confidence = self.confidence_for(air_object)
        distance_noise = max(0.0001, self.noise_std)
        return RadarObservation(
            sensor_id=self.sensor_id,
            object_id=air_object.object_id,
            measured_latitude=self.simulate_noise(air_object.latitude, distance_noise),
            measured_longitude=self.simulate_noise(air_object.longitude, distance_noise),
            measured_altitude_m=self.simulate_noise(air_object.altitude_m, self.noise_std * 1000),
            measured_speed_mps=max(0.0, self.simulate_noise(air_object.speed_mps, self.noise_std * 50)),
            measured_heading_deg=self.simulate_noise(air_object.heading_deg, self.noise_std * 20) % 360,
            timestamp=air_object.timestamp,
            confidence=confidence,
            noise_level=self.noise_std,
        )

    def summary(self) -> Dict[str, float | str]:
        """Return sensor metadata suitable for tables or JSON."""
        return {
            "sensor_id": self.sensor_id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "coverage_radius_km": self.coverage_radius_km,
            "sensor_type": self.sensor_type,
            "reliability_score": self.reliability_score,
        }


@dataclass
class PrimaryRadarSensor(RadarSensor):
    """Primary radar-style sensor that can detect objects without transponders."""

    sensor_type: str = "primary"

    def confidence_for(self, air_object: AirObject) -> float:
        confidence = super().confidence_for(air_object)
        if not air_object.has_transponder:
            confidence *= 0.92
        return _clamp(confidence)


@dataclass
class SecondaryRadarSensor(RadarSensor):
    """Secondary radar-style sensor that strongly depends on transponder identity."""

    sensor_type: str = "secondary"

    def can_detect(self, air_object: AirObject) -> bool:
        return air_object.has_transponder and super().can_detect(air_object)

    def confidence_for(self, air_object: AirObject) -> float:
        identity_bonus = 0.12 if air_object.callsign or air_object.has_transponder else -0.4
        return _clamp(super().confidence_for(air_object) + identity_bonus)


@dataclass
class PassiveSensor(RadarSensor):
    """Conceptual non-emitting sensor for public-like/synthetic data fusion."""

    sensor_type: str = "passive"
    reliability_score: float = 0.75
    noise_std: float = 0.02

    def confidence_for(self, air_object: AirObject) -> float:
        confidence = super().confidence_for(air_object)
        if not air_object.has_transponder:
            confidence *= 0.55
        return _clamp(confidence)
