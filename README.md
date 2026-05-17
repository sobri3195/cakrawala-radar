# Cakrawala Radar

```text
   ____      _                         _       ____            _
  / ___|__ _| | ___ __ __ ___      __ / \     |  _ \ __ _  __| | __ _ _ __
 | |   / _` | |/ / '__/ _` \ \ /\ / // _ \    | |_) / _` |/ _` |/ _` | '__|
 | |__| (_| |   <| | | (_| |\ V  V // ___ \   |  _ < (_| | (_| | (_| | |
  \____\__,_|_|\_\_|  \__,_| \_/\_//_/   \_\  |_| \_\__,_|\__,_|\__,_|_|
```

[![PyPI](https://img.shields.io/badge/PyPI-cakrawala--radar-blue)](https://pypi.org/project/cakrawala-radar/)
[![Python](https://img.shields.io/badge/python-%3E%3D3.9-brightgreen)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

AI-powered airspace surveillance simulation and multi-sensor fusion toolkit for Indonesia-focused research.

Cakrawala Radar adalah library Python untuk riset, simulasi, analisis, dan visualisasi sistem pemantauan wilayah udara berbasis radar, ADS-B sintetis/publik, sensor fusion, anomaly detection, dan explainable AI. Library ini dibuat untuk konteks geografis Indonesia sebagai negara kepulauan dengan wilayah udara luas, area perbatasan, jalur penerbangan strategis, cuaca tropis, dan kebutuhan interoperabilitas multi-sensor.

## Author

**Lettu Kes dr. Muhammad Sobri Maulana, S.Kom, CEH, OSCP, OSCE**

- Email: [muhammadsobrimaulana31@gmail.com](mailto:muhammadsobrimaulana31@gmail.com)
- GitHub: [github.com/sobri3195](https://github.com/sobri3195)
- Website: [muhammadsobrimaulana.netlify.app](https://muhammadsobrimaulana.netlify.app)
- Sevalla Page: [muhammad-sobri-maulana-kvr6a.sevalla.page](https://muhammad-sobri-maulana-kvr6a.sevalla.page/)
- Online Store: [Toko Online Sobri](https://pegasus-shop.netlify.app)

## Community and Social Links

- YouTube: [@muhammadsobrimaulana6013](https://www.youtube.com/@muhammadsobrimaulana6013)
- Telegram: [t.me/winlin_exploit](https://t.me/winlin_exploit)
- TikTok: [@dr.sobri](https://www.tiktok.com/@dr.sobri)
- WhatsApp Group: [Cakrawala Radar Community](https://chat.whatsapp.com/B8nwRZOBMo64GjTwdXV8Bl)
- Gumroad: [maulanasobri.gumroad.com](https://maulanasobri.gumroad.com/)

## Support and Donation

Jika proyek ini bermanfaat untuk riset, edukasi, atau pembelajaran, Anda dapat mendukung pengembangan melalui:

- Lynk: [lynk.id/muhsobrimaulana](https://lynk.id/muhsobrimaulana)
- Trakteer: [trakteer.id/g9mkave5gauns962u07t](https://trakteer.id/g9mkave5gauns962u07t)
- KaryaKarsa: [karyakarsa.com/muhammadsobrimaulana](https://karyakarsa.com/muhammadsobrimaulana)
- Nyawer: [nyawer.co/MuhammadSobriMaulana](https://nyawer.co/MuhammadSobriMaulana)

## Features

- Lightweight data models for radar, ADS-B, fused tracks, weather, coverage, and scenarios.
- Primary, secondary, passive, coastal, and experimental radar-style sensor simulation.
- Synthetic ADS-B generation and conversion without automatic real-time API calls.
- Indonesia-focused synthetic routes such as Jakarta-Natuna, Makassar-Papua, Batam-Pontianak, and Ambon-Sorong.
- Multi-sensor fusion using confidence-weighted averaging and nearest-neighbor association.
- Simple Kalman filter for educational track smoothing.
- Rule-based anomaly detection with optional scikit-learn IsolationForest.
- Explainable anomaly notes with safe, non-kinetic recommendations.
- Coverage analysis with haversine distance and simple grids.
- Matplotlib visualization and a Rich/Typer CLI.

## Installation

Local editable install:

```powershell
py -m pip install -e .
```

Install from a local build:

```powershell
py -m pip install .
```

Development install:

```powershell
py -m pip install -e .[dev]
```

## Quickstart

```python
from cakrawala_radar import RadarSensor, AirObject, AnomalyDetector

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

print(sensor.can_detect(obj))
```

## Radar Simulation

```python
from cakrawala_radar import PrimaryRadarSensor, AirObject

sensor = PrimaryRadarSensor(
    sensor_id="PRI-JKT",
    name="Jakarta Primary Synthetic Radar",
    latitude=-6.2,
    longitude=106.8,
    coverage_radius_km=350,
    min_altitude_m=0,
    max_altitude_m=15000,
)

obj = AirObject("OBJ-1", -5.9, 107.0, 9000, 220, 40)
observation = sensor.observe(obj)
print(observation)
```

## Anomaly Detection

```python
from cakrawala_radar import AnomalyDetector
from cakrawala_radar.simulator import TrajectorySimulator

sim = TrajectorySimulator()
track = sim.generate_linear_route("OBJ-ANOM", (-6.2, 106.8), (3.95, 108.38), steps=12)
track = sim.simulate_heading_change(track, index=5, delta_deg=95)

result = AnomalyDetector().detect(track)
print(result.label, result.reasons)
```

## Sensor Fusion

```python
from cakrawala_radar import MultiSensorFusion, PrimaryRadarSensor, SecondaryRadarSensor, AirObject

obj = AirObject("OBJ-2", -4.0, 109.0, 10000, 240, 60, has_transponder=True)
sensors = [
    PrimaryRadarSensor("P-1", "Primary", -6.2, 106.8, 450, 0, 16000),
    SecondaryRadarSensor("S-1", "Secondary", -6.1, 107.0, 500, 0, 16000),
]
observations = [obs for sensor in sensors if (obs := sensor.observe(obj))]
fused = MultiSensorFusion().fuse_observations(observations)
print(fused)
```

## Coverage Analysis

```python
from cakrawala_radar import CoverageAnalyzer, RadarSensor

coverage = CoverageAnalyzer()
coverage.add_sensor(RadarSensor("RDR-JKT", "Jakarta", -6.2, 106.8, 350, 0, 15000))
result = coverage.compute_point_coverage(-5.8, 107.1, 10000)
print(result.covered, result.covering_sensors)
```

## CLI

```powershell
cakrawala-radar version
cakrawala-radar simulate --objects 3 --steps 20 --anomaly --output demo_tracks.csv
cakrawala-radar detect --input demo_tracks.csv --output anomaly_results.json --explain
cakrawala-radar coverage-demo --plot
cakrawala-radar fusion-demo
cakrawala-radar digital-twin-demo --steps 10
cakrawala-radar generate-dataset --samples 100 --anomaly-ratio 0.2 --output dataset.csv
```

## Testing, Build, and Publish

```powershell
py -m pytest
py -m build
py -m twine upload --repository testpypi dist/*
py -m twine upload dist/*
```

Smoke checks:

```powershell
py -m pip install .
python -c "import cakrawala_radar; print(cakrawala_radar.__version__)"
cakrawala-radar version
```

## Safety Disclaimer

Cakrawala Radar is for simulation, education, academic research, safety analysis, and high-level conceptual decision support only. It does not provide weapon systems, targeting, interception instructions, evasion, jamming, spoofing, radar hacking, access to operational radar systems, tactical military guidance, or restricted data workflows.

All included demos use synthetic data. The package does not automatically call external live-data APIs.

## Roadmap

- More route generators for maritime and archipelago research scenarios.
- Better uncertainty modeling and confidence calibration.
- Optional interactive notebooks.
- Expanded documentation and benchmark datasets based only on synthetic or public user-supplied data.

## Citation

```bibtex
@software{cakrawala_radar_2026,
  title = {Cakrawala Radar},
  author = {Muhammad Sobri Maulana},
  year = {2026},
  version = {0.1.0},
  note = {AI-powered airspace surveillance simulation and multi-sensor fusion toolkit}
}
```

## License

MIT. See [LICENSE](LICENSE).
