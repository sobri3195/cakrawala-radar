"""Configuration helpers for Cakrawala Radar."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SimulationConfig:
    """Small configuration object for repeatable simulations."""

    random_seed: int = 42
    default_steps: int = 20
    default_objects: int = 3
    default_altitude_m: float = 9000.0
    default_speed_mps: float = 230.0
    safe_mode: bool = True


DEFAULT_CONFIG = SimulationConfig()
