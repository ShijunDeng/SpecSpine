from __future__ import annotations

import json

from .models import SecurityCueReport

__all__ = [
    "render_security_cue_json",
]


def render_security_cue_json(report: SecurityCueReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"
