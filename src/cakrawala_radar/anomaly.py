"""Rule-based and optional ML anomaly detection."""

from __future__ import annotations

from typing import Iterable, List, Sequence

from .constants import SAFE_RECOMMENDED_ACTIONS
from .geospatial import haversine_distance_km
from .models import AirObject, AnomalyResult, FusedTrack


def _heading_delta(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


class AnomalyDetector:
    """Transparent rule-based anomaly detector for synthetic tracks."""

    def detect(self, track_history: Sequence[AirObject | FusedTrack]) -> AnomalyResult:
        """Score track history and return an explainable result."""
        if not track_history:
            raise ValueError("track_history must not be empty")
        scores = {
            "heading": self.score_heading_change(track_history),
            "altitude": self.score_altitude_change(track_history),
            "speed": self.score_speed_change(track_history),
            "dropout": self.score_sensor_dropout(track_history),
            "adsb": self.score_adsb_mismatch(track_history),
            "route": self.score_route_deviation(track_history),
            "confidence": self.score_low_confidence(track_history),
        }
        score = max(scores.values())
        reasons = self._reasons(scores)
        label = self.classify_score(score)
        return AnomalyResult(
            object_id=getattr(track_history[-1], "object_id", "unknown"),
            anomaly_score=round(score, 3),
            label=label,
            reasons=reasons or ["No significant anomaly detected."],
            recommended_action=SAFE_RECOMMENDED_ACTIONS[0 if label == "normal" else 1],
        )

    def score_heading_change(self, track_history: Sequence[AirObject | FusedTrack]) -> float:
        """Score sudden heading changes."""
        if len(track_history) < 2:
            return 0.0
        max_delta = max(
            _heading_delta(track_history[i].heading_deg, track_history[i - 1].heading_deg)
            for i in range(1, len(track_history))
        )
        return min(1.0, max_delta / 120.0)

    def score_altitude_change(self, track_history: Sequence[AirObject | FusedTrack]) -> float:
        """Score abrupt altitude changes."""
        if len(track_history) < 2:
            return 0.0
        max_delta = max(
            abs(track_history[i].altitude_m - track_history[i - 1].altitude_m)
            for i in range(1, len(track_history))
        )
        return min(1.0, max_delta / 3000.0)

    def score_speed_change(self, track_history: Sequence[AirObject | FusedTrack]) -> float:
        """Score abrupt speed changes."""
        if len(track_history) < 2:
            return 0.0
        max_delta = max(
            abs(track_history[i].speed_mps - track_history[i - 1].speed_mps)
            for i in range(1, len(track_history))
        )
        return min(1.0, max_delta / 140.0)

    def score_sensor_dropout(self, track_history: Sequence[AirObject | FusedTrack]) -> float:
        """Score long time gaps between track points."""
        if len(track_history) < 2:
            return 0.0
        gaps = []
        for i in range(1, len(track_history)):
            current = track_history[i].timestamp
            previous = track_history[i - 1].timestamp
            gaps.append(abs((current - previous).total_seconds()))
        max_gap = max(gaps)
        return min(1.0, max(0.0, (max_gap - 120.0) / 600.0))

    def score_adsb_mismatch(self, track_history: Sequence[AirObject | FusedTrack]) -> float:
        """Score missing transponder identity in AirObject histories."""
        air_objects = [item for item in track_history if isinstance(item, AirObject)]
        if not air_objects:
            return 0.0
        missing_ratio = sum(not item.has_transponder for item in air_objects) / len(air_objects)
        return min(1.0, missing_ratio)

    def score_route_deviation(self, track_history: Sequence[AirObject | FusedTrack]) -> float:
        """Score a single step that is unusually large relative to the route."""
        if len(track_history) < 3:
            return 0.0
        distances = []
        for i in range(1, len(track_history)):
            distances.append(
                haversine_distance_km(
                    track_history[i - 1].latitude,
                    track_history[i - 1].longitude,
                    track_history[i].latitude,
                    track_history[i].longitude,
                )
            )
        sorted_distances = sorted(distances)
        median = sorted_distances[len(sorted_distances) // 2]
        if median <= 1.0:
            return min(1.0, max(distances) / 100.0)
        excess = max(distances) - median
        return min(1.0, max(0.0, excess / max(250.0, median * 2.0)))

    def score_low_confidence(self, track_history: Sequence[AirObject | FusedTrack]) -> float:
        """Score low-confidence fused histories."""
        confidences = [item.confidence for item in track_history if isinstance(item, FusedTrack)]
        if not confidences:
            return 0.0
        return min(1.0, max(0.0, 0.5 - sum(confidences) / len(confidences)) * 2)

    def classify_score(self, score: float) -> str:
        """Map a score to normal, suspicious, or high_anomaly."""
        if score < 0.40:
            return "normal"
        if score < 0.70:
            return "suspicious"
        return "high_anomaly"

    def _reasons(self, scores: dict[str, float]) -> List[str]:
        reasons: List[str] = []
        if scores["heading"] >= 0.4:
            reasons.append("Sudden heading change detected.")
        if scores["altitude"] >= 0.4:
            reasons.append("Altitude inconsistency detected.")
        if scores["speed"] >= 0.4:
            reasons.append("Speed spike detected.")
        if scores["dropout"] >= 0.4:
            reasons.append("Possible sensor dropout or long observation gap.")
        if scores["adsb"] >= 0.4:
            reasons.append("ADS-B/transponder identity is missing for part of the synthetic track.")
        if scores["route"] >= 0.4:
            reasons.append("Unusual route deviation detected.")
        if scores["confidence"] >= 0.4:
            reasons.append("Low confidence fused track.")
        return reasons


class IsolationForestAnomalyDetector:
    """Optional scikit-learn IsolationForest wrapper with rule-based fallback."""

    def __init__(self) -> None:
        try:
            from sklearn.ensemble import IsolationForest
        except Exception:  # pragma: no cover - depends on optional dependency
            self.model = None
        else:
            self.model = IsolationForest(contamination=0.1, random_state=42)
        self.fallback = AnomalyDetector()

    def detect(self, track_history: Sequence[AirObject | FusedTrack]) -> AnomalyResult:
        """Detect anomalies using IsolationForest when available."""
        if self.model is None or len(track_history) < 5:
            return self.fallback.detect(track_history)
        features = [
            [item.latitude, item.longitude, item.altitude_m, item.speed_mps, item.heading_deg]
            for item in track_history
        ]
        predictions = self.model.fit_predict(features)
        anomaly_ratio = sum(pred == -1 for pred in predictions) / len(predictions)
        label = self.fallback.classify_score(anomaly_ratio)
        return AnomalyResult(
            object_id=getattr(track_history[-1], "object_id", "unknown"),
            anomaly_score=round(float(anomaly_ratio), 3),
            label=label,
            reasons=["IsolationForest flagged unusual synthetic feature patterns."],
            recommended_action="validate data quality",
        )
