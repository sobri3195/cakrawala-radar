"""Matplotlib visualizations for synthetic airspace data."""

from __future__ import annotations

from typing import Iterable, Sequence

import matplotlib.pyplot as plt

from .coverage import CoverageAnalyzer
from .models import AirObject, AnomalyResult, FusedTrack, RadarObservation
from .radar import create_indonesia_demo_sensors
from .sensors import RadarSensor
from .trajectory import TrajectorySimulator


def plot_sensors(sensors: Iterable[RadarSensor]):
    """Plot sensor points with labels."""
    fig, ax = plt.subplots()
    for sensor in sensors:
        ax.scatter(sensor.longitude, sensor.latitude, marker="^", label=sensor.sensor_id)
        ax.text(sensor.longitude, sensor.latitude, sensor.sensor_id)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Synthetic Sensor Locations")
    ax.grid(True, alpha=0.3)
    return fig, ax


def plot_trajectory(track: Sequence[AirObject]):
    """Plot a synthetic trajectory."""
    fig, ax = plt.subplots()
    ax.plot([obj.longitude for obj in track], [obj.latitude for obj in track], marker="o")
    for obj in track[:: max(1, len(track) // 5)]:
        ax.text(obj.longitude, obj.latitude, obj.object_id)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Synthetic Trajectory")
    ax.grid(True, alpha=0.3)
    return fig, ax


def plot_observations(observations: Sequence[RadarObservation]):
    """Plot radar observations."""
    fig, ax = plt.subplots()
    ax.scatter(
        [obs.measured_longitude for obs in observations],
        [obs.measured_latitude for obs in observations],
        c=[obs.confidence for obs in observations],
        cmap="viridis",
    )
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Synthetic Radar Observations")
    ax.grid(True, alpha=0.3)
    return fig, ax


def plot_fused_tracks(tracks: Sequence[FusedTrack]):
    """Plot fused tracks."""
    fig, ax = plt.subplots()
    ax.scatter([track.longitude for track in tracks], [track.latitude for track in tracks], marker="x")
    for track in tracks:
        ax.text(track.longitude, track.latitude, track.track_id)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Fused Tracks")
    ax.grid(True, alpha=0.3)
    return fig, ax


def plot_anomaly_scores(results: Sequence[AnomalyResult]):
    """Plot anomaly scores by object id."""
    fig, ax = plt.subplots()
    ax.bar([result.object_id for result in results], [result.anomaly_score for result in results])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Anomaly Score")
    ax.set_title("Anomaly Scores")
    return fig, ax


def plot_coverage_grid(results):
    """Plot grid coverage results."""
    fig, ax = plt.subplots()
    scatter = ax.scatter(
        [result.longitude for result in results],
        [result.latitude for result in results],
        c=[result.coverage_count for result in results],
        cmap="plasma",
    )
    fig.colorbar(scatter, ax=ax, label="Coverage Count")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Coverage Grid")
    ax.grid(True, alpha=0.3)
    return fig, ax


def plot_indonesia_demo():
    """Plot a small Indonesia-focused synthetic demo."""
    sensors = create_indonesia_demo_sensors()
    sim = TrajectorySimulator()
    track = sim.generate_archipelago_route("OBJ-DEMO", "jakarta_natuna", steps=20)
    analyzer = CoverageAnalyzer(sensors)
    grid = analyzer.estimate_coverage_grid(-8, 5, 103, 132, spacing_km=350)
    fig, ax = plot_coverage_grid(grid)
    for sensor in sensors:
        ax.scatter(sensor.longitude, sensor.latitude, marker="^", color="black")
        ax.text(sensor.longitude, sensor.latitude, sensor.sensor_id)
    ax.plot([obj.longitude for obj in track], [obj.latitude for obj in track], color="tab:blue")
    ax.set_title("Cakrawala Radar Indonesia Demo")
    return fig, ax
