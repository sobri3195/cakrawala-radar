from cakrawala_radar import AnomalyDetector, TrajectorySimulator


def test_anomaly_scoring_high_heading_change():
    sim = TrajectorySimulator()
    track = sim.generate_linear_route("OBJ", (-6.2, 106.8), (-5.2, 107.8), steps=6)
    track = sim.simulate_heading_change(track, index=3, delta_deg=110)

    result = AnomalyDetector().detect(track)

    assert result.label in {"suspicious", "high_anomaly"}
    assert result.anomaly_score >= 0.4


def test_archipelago_route_is_not_route_deviation_by_default():
    sim = TrajectorySimulator()
    track = sim.generate_archipelago_route("OBJ-NORMAL", "jakarta_natuna", steps=8)

    result = AnomalyDetector().detect(track)

    assert result.label == "normal"
