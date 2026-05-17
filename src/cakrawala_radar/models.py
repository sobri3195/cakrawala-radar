"""Lightweight data models used by the package."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .geospatial import bearing_deg, haversine_distance_km


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


@dataclass
class GeoPoint:
    """Geographic point with optional altitude."""

    latitude: float
    longitude: float
    altitude_m: Optional[float] = None

    def distance_to(self, other: "GeoPoint") -> float:
        """Return haversine distance to another point in kilometers."""
        return haversine_distance_km(self.latitude, self.longitude, other.latitude, other.longitude)

    def bearing_to(self, other: "GeoPoint") -> float:
        """Return initial bearing to another point in degrees."""
        return bearing_deg(self.latitude, self.longitude, other.latitude, other.longitude)


@dataclass
class AirObject:
    """Synthetic air object state used for simulation and research."""

    object_id: str
    latitude: float
    longitude: float
    altitude_m: float
    speed_mps: float
    heading_deg: float
    timestamp: datetime = field(default_factory=utc_now)
    callsign: Optional[str] = None
    has_transponder: bool = True
    object_type: str = "unknown"

    def position(self) -> GeoPoint:
        """Return current object position."""
        return GeoPoint(self.latitude, self.longitude, self.altitude_m)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a plain dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class RadarObservation:
    """Noisy radar-like observation of an air object."""

    sensor_id: str
    object_id: str
    measured_latitude: float
    measured_longitude: float
    measured_altitude_m: float
    measured_speed_mps: float
    measured_heading_deg: float
    timestamp: datetime = field(default_factory=utc_now)
    confidence: float = 1.0
    noise_level: float = 0.0


@dataclass
class ADSBMessage:
    """Synthetic or public-like ADS-B message model."""

    icao24: str
    callsign: Optional[str]
    latitude: float
    longitude: float
    altitude_m: float
    ground_speed_mps: float
    track_deg: float
    timestamp: datetime = field(default_factory=utc_now)


@dataclass
class SensorTrack:
    """Track produced by one sensor over time."""

    track_id: str
    sensor_id: str
    object_id: str
    observations: List[RadarObservation] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class FusedTrack:
    """Result of combining observations from one or more sensors."""

    track_id: str
    object_id: str
    latitude: float
    longitude: float
    altitude_m: float
    speed_mps: float
    heading_deg: float
    confidence: float
    sources: List[str]
    timestamp: datetime = field(default_factory=utc_now)

    def position(self) -> GeoPoint:
        """Return current fused position."""
        return GeoPoint(self.latitude, self.longitude, self.altitude_m)


@dataclass
class AnomalyResult:
    """Explainable anomaly scoring output."""

    object_id: str
    anomaly_score: float
    label: str
    reasons: List[str] = field(default_factory=list)
    recommended_action: str = "review track history"


@dataclass
class CoverageResult:
    """Coverage result for a point or route segment."""

    covered: bool
    coverage_count: int
    covering_sensors: List[str]
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude_m: Optional[float] = None
    coverage_ratio: Optional[float] = None
    low_coverage_segments: List[int] = field(default_factory=list)


@dataclass
class WeatherCondition:
    """Simple tropical-weather condition model."""

    visibility_km: float = 20.0
    rain_intensity: float = 0.0
    wind_speed_mps: float = 0.0
    cloud_density: float = 0.0
    interference_factor: float = 0.0


@dataclass
class DigitalTwinScenario:
    """Serializable digital twin scenario description."""

    scenario_name: str
    sensors: List[Dict[str, Any]] = field(default_factory=list)
    air_objects: List[Dict[str, Any]] = field(default_factory=list)
    routes: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    weather: Dict[str, Any] = field(default_factory=dict)
    simulation_time: int = 0
