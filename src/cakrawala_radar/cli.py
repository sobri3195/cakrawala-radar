"""Command line interface for Cakrawala Radar."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .anomaly import AnomalyDetector
from .coverage import CoverageAnalyzer
from .dataset import generate_synthetic_dataset, load_tracks_csv, save_tracks_csv, tracks_to_dataframe
from .digital_twin import DigitalTwinAirspace
from .explainability import ExplainableAnomaly
from .fusion import MultiSensorFusion
from .radar import create_indonesia_demo_sensors
from .trajectory import TrajectorySimulator
from .visualization import plot_indonesia_demo, plot_trajectory

app = typer.Typer(help="Cakrawala Radar research and simulation toolkit.")
console = Console()


@app.command()
def version() -> None:
    """Print package version."""
    console.print(f"[bold]cakrawala-radar[/bold] {__version__}")


@app.command()
def simulate(
    objects: int = typer.Option(3, "--objects", help="Number of synthetic objects."),
    steps: int = typer.Option(20, "--steps", help="Route steps per object."),
    anomaly: bool = typer.Option(False, "--anomaly/--no-anomaly", help="Inject synthetic anomalies."),
    output: Optional[Path] = typer.Option(None, "--output", help="Optional output CSV path."),
) -> None:
    """Generate synthetic tracks."""
    sim = TrajectorySimulator()
    frames = []
    route_names = ["jakarta_natuna", "makassar_papua", "batam_pontianak", "ambon_sorong"]
    for idx in range(objects):
        track = sim.generate_archipelago_route(f"OBJ-{idx:03d}", route_names[idx % len(route_names)], steps=steps)
        anomaly_type = "none"
        label = "normal"
        if anomaly and idx == 0:
            anomaly_type = "sudden_heading_change"
            label = "anomaly"
            track = sim.inject_anomaly(track, anomaly_type)
        frames.append(tracks_to_dataframe(track, anomaly_label=label, anomaly_type=anomaly_type))
    frame = pd.concat(frames, ignore_index=True)
    if output:
        save_tracks_csv(frame, output)
    table = Table(title="Synthetic Simulation")
    table.add_column("Objects")
    table.add_column("Rows")
    table.add_column("Anomaly")
    table.add_column("Output")
    table.add_row(str(objects), str(len(frame)), str(anomaly), str(output or "-"))
    console.print(table)


@app.command()
def detect(
    input: Path = typer.Option(..., "--input", help="Input track CSV."),
    output: Optional[Path] = typer.Option(None, "--output", help="Optional JSON or CSV output path."),
    explain: bool = typer.Option(False, "--explain/--no-explain", help="Include explanations."),
) -> None:
    """Detect anomalies in a synthetic track CSV."""
    frame = load_tracks_csv(input)
    detector = AnomalyDetector()
    explainer = ExplainableAnomaly()
    results = []
    for object_id, group in frame.groupby("object_id"):
        track = _frame_to_air_objects(group)
        result = detector.detect(track)
        row = {
            "object_id": object_id,
            "score": result.anomaly_score,
            "label": result.label,
            "reasons": "; ".join(result.reasons),
            "recommended_action": result.recommended_action,
        }
        if explain:
            row["explanation"] = explainer.generate_human_readable_summary(result, track)
        results.append(row)
    if output:
        if output.suffix.lower() == ".csv":
            pd.DataFrame(results).to_csv(output, index=False)
        else:
            output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    table = Table(title="Anomaly Detection")
    table.add_column("Object")
    table.add_column("Score")
    table.add_column("Label")
    for result in results:
        table.add_row(str(result["object_id"]), f"{result['score']:.3f}", str(result["label"]))
    console.print(table)


@app.command("coverage-demo")
def coverage_demo(plot: bool = typer.Option(False, "--plot/--no-plot", help="Show matplotlib plot.")) -> None:
    """Run a simple Indonesia coverage demo."""
    sensors = create_indonesia_demo_sensors()
    analyzer = CoverageAnalyzer(sensors)
    sim = TrajectorySimulator()
    route = sim.generate_archipelago_route("OBJ-COV", "jakarta_natuna", steps=20)
    result = analyzer.compute_route_coverage(route)
    table = Table(title="Coverage Demo")
    table.add_column("Sensors")
    table.add_column("Coverage Ratio")
    table.add_column("Low Segments")
    table.add_row(str(len(sensors)), f"{result.coverage_ratio:.2f}", str(len(result.low_coverage_segments)))
    console.print(table)
    if plot:
        plot_indonesia_demo()
        import matplotlib.pyplot as plt

        plt.show()


@app.command("fusion-demo")
def fusion_demo(plot: bool = typer.Option(False, "--plot/--no-plot", help="Show matplotlib plot.")) -> None:
    """Run a multi-sensor fusion demo."""
    sensors = create_indonesia_demo_sensors()
    sim = TrajectorySimulator()
    track = sim.generate_archipelago_route("OBJ-FUS", "jakarta_natuna", steps=8)
    observations = sim.simulate_sensor_observations(track, sensors)
    fused = MultiSensorFusion().fuse_observations(observations)
    table = Table(title="Fusion Demo")
    table.add_column("Observations")
    table.add_column("Fused Tracks")
    table.add_column("Sources")
    table.add_row(str(len(observations)), str(len(fused)), ", ".join(fused[0].sources) if fused else "-")
    console.print(table)
    if plot:
        plot_trajectory(track)
        import matplotlib.pyplot as plt

        plt.show()


@app.command("digital-twin-demo")
def digital_twin_demo(
    steps: int = typer.Option(10, "--steps", help="Simulation steps."),
    plot: bool = typer.Option(False, "--plot/--no-plot", help="Show matplotlib plot."),
) -> None:
    """Run a digital twin demo."""
    sim = TrajectorySimulator()
    twin = DigitalTwinAirspace(
        sensors=create_indonesia_demo_sensors(),
        routes={"OBJ-TWIN": sim.generate_archipelago_route("OBJ-TWIN", "ambon_sorong", steps=steps)},
    )
    states = twin.run(steps)
    table = Table(title="Digital Twin Demo")
    table.add_column("Scenario")
    table.add_column("Emitted States")
    table.add_column("Simulation Time")
    table.add_row(twin.scenario_name, str(len(states)), str(twin.simulation_time))
    console.print(table)
    if plot:
        plot_trajectory(twin.routes["OBJ-TWIN"])
        import matplotlib.pyplot as plt

        plt.show()


@app.command("generate-dataset")
def generate_dataset(
    samples: int = typer.Option(100, "--samples", help="Number of synthetic route samples."),
    anomaly_ratio: float = typer.Option(0.2, "--anomaly-ratio", help="Fraction of anomalous samples."),
    output: Path = typer.Option(Path("cakrawala_dataset.csv"), "--output", help="Output CSV path."),
) -> None:
    """Generate a labeled synthetic dataset."""
    frame = generate_synthetic_dataset(samples=samples, anomaly_ratio=anomaly_ratio)
    frame.to_csv(output, index=False)
    table = Table(title="Generated Dataset")
    table.add_column("Rows")
    table.add_column("Samples")
    table.add_column("Output")
    table.add_row(str(len(frame)), str(samples), str(output))
    console.print(table)


def _frame_to_air_objects(frame: pd.DataFrame):
    from .models import AirObject

    def parse_bool(value) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "y"}
        return bool(value)

    objects = []
    for _, row in frame.sort_values("timestamp").iterrows():
        timestamp = pd.to_datetime(row.get("timestamp"), utc=True).to_pydatetime()
        objects.append(
            AirObject(
                object_id=str(row["object_id"]),
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                altitude_m=float(row["altitude_m"]),
                speed_mps=float(row["speed_mps"]),
                heading_deg=float(row["heading_deg"]),
                timestamp=timestamp,
                has_transponder=parse_bool(row.get("has_transponder", True)),
            )
        )
    return objects


if __name__ == "__main__":
    app()
