from cakrawala_radar import AirObject, RadarSensor


sensor = RadarSensor(
    sensor_id="RDR-JKT-001",
    name="Jakarta Synthetic Radar",
    latitude=-6.2,
    longitude=106.8,
    coverage_radius_km=350,
    min_altitude_m=0,
    max_altitude_m=15000,
)

obj = AirObject(
    object_id="OBJ-001",
    latitude=-5.8,
    longitude=107.1,
    altitude_m=10000,
    speed_mps=230,
    heading_deg=45,
    has_transponder=False,
)

print("Can detect:", sensor.can_detect(obj))
print("Observation:", sensor.observe(obj))
