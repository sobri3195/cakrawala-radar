from cakrawala_radar import AnomalyDetector, TrajectorySimulator


sim = TrajectorySimulator()
track = sim.generate_archipelago_route("OBJ-ANOM", "batam_pontianak", steps=12)
track = sim.inject_anomaly(track, "speed_spike", index=6)
result = AnomalyDetector().detect(track)

print(result)
