from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "ValidationHealth",
]


@dataclass(frozen=True)
class ValidationHealth:
    ok: bool
    pass_count: int
    fail_count: int
    warn_count: int
    skip_count: int
    total: int
    top_failing_rules: tuple[dict[str, str], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "fail_count": self.fail_count,
            "ok": self.ok,
            "pass_count": self.pass_count,
            "skip_count": self.skip_count,
            "top_failing_rules": list(self.top_failing_rules),
            "total": self.total,
            "warn_count": self.warn_count,
        }
