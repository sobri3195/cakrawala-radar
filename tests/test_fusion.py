from cakrawala_radar import MultiSensorFusion, RadarObservation


def test_weighted_average_fusion():
    observations = [
        RadarObservation("A", "OBJ", -6.0, 106.0, 9000, 220, 40, confidence=0.8),
        RadarObservation("B", "OBJ", -4.0, 108.0, 11000, 240, 60, confidence=0.2),
    ]

    fused = MultiSensorFusion().confidence_weighted_fusion(observations)

    assert fused.object_id == "OBJ"
    assert fused.latitude < -5.0
    assert fused.confidence > 0.5
