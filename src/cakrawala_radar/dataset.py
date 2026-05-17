"""Dataset generation and CSV helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import pandas as pd

from .models import AirObject, RadarObservation
from .trajectory import TrajectorySimulator


TRACK_COLUMNS = [
    "object_id",
    "timestamp",
    "latitude",
    "longitude",
    "altitude_m",
    "speed_mps",
    "heading_deg",
    "has_transponder",
    "anomaly_label",
    "anomaly_type",
]


def tracks_to_dataframe(
    tracks: Iterable[AirObject],
    anomaly_label: str = "normal",
    anomaly_type: str = "none",
) -> pd.DataFrame:
    """Convert AirObject rows to a DataFrame."""
    return pd.DataFrame(
        [
            {
                "object_id": obj.object_id,
                "timestamp": obj.timestamp.isoformat(),
                "latitude": obj.latitude,
                "longitude": obj.longitude,
                "altitude_m": obj.altitude_m,
                "speed_mps": obj.speed_mps,
                "heading_deg": obj.heading_deg,
                "has_transponder": obj.has_transponder,
                "anomaly_label": anomaly_label,
                "anomaly_type": anomaly_type,
            }
            for obj in tracks
        ],
        columns=TRACK_COLUMNS,
    )


def generate_synthetic_dataset(samples: int = 100, anomaly_ratio: float = 0.1) -> pd.DataFrame:
    """Generate a labeled synthetic track dataset."""
    sim = TrajectorySimulator()
    frames: List[pd.DataFrame] = []
    route_names = ["jakarta_natuna", "makassar_papua", "batam_pontianak", "ambon_sorong"]
    samples = max(1, samples)
    anomaly_count = int(samples * max(0.0, min(1.0, anomaly_ratio)))
    for idx in range(samples):
        route = sim.generate_archipelago_route(f"OBJ-{idx:04d}", route_names[idx % len(route_names)], steps=8)
        if idx < anomaly_count:
            anomaly_type = ["sudden_heading_change", "speed_spike", "missing_transponder"][idx % 3]
            route = sim.inject_anomaly(route, anomaly_type)
            frames.append(tracks_to_dataframe(route, "anomaly", anomaly_type))
        else:
            frames.append(tracks_to_dataframe(route))
    return pd.concat(frames, ignore_index=True)


def save_tracks_csv(tracks: Iterable[AirObject] | pd.DataFrame, path: str | Path) -> None:
    """Save tracks to CSV."""
    frame = tracks if isinstance(tracks, pd.DataFrame) else tracks_to_dataframe(tracks)
    frame.to_csv(path, index=False)


def load_tracks_csv(path: str | Path) -> pd.DataFrame:
    """Load track CSV."""
    return pd.read_csv(path)


def save_observations_csv(observations: Iterable[RadarObservation], path: str | Path) -> None:
    """Save radar observations to CSV."""
    pd.DataFrame(
        [
            {
                "sensor_id": obs.sensor_id,
                "object_id": obs.object_id,
                "timestamp": obs.timestamp.isoformat(),
                "latitude": obs.measured_latitude,
                "longitude": obs.measured_longitude,
                "altitude_m": obs.measured_altitude_m,
                "speed_mps": obs.measured_speed_mps,
                "heading_deg": obs.measured_heading_deg,
                "confidence": obs.confidence,
                "noise_level": obs.noise_level,
            }
            for obs in observations
        ]
    ).to_csv(path, index=False)


def load_observations_csv(path: str | Path) -> pd.DataFrame:
    """Load radar observation CSV."""
    return pd.read_csv(path)


def train_test_split_tracks(
    frame: pd.DataFrame,
    test_size: float = 0.2,
    seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return random train/test split without adding a dependency."""
    shuffled = frame.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    split = int(len(shuffled) * (1.0 - max(0.0, min(1.0, test_size))))
    return shuffled.iloc[:split].copy(), shuffled.iloc[split:].copy()


def generate_labeled_anomaly_dataset(samples: int = 100, anomaly_ratio: float = 0.2) -> pd.DataFrame:
    """Alias for labeled synthetic anomaly dataset generation."""
    return generate_synthetic_dataset(samples=samples, anomaly_ratio=anomaly_ratio)
