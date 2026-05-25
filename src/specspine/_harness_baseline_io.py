from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .harness_coverage_models import HarnessCoverageReport

__all__ = [
    "_load_baseline",
    "_save_baseline",
]


def _load_baseline(root: Path) -> dict[str, Any] | None:
    resolved_root = root.expanduser().resolve()
    baseline_path = resolved_root / ".specspine" / "harness-baseline.json"
    if not baseline_path.exists():
        return None
    try:
        content = baseline_path.read_text(encoding="utf-8")
        return json.loads(content)
    except (OSError, json.JSONDecodeError):
        return None


def _save_baseline(root: Path, report: HarnessCoverageReport) -> None:
    resolved_root = root.expanduser().resolve()
    baseline_dir = resolved_root / ".specspine"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    baseline_path = baseline_dir / "harness-baseline.json"
    data = report.as_dict()
    baseline_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
