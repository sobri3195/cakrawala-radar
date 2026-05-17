from cakrawala_radar.models import GeoPoint


def test_haversine_distance_and_bearing():
    jakarta = GeoPoint(-6.2088, 106.8456)
    bandung = GeoPoint(-6.9175, 107.6191)

    distance = jakarta.distance_to(bandung)
    bearing = jakarta.bearing_to(bandung)

    assert 110 < distance < 130
    assert 120 < bearing < 160
