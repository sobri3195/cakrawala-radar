from cakrawala_radar import AnomalyDetector, ExplainableAnomaly, TrajectorySimulator


sim = TrajectorySimulator()
track = sim.generate_archipelago_route("OBJ-XAI", "ambon_sorong", steps=12)
track = sim.simulate_unidentified_object(track, start=5)
result = AnomalyDetector().detect(track)
explanation = ExplainableAnomaly().explain(result, track)

print(explanation)
