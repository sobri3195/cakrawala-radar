"""Simple multi-sensor fusion algorithms."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, Iterable, List, Sequence

from .adsb import ADSBMessage
from .geospatial import haversine_distance_km
from .models import FusedTrack, RadarObservation


class MultiSensorFusion:
    """Fuse radar observations using transparent educational methods."""

    def fuse_observations(self, observations: Sequence[RadarObservation]) -> List[FusedTrack]:
        """Group observations by object id and return fused tracks."""
        groups: Dict[str, List[RadarObservation]] = defaultdict(list)
        for observation in observations:
            groups[observation.object_id].append(observation)
        return [self.confidence_weighted_fusion(group) for group in groups.values()]

    def weighted_average_fusion(
        self,
        observations: Sequence[RadarObservation],
        weights: Sequence[float] | None = None,
    ) -> FusedTrack:
        """Fuse observations with explicit or uniform weights."""
        if not observations:
            raise ValueError("observations must not be empty")
        if weights is None:
            weights = [1.0] * len(observations)
        total = sum(weights) or 1.0
        latest = max(observations, key=lambda obs: obs.timestamp)
        return FusedTrack(
            track_id=f"FUSED-{latest.object_id}",
            object_id=latest.object_id,
            latitude=sum(obs.measured_latitude * weight for obs, weight in zip(observations, weights)) / total,
            longitude=sum(obs.measured_longitude * weight for obs, weight in zip(observations, weights)) / total,
            altitude_m=sum(obs.measured_altitude_m * weight for obs, weight in zip(observations, weights)) / total,
            speed_mps=sum(obs.measured_speed_mps * weight for obs, weight in zip(observations, weights)) / total,
            heading_deg=sum(obs.measured_heading_deg * weight for obs, weight in zip(observations, weights)) / total % 360,
            confidence=self.estimate_track_confidence(observations),
            sources=sorted({obs.sensor_id for obs in observations}),
            timestamp=latest.timestamp,
        )

    def confidence_weighted_fusion(self, observations: Sequence[RadarObservation]) -> FusedTrack:
        """Fuse observations using confidence as weights."""
        weights = [max(obs.confidence, 0.01) for obs in observations]
        return self.weighted_average_fusion(observations, weights)

    def associate_tracks(
        self,
        observations: Sequence[RadarObservation],
        distance_threshold_km: float = 25.0,
    ) -> List[List[RadarObservation]]:
        """Nearest-neighbor grouping by object id and spatial proximity."""
        groups: List[List[RadarObservation]] = []
        for obs in observations:
            placed = False
            for group in groups:
                anchor = group[0]
                distance = haversine_distance_km(
                    obs.measured_latitude,
                    obs.measured_longitude,
                    anchor.measured_latitude,
                    anchor.measured_longitude,
                )
                if obs.object_id == anchor.object_id or distance <= distance_threshold_km:
                    group.append(obs)
                    placed = True
                    break
            if not placed:
                groups.append([obs])
        return groups

    def remove_duplicate_tracks(
        self,
        tracks: Iterable[FusedTrack],
        distance_threshold_km: float = 5.0,
    ) -> List[FusedTrack]:
        """Remove near-duplicate fused tracks, keeping higher confidence."""
        kept: List[FusedTrack] = []
        for track in sorted(tracks, key=lambda item: item.confidence, reverse=True):
            duplicate = False
            for existing in kept:
                distance = haversine_distance_km(track.latitude, track.longitude, existing.latitude, existing.longitude)
                if track.object_id == existing.object_id and distance <= distance_threshold_km:
                    duplicate = True
                    break
            if not duplicate:
                kept.append(track)
        return kept

    def estimate_track_confidence(self, observations: Sequence[RadarObservation]) -> float:
        """Estimate fused confidence from average confidence and source diversity."""
        if not observations:
            return 0.0
        avg = sum(obs.confidence for obs in observations) / len(observations)
        diversity_bonus = min(0.2, 0.05 * len({obs.sensor_id for obs in observations}))
        return max(0.0, min(1.0, avg + diversity_bonus))

    def compare_adsb_and_radar(
        self,
        adsb_message: ADSBMessage,
        radar_observation: RadarObservation,
    ) -> Dict[str, float | bool]:
        """Compare synthetic ADS-B and radar observations."""
        distance_km = haversine_distance_km(
            adsb_message.latitude,
            adsb_message.longitude,
            radar_observation.measured_latitude,
            radar_observation.measured_longitude,
        )
        altitude_delta_m = abs(adsb_message.altitude_m - radar_observation.measured_altitude_m)
        return {
            "position_delta_km": distance_km,
            "altitude_delta_m": altitude_delta_m,
            "speed_delta_mps": abs(adsb_message.ground_speed_mps - radar_observation.measured_speed_mps),
            "consistent": distance_km <= 20 and altitude_delta_m <= 750,
        }
