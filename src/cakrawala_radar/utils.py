"""General utility helpers."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Clamp a numeric value."""
    return max(low, min(high, value))


def json_default(value: Any) -> str:
    """JSON serializer for datetime-like values."""
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def write_json(path: str | Path, data: Any) -> None:
    """Write indented UTF-8 JSON."""
    Path(path).write_text(json.dumps(data, indent=2, default=json_default), encoding="utf-8")


def read_json(path: str | Path) -> Any:
    """Read UTF-8 JSON."""
    return json.loads(Path(path).read_text(encoding="utf-8"))
