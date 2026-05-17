from cakrawala_radar import TrajectorySimulator


def test_trajectory_generation_and_anomaly():
    sim = TrajectorySimulator()
    track = sim.generate_archipelago_route("OBJ", "jakarta_natuna", steps=10)
    changed = sim.simulate_heading_change(track, index=5, delta_deg=90)

    assert len(track) == 10
    assert changed[5].heading_deg != track[5].heading_deg
