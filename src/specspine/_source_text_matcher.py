from __future__ import annotations

from typing import Any

__all__ = [
    "_modules_from_text",
]


def _modules_from_text(content: str, modules: dict[str, dict[str, Any]]) -> set[str]:
    matched: set[str] = set()
    for module, info in modules.items():
        stem = module.rsplit(".", 1)[-1]
        needles = {module, f"{stem}.py"}
        needles.update(str(symbol) for symbol in info["symbols"])
        if any(needle and needle in content for needle in needles):
            matched.add(module)
    return matched
