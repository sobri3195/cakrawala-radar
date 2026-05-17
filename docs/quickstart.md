# Quickstart

```python
from cakrawala_radar import RadarSensor, AirObject

sensor = RadarSensor("RDR-JKT", "Jakarta Synthetic Radar", -6.2, 106.8, 350, 0, 15000)
obj = AirObject("OBJ-1", -5.8, 107.1, 10000, 230, 45)

print(sensor.can_detect(obj))
```

CLI:

```powershell
cakrawala-radar version
cakrawala-radar simulate --objects 2 --steps 10 --output demo.csv
```
