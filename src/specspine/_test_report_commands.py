from __future__ import annotations

__all__ = [
    "_recommended_test_packet_commands",
]


def _recommended_test_packet_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature tests {slug} . --json",
        f"specspine feature trace {slug} . --json",
        f"specspine feature ready {slug} . --json",
        f"specspine feature handoff {slug} . --json",
        "specspine validate . --fusion --features",
    )
