from __future__ import annotations

__all__ = [
    "_recommended_commands",
]


def _recommended_commands(feature_ids: tuple[str, ...]) -> tuple[str, ...]:
    commands: list[str] = ["specspine drift monitor . --json"]
    for slug in feature_ids:
        commands.append(f"specspine drift monitor . --feature {slug} --json")
    commands.append("specspine consistency scan . --json")
    commands.append("specspine validate . --fusion --features")
    seen: set[str] = set()
    deduped: list[str] = []
    for c in commands:
        if c not in seen:
            seen.add(c)
            deduped.append(c)
    return tuple(deduped)
