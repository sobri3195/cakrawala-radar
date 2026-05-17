"""Radar convenience exports and demo sensor factories."""

from __future__ import annotations

from typing import List

from .sensors import PassiveSensor, PrimaryRadarSensor, RadarSensor, SecondaryRadarSensor


def create_indonesia_demo_sensors() -> List[RadarSensor]:
    """Return a small synthetic sensor set around public city coordinates."""
    return [
        PrimaryRadarSensor("RDR-JKT-001", "Jakarta Synthetic Primary", -6.2088, 106.8456, 420, 0, 16000),
        SecondaryRadarSensor("SSR-BTM-001", "Batam Synthetic Secondary", 1.1301, 104.0529, 380, 0, 16000),
        PrimaryRadarSensor("RDR-MKS-001", "Makassar Synthetic Primary", -5.1477, 119.4327, 450, 0, 17000),
        PassiveSensor("PAS-AMB-001", "Ambon Public-like Passive", -3.6554, 128.1908, 360, 0, 14000),
    ]


__all__ = ["RadarSensor", "PrimaryRadarSensor", "SecondaryRadarSensor", "PassiveSensor", "create_indonesia_demo_sensors"]
