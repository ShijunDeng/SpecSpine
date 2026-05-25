from __future__ import annotations


def _feature_trace_command(slug: str) -> str:
    return f"specspine feature trace {slug} . --json"


def _feature_ready_command(slug: str) -> str:
    return f"specspine feature ready {slug} . --json --require-coverage"


def _feature_tests_command(slug: str) -> str:
    return f"specspine feature tests {slug} . --json"


__all__ = [
    "_feature_trace_command",
    "_feature_ready_command",
    "_feature_tests_command",
]
