"""Evaluation metrics for synthetic surveillance experiments."""

from __future__ import annotations

import math
from typing import Iterable, Sequence

from .geospatial import haversine_distance_km


def detection_rate(detected: int, total: int) -> float:
    """Return detected / total."""
    return detected / total if total else 0.0


def false_alarm_rate(false_alarms: int, total_alerts: int) -> float:
    """Return false alarms / total alerts."""
    return false_alarms / total_alerts if total_alerts else 0.0


def precision_recall_f1(true_positive: int, false_positive: int, false_negative: int) -> tuple[float, float, float]:
    """Return precision, recall, and F1 score."""
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def track_continuity_score(observed_steps: int, expected_steps: int) -> float:
    """Return continuity ratio for a track."""
    return observed_steps / expected_steps if expected_steps else 0.0


def coverage_ratio(covered_points: int, total_points: int) -> float:
    """Return covered points / total points."""
    return covered_points / total_points if total_points else 0.0


def mean_position_error(
    truth_points: Sequence[tuple[float, float]],
    estimated_points: Sequence[tuple[float, float]],
) -> float:
    """Return mean haversine position error in kilometers."""
    if len(truth_points) != len(estimated_points):
        raise ValueError("truth_points and estimated_points must have equal length")
    if not truth_points:
        return 0.0
    errors = [
        haversine_distance_km(t_lat, t_lon, e_lat, e_lon)
        for (t_lat, t_lon), (e_lat, e_lon) in zip(truth_points, estimated_points)
    ]
    return sum(errors) / len(errors)


def confidence_calibration_summary(confidences: Iterable[float], outcomes: Iterable[bool]) -> dict[str, float]:
    """Return basic confidence calibration summary."""
    confidence_list = list(confidences)
    outcome_list = [1.0 if item else 0.0 for item in outcomes]
    if len(confidence_list) != len(outcome_list):
        raise ValueError("confidences and outcomes must have equal length")
    if not confidence_list:
        return {"mean_confidence": 0.0, "accuracy": 0.0, "calibration_error": 0.0}
    mean_confidence = sum(confidence_list) / len(confidence_list)
    accuracy = sum(outcome_list) / len(outcome_list)
    calibration_error = math.fabs(mean_confidence - accuracy)
    return {
        "mean_confidence": mean_confidence,
        "accuracy": accuracy,
        "calibration_error": calibration_error,
    }
