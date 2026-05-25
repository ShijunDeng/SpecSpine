from __future__ import annotations

__all__ = ["_render_task_issue_commands"]


def _render_task_issue_commands(commands: tuple[str, ...]) -> list[str]:
    return [f"- `{command}`" for command in commands]
