from __future__ import annotations

import shlex

from .feature_bundle import FeatureSyncPlan

__all__ = [
    "_render_command_lines",
    "_render_recommended_commands",
]


def _render_command_lines(plan: FeatureSyncPlan) -> list[str]:
    lines = ["", "## Commands", ""]
    for command in plan.commands:
        lines.extend(
            [
                f"### {command.id}",
                "",
                f"- Kind: {command.kind}",
                f"- Description: {command.description}",
                f"- Body source: {command.body_source}",
                f"- Creates remote: {'yes' if command.creates_remote else 'no'}",
                f"- Requires token: {'yes' if command.requires_token else 'no'}",
                f"- Requires network: {'yes' if command.requires_network else 'no'}",
                (
                    "- Safe to auto-run: "
                    f"{'yes' if command.safe_to_auto_run else 'no'}"
                ),
                f"- Command: `{shlex.join(command.argv)}`",
                "",
            ]
        )
    return lines


def _render_recommended_commands(plan: FeatureSyncPlan) -> list[str]:
    lines = ["## Recommended Local Commands", ""]
    lines.extend(f"- `{command}`" for command in plan.recommended_commands)
    return lines
