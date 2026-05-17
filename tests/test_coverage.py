from cakrawala_radar import CoverageAnalyzer, RadarSensor, TrajectorySimulator


def test_route_coverage_result():
    sensor = RadarSensor("R1", "Radar", -6.2, 106.8, 500, 0, 15000)
    route = TrajectorySimulator().generate_linear_route("OBJ", (-6.2, 106.8), (-5.8, 107.1), steps=5)
    result = CoverageAnalyzer([sensor]).compute_route_coverage(route)

    assert result.coverage_ratio == 1.0
    assert result.coverage_count == 1
