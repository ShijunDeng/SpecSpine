from __future__ import annotations

__all__ = [
    "_format_task_lines",
]


def _format_task_lines(tasks: list[dict]) -> str:
    return "\n".join(
        f"- [ ] {t['id']}: {t['text']}\n  _Boundary: {t['boundary']}\n  _Depends: {t['depends']}"
        for t in tasks
    )
