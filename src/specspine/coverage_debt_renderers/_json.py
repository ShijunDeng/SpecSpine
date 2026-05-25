from __future__ import annotations

import json
from typing import Any

__all__ = [
    "render_coverage_debt_json",
]


def render_coverage_debt_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"
