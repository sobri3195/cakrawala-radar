from cakrawala_radar import TrajectorySimulator
from cakrawala_radar.digital_twin import DigitalTwinAirspace
from cakrawala_radar.radar import create_indonesia_demo_sensors


sim = TrajectorySimulator()
twin = DigitalTwinAirspace(
    sensors=create_indonesia_demo_sensors(),
    routes={"OBJ-TWIN": sim.generate_archipelago_route("OBJ-TWIN", "jakarta_natuna", steps=10)},
)

print(twin.run(steps=3))
print(twin.summarize())
