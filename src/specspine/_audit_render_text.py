from __future__ import annotations

from .audit_models import ComplianceReport
from ._audit_header_renderer import render_audit_header
from ._audit_feature_renderer import render_audit_features
from ._audit_footer_renderer import render_audit_footer


def render_compliance_text(report: ComplianceReport) -> str:
    lines = render_audit_header(report)
    lines.extend(render_audit_features(report))
    lines.extend(render_audit_footer(report))
    return "\n".join(lines) + "\n"


__all__ = [
    "render_compliance_text",
]
