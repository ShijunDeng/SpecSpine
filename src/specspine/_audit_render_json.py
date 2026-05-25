from __future__ import annotations

import json

from .audit_models import ComplianceReport


def render_compliance_json(report: ComplianceReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


__all__ = [
    "render_compliance_json",
]
