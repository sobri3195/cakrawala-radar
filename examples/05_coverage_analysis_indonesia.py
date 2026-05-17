from cakrawala_radar import CoverageAnalyzer, TrajectorySimulator
from cakrawala_radar.radar import create_indonesia_demo_sensors


sensors = create_indonesia_demo_sensors()
route = TrajectorySimulator().generate_archipelago_route("OBJ-COV", "makassar_papua", steps=16)
result = CoverageAnalyzer(sensors).compute_route_coverage(route)

print(result)
