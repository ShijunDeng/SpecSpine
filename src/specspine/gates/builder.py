from __future__ import annotations

from pathlib import Path

from .constants import QUALITY_GATE_SOURCE_FILE
from .models import QualityGateReport
from .parsers import parse_definition_of_done, parse_required_checks

__all__ = [
    "build_quality_gate_report",
]


def _recommended_commands() -> tuple[str, ...]:
    return (
        "specspine gates . --json",
        "specspine validate . --fusion --features",
        "specspine status . --json --validate",
        "python3 -m unittest discover -s tests",
    )


def build_quality_gate_report(root: Path) -> QualityGateReport:
    resolved_root = root.expanduser().resolve()
    source_path = resolved_root / QUALITY_GATE_SOURCE_FILE

    if not source_path.exists():
        return QualityGateReport(
            root=resolved_root,
            source_file=QUALITY_GATE_SOURCE_FILE,
            source_missing=True,
            required_checks=(),
            definition_of_done=(),
            recommended_commands=_recommended_commands(),
        )

    content = source_path.read_text(encoding="utf-8")
    return QualityGateReport(
        root=resolved_root,
        source_file=QUALITY_GATE_SOURCE_FILE,
        source_missing=False,
        required_checks=parse_required_checks(content),
        definition_of_done=parse_definition_of_done(content),
        recommended_commands=_recommended_commands(),
    )
