"""A tiny Kalman-like smoother for educational track examples."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class SimpleKalmanFilter:
    """Minimal scalar-gain state smoother for lat/lon/altitude/velocity."""

    process_noise: float = 0.01
    measurement_noise: float = 0.1
    state: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    covariance: float = 1.0
    initialized: bool = False

    def reset(self) -> None:
        """Reset filter state."""
        self.state = [0.0, 0.0, 0.0, 0.0]
        self.covariance = 1.0
        self.initialized = False

    def predict(self) -> List[float]:
        """Predict the next state. This simple model keeps position constant."""
        self.covariance += self.process_noise
        return list(self.state)

    def update(self, measurement: List[float]) -> List[float]:
        """Update state with [latitude, longitude, altitude, velocity]."""
        if len(measurement) != 4:
            raise ValueError("measurement must contain four values")
        if not self.initialized:
            self.state = list(measurement)
            self.initialized = True
            return list(self.state)
        self.predict()
        gain = self.covariance / (self.covariance + self.measurement_noise)
        self.state = [
            state_value + gain * (measurement_value - state_value)
            for state_value, measurement_value in zip(self.state, measurement)
        ]
        self.covariance = (1 - gain) * self.covariance
        return list(self.state)
