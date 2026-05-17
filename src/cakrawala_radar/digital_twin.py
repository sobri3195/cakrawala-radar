"""Digital twin style synthetic airspace simulation."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

from .models import AirObject, DigitalTwinScenario, WeatherCondition
from .sensors import RadarSensor
from .trajectory import TrajectorySimulator
from .utils import read_json, write_json


class DigitalTwinAirspace:
    """A small synthetic airspace simulation container."""

    def __init__(
        self,
        scenario_name: str = "Cakrawala Synthetic Airspace",
        sensors: List[RadarSensor] | None = None,
        air_objects: List[AirObject] | None = None,
        routes: Dict[str, List[AirObject]] | None = None,
        weather: WeatherCondition | None = None,
        simulation_time: int = 0,
    ) -> None:
        self.scenario_name = scenario_name
        self.sensors = sensors or []
        self.air_objects = air_objects or []
        self.routes = routes or {}
        self.weather = weather or WeatherCondition()
        self.simulation_time = simulation_time

    def run(self, steps: int = 10) -> List[AirObject]:
        """Run a fixed number of steps and return emitted air-object states."""
        states: List[AirObject] = []
        for _ in range(steps):
            states.extend(self.step())
        return states

    def step(self) -> List[AirObject]:
        """Advance the simulation by one route index."""
        emitted: List[AirObject] = []
        for object_id, route in self.routes.items():
            if route:
                emitted.append(route[self.simulation_time % len(route)])
        self.air_objects = emitted
        self.simulation_time += 1
        return emitted

    def reset(self) -> None:
        """Reset simulation time and active objects."""
        self.simulation_time = 0
        self.air_objects = []

    def export_scenario_json(self, path: str | Path) -> None:
        """Export scenario metadata and routes to JSON."""
        scenario = DigitalTwinScenario(
            scenario_name=self.scenario_name,
            sensors=[sensor.summary() for sensor in self.sensors],
            air_objects=[obj.to_dict() for obj in self.air_objects],
            routes={key: [obj.to_dict() for obj in route] for key, route in self.routes.items()},
            weather=asdict(self.weather),
            simulation_time=self.simulation_time,
        )
        write_json(path, asdict(scenario))

    @classmethod
    def load_scenario_json(cls, path: str | Path) -> "DigitalTwinAirspace":
        """Load lightweight scenario metadata from JSON.

        Sensor objects are not reconstructed because JSON may come from external
        tools. Routes are regenerated as a safe demo route when only metadata is
        available.
        """
        data = read_json(path)
        sim = TrajectorySimulator()
        routes = {"OBJ-DEMO": sim.generate_archipelago_route("OBJ-DEMO", "jakarta_natuna", steps=10)}
        return cls(
            scenario_name=data.get("scenario_name", "Loaded Scenario"),
            routes=routes,
            weather=WeatherCondition(**data.get("weather", {})),
            simulation_time=int(data.get("simulation_time", 0)),
        )

    def summarize(self) -> Dict[str, object]:
        """Return a compact scenario summary."""
        return {
            "scenario_name": self.scenario_name,
            "sensor_count": len(self.sensors),
            "route_count": len(self.routes),
            "active_objects": len(self.air_objects),
            "simulation_time": self.simulation_time,
            "weather": asdict(self.weather),
        }
