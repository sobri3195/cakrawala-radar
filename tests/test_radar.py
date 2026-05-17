from cakrawala_radar import AirObject, RadarSensor


def test_radar_observation_created_in_range():
    sensor = RadarSensor("R1", "Radar", -6.2, 106.8, 350, 0, 15000, noise_std=0.0)
    obj = AirObject("OBJ", -5.9, 107.0, 9000, 220, 45)

    observation = sensor.observe(obj)

    assert observation is not None
    assert observation.object_id == "OBJ"
    assert observation.confidence > 0
