from __future__ import annotations

__all__ = [
    "_recommended_commands",
    "_safety_notes",
]


def _recommended_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine verify matrix {slug} . --json",
        f"specspine feature trace {slug} . --json",
        f"specspine feature tests {slug} . --json",
        f"specspine feature ready {slug} . --json --require-coverage",
        f"specspine provenance manifest . --feature {slug} --json",
        f"specspine review packet . --feature {slug} --json",
        "specspine validate . --fusion --features",
    )


def _safety_notes() -> tuple[str, ...]:
    return (
        "This verification matrix is advisory local evidence.",
        "Recommended commands are advisory and are not executed.",
        "A verified row means the local acceptance criterion is checked and has at least one checked existing coverage link; it does not prove tests were run.",
        "SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, read environment variables, or read tokens.",
    )
