"""Synthetic/public-like ADS-B utilities.

This module never performs automatic network calls. It accepts user-supplied
records and generates demo messages suitable for education and tests.
"""

from __future__ import annotations

import random
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from .models import ADSBMessage, AirObject, utc_now


def _parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return utc_now()


def generate_synthetic_adsb(
    count: int = 1,
    prefix: str = "CKR",
    start_latitude: float = -6.2,
    start_longitude: float = 106.8,
) -> List[ADSBMessage]:
    """Generate synthetic ADS-B messages near a configurable point."""
    messages: List[ADSBMessage] = []
    for idx in range(count):
        messages.append(
            ADSBMessage(
                icao24=f"{prefix}{idx:03X}",
                callsign=f"{prefix}{idx:03d}",
                latitude=start_latitude + random.uniform(-1.0, 1.0),
                longitude=start_longitude + random.uniform(-1.0, 1.0),
                altitude_m=random.uniform(3000, 12000),
                ground_speed_mps=random.uniform(160, 260),
                track_deg=random.uniform(0, 360),
                timestamp=utc_now(),
            )
        )
    return messages


def parse_adsb_like_dict(record: Dict[str, Any]) -> ADSBMessage:
    """Parse a dictionary with ADS-B-like fields into an ADSBMessage."""
    return ADSBMessage(
        icao24=str(record.get("icao24") or record.get("hex") or record.get("id") or "SIM000"),
        callsign=record.get("callsign"),
        latitude=float(record["latitude"]),
        longitude=float(record["longitude"]),
        altitude_m=float(record.get("altitude_m", record.get("altitude", 0.0))),
        ground_speed_mps=float(record.get("ground_speed_mps", record.get("speed_mps", 0.0))),
        track_deg=float(record.get("track_deg", record.get("heading_deg", 0.0))) % 360,
        timestamp=_parse_timestamp(record.get("timestamp")),
    )


def adsb_to_air_object(message: ADSBMessage, object_type: str = "adsb") -> AirObject:
    """Convert a synthetic ADS-B message into an AirObject."""
    return AirObject(
        object_id=message.icao24,
        latitude=message.latitude,
        longitude=message.longitude,
        altitude_m=message.altitude_m,
        speed_mps=message.ground_speed_mps,
        heading_deg=message.track_deg,
        timestamp=message.timestamp,
        callsign=message.callsign,
        has_transponder=True,
        object_type=object_type,
    )


def validate_adsb_message(message: ADSBMessage) -> bool:
    """Return True when message fields are in plausible ranges."""
    return (
        bool(message.icao24)
        and -90 <= message.latitude <= 90
        and -180 <= message.longitude <= 180
        and -500 <= message.altitude_m <= 25000
        and message.ground_speed_mps >= 0
        and 0 <= message.track_deg < 360
    )


def simulate_missing_adsb_identity(message: ADSBMessage) -> ADSBMessage:
    """Return a copy with callsign removed for identity-loss experiments."""
    return ADSBMessage(
        icao24=message.icao24,
        callsign=None,
        latitude=message.latitude,
        longitude=message.longitude,
        altitude_m=message.altitude_m,
        ground_speed_mps=message.ground_speed_mps,
        track_deg=message.track_deg,
        timestamp=message.timestamp,
    )


def simulate_adsb_dropout(
    messages: Iterable[ADSBMessage],
    dropout_probability: float = 0.2,
    seed: Optional[int] = None,
) -> List[ADSBMessage]:
    """Drop synthetic ADS-B messages with the requested probability."""
    rng = random.Random(seed)
    probability = max(0.0, min(1.0, dropout_probability))
    return [message for message in messages if rng.random() >= probability]
