from __future__ import annotations

__all__ = [
    "_recommended_commands",
    "_safety_notes",
]


def _recommended_commands(feature_id: str | None) -> tuple[str, ...]:
    if feature_id is None:
        return (
            "specspine provenance manifest . --json",
            "specspine validate . --fusion --features",
            "specspine review packet . --json",
            "specspine security cues . --json",
            "specspine change risk . --json",
        )

    return (
        f"specspine provenance manifest . --feature {feature_id} --json",
        f"specspine feature handoff {feature_id} . --json",
        f"specspine feature ready {feature_id} . --json --require-coverage",
        f"specspine feature trace {feature_id} . --json",
        f"specspine feature tests {feature_id} . --json",
        f"specspine tests impact . --feature {feature_id} --json",
        f"specspine review packet . --feature {feature_id} --json",
        f"specspine security cues . --feature {feature_id} --json",
        f"specspine change risk . --feature {feature_id} --json",
        "specspine validate . --fusion --features",
    )


def _safety_notes() -> tuple[str, ...]:
    return (
        "This provenance manifest is advisory only.",
        "Hashes prove only the local file bytes read at manifest build time.",
        "File contents are never included in this report.",
        "SpecSpine did not run commands, run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, read environment variables, or read tokens.",
    )
