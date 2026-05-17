from cakrawala_radar import AirObject, PrimaryRadarSensor, SecondaryRadarSensor


def test_primary_radar_detects_without_transponder():
    sensor = PrimaryRadarSensor("P1", "Primary", -6.2, 106.8, 350, 0, 15000)
    obj = AirObject("OBJ", -5.9, 107.0, 9000, 220, 45, has_transponder=False)

    assert sensor.can_detect(obj)


def test_secondary_radar_requires_transponder():
    sensor = SecondaryRadarSensor("S1", "Secondary", -6.2, 106.8, 350, 0, 15000)
    obj = AirObject("OBJ", -5.9, 107.0, 9000, 220, 45, has_transponder=False)

    assert not sensor.can_detect(obj)
