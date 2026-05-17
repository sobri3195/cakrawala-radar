# Contributing

Thank you for helping improve Cakrawala Radar.

## Development Setup

```powershell
py -m pip install -e .[dev]
py -m pytest
```

## Guidelines

- Keep the project safe, legal, educational, and research-oriented.
- Do not add weapons, targeting, evasion, jamming, spoofing, intrusion, or operational military guidance.
- Do not add automatic network calls to live radar or restricted systems.
- Prefer synthetic or public user-supplied datasets.
- Keep new features typed, documented, and covered by focused tests.

## Pull Request Checklist

- Tests pass with `py -m pytest`.
- Public APIs have type hints and clear docstrings.
- Documentation/examples are updated when behavior changes.
- Security policy remains respected.
