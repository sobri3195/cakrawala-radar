"""Human-readable explanations for anomaly outputs."""

from __future__ import annotations

from typing import Dict, List, Sequence

from .models import AirObject, AnomalyResult, FusedTrack


class ExplainableAnomaly:
    """Generate safe explanations and operator notes."""

    def explain(self, result: AnomalyResult, track_history: Sequence[AirObject | FusedTrack]) -> Dict[str, object]:
        """Return reason codes, summary, and a safe non-kinetic note."""
        return {
            "object_id": result.object_id,
            "label": result.label,
            "score": result.anomaly_score,
            "reason_codes": self.generate_reason_codes(result),
            "summary": self.generate_human_readable_summary(result, track_history),
            "operator_note": self.generate_operator_note(result),
        }

    def generate_reason_codes(self, result: AnomalyResult) -> List[str]:
        """Map reason text to compact reason codes."""
        mapping = {
            "heading": "HEADING_CHANGE",
            "Altitude": "ALTITUDE_INCONSISTENCY",
            "Speed": "SPEED_SPIKE",
            "dropout": "SENSOR_DROPOUT",
            "ADS-B": "MISSING_ADSB_IDENTITY",
            "route": "ROUTE_DEVIATION",
            "confidence": "LOW_CONFIDENCE",
        }
        codes: List[str] = []
        for reason in result.reasons:
            for token, code in mapping.items():
                if token.lower() in reason.lower() and code not in codes:
                    codes.append(code)
        return codes or ["NO_SIGNIFICANT_ANOMALY"]

    def generate_human_readable_summary(
        self,
        result: AnomalyResult,
        track_history: Sequence[AirObject | FusedTrack],
    ) -> str:
        """Generate Indonesian-language summary for research dashboards."""
        if result.label == "normal":
            return "Lintasan sintetis tampak normal berdasarkan aturan sederhana yang digunakan."
        joined = " ".join(result.reasons)
        if "heading" in joined.lower():
            return "Objek mengalami perubahan heading signifikan dalam interval pendek."
        if "ads-b" in joined.lower() or "transponder" in joined.lower():
            return "Data ADS-B tidak tersedia pada beberapa titik lintasan sintetis."
        if "confidence" in joined.lower():
            return "Confidence lintasan rendah sehingga perlu validasi data tambahan."
        return "Terdapat pola lintasan yang perlu ditinjau dalam konteks riset dan keselamatan."

    def generate_operator_note(self, result: AnomalyResult) -> str:
        """Return safe, non-kinetic next-step guidance."""
        if result.label == "normal":
            return "Lanjutkan pemantauan konseptual dan simpan histori lintasan untuk evaluasi."
        return (
            "Verifikasi dengan sensor tambahan, tinjau histori lintasan, lakukan validasi data, "
            "dan tingkatkan confidence dengan observasi berikutnya."
        )
