"""Simple tropical weather impact model."""

from __future__ import annotations

from .models import WeatherCondition


class WeatherImpactModel:
    """Estimate confidence degradation from weather-like conditions."""

    def estimate_detection_degradation(self, weather: WeatherCondition) -> float:
        """Return degradation factor from 0 to 1."""
        rain = min(1.0, max(0.0, weather.rain_intensity))
        cloud = min(1.0, max(0.0, weather.cloud_density))
        interference = min(1.0, max(0.0, weather.interference_factor))
        visibility_penalty = max(0.0, (10.0 - weather.visibility_km) / 10.0)
        wind_penalty = min(1.0, weather.wind_speed_mps / 40.0) * 0.1
        return min(0.8, rain * 0.25 + cloud * 0.15 + interference * 0.3 + visibility_penalty * 0.15 + wind_penalty)

    def apply_weather_to_sensor_confidence(self, confidence: float, weather: WeatherCondition) -> float:
        """Apply weather degradation to a confidence value."""
        degradation = self.estimate_detection_degradation(weather)
        return max(0.0, min(1.0, confidence * (1.0 - degradation)))
