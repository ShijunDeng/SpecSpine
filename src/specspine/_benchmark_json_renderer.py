from __future__ import annotations

import json

from .benchmark_models import BenchmarkReport

__all__ = [
    "render_benchmark_json",
]


def render_benchmark_json(report: BenchmarkReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"
