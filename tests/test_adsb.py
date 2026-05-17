from cakrawala_radar.adsb import adsb_to_air_object, generate_synthetic_adsb, validate_adsb_message


def test_adsb_generation_and_conversion():
    message = generate_synthetic_adsb(count=1)[0]
    obj = adsb_to_air_object(message)

    assert validate_adsb_message(message)
    assert obj.object_id == message.icao24
    assert obj.has_transponder
