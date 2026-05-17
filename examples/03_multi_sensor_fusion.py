from cakrawala_radar import MultiSensorFusion, TrajectorySimulator
from cakrawala_radar.radar import create_indonesia_demo_sensors


sim = TrajectorySimulator()
sensors = create_indonesia_demo_sensors()
track = sim.generate_archipelago_route("OBJ-FUSION", "jakarta_natuna", steps=8)
observations = sim.simulate_sensor_observations(track, sensors)
fused = MultiSensorFusion().fuse_observations(observations)

print(f"observations={len(observations)}")
print(fused)
