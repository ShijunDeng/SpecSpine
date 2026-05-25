from __future__ import annotations

from .helpers import _dedupe

__all__ = [
    "_recommended_commands",
]


def _recommended_commands(
    changed_files: tuple[str, ...],
    feature_ids: tuple[str, ...],
) -> tuple[str, ...]:
    commands: list[str] = []
    if changed_files:
        for path in changed_files:
            commands.append(f"specspine change risk . --changed {path} --json")
            commands.append(f"specspine review packet . --changed {path} --json")
            commands.append(f"specspine tests impact . --changed {path} --json")
    else:
        commands.extend(
            [
                "specspine change risk . --json",
                "specspine review packet . --json",
                "specspine tests impact . --json",
            ]
        )
    for slug in feature_ids:
        commands.append(f"specspine change risk . --feature {slug} --json")
        commands.append(f"specspine review packet . --feature {slug} --json")
        commands.append(f"specspine tests impact . --feature {slug} --json")
        commands.append(
            f"specspine feature ready {slug} . --json --require-coverage"
        )
    return _dedupe(commands)
