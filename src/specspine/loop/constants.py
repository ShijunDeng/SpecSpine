from __future__ import annotations

from typing import Any

__all__ = [
    "LOCAL_COMMAND_FLAGS",
    "LIFECYCLE_COMMANDS",
    "CONTEXT_COMMANDS",
    "VALIDATION_COMMANDS",
    "SUBAGENTS",
    "SAFETY_NOTES",
]

LOCAL_COMMAND_FLAGS: dict[str, bool] = {
    "creates_remote": False,
    "executed": False,
    "requires_network": False,
    "requires_token": False,
    "safe_to_auto_run": False,
}

LIFECYCLE_COMMANDS: dict[str, tuple[str, ...]] = {
    "proposed": (
        'specspine feature new <slug> . --title "..." --why "..."',
        "specspine feature status <slug> . --set planned --enforce-transition --json",
    ),
    "planned": (
        "specspine feature handoff <slug> . --json",
        "specspine feature tasks <slug> . --json",
    ),
    "in-progress": (
        "specspine feature tasks <slug> . --json",
        "specspine feature trace <slug> . --json",
    ),
    "implemented": (
        "specspine feature tests <slug> . --json",
        "specspine feature ready <slug> . --json",
    ),
    "validated": (
        "specspine feature pr <slug> . --json",
        "specspine validate . --fusion --features",
    ),
    "archived": (
        "specspine status . --json --validate",
    ),
}

CONTEXT_COMMANDS: tuple[dict[str, object], ...] = (
    {
        "id": "workspace-status",
        "description": "Load local workspace, fusion, feature summary, and readiness context.",
        "command": (
            "specspine status . --json --validate "
            "--feature-summaries --readiness-summary"
        ),
    },
    {
        "id": "feature-handoff",
        "description": "Open the focused local implementation packet for one feature.",
        "command": "specspine feature handoff <slug> . --json",
    },
    {
        "id": "feature-tasks",
        "description": "Read the focused local execution checklist for one feature.",
        "command": "specspine feature tasks <slug> . --json",
    },
    {
        "id": "feature-ready",
        "description": "Evaluate the local per-feature readiness gate.",
        "command": "specspine feature ready <slug> . --json",
    },
    {
        "id": "coverage-debt",
        "description": "Inspect local acceptance-criteria coverage debt.",
        "command": "specspine coverage debt . --json --policy",
    },
    {
        "id": "coverage-plan",
        "description": "Plan read-only remediation for missing coverage links.",
        "command": "specspine coverage plan . --json --policy",
    },
)

VALIDATION_COMMANDS: tuple[dict[str, object], ...] = (
    {
        "id": "unit-tests",
        "description": "Run the local Python unit test suite.",
        "command": "PYTHONPATH=src python3 -m unittest discover -s tests",
    },
    {
        "id": "workspace-validation",
        "description": "Validate workspace, fusion, and native feature contracts.",
        "command": "PYTHONPATH=src python3 -m specspine validate . --fusion --features",
    },
    {
        "id": "status-validation",
        "description": "Export local status with validation and feature summaries.",
        "command": (
            "PYTHONPATH=src python3 -m specspine status . --json --validate "
            "--feature-summaries --readiness-summary"
        ),
    },
)

SUBAGENTS: tuple[dict[str, object], ...] = (
    {
        "id": "implementation-worker",
        "focus": "Implement one native feature from local spec, execution, and quality evidence.",
        "inputs": (
            "specspine feature handoff <slug> . --json",
            "specspine feature tasks <slug> . --json",
        ),
        "outputs": (
            "code changes",
            "updated native feature bundle evidence",
        ),
    },
    {
        "id": "validation-worker",
        "focus": "Run focused local tests and readiness checks without remote services.",
        "inputs": (
            "specspine feature tests <slug> . --json",
            "specspine feature ready <slug> . --json",
        ),
        "outputs": (
            "test results",
            "readiness evidence",
        ),
    },
    {
        "id": "review-worker",
        "focus": "Review traceability, blockers, release readiness, and documentation.",
        "inputs": (
            "specspine feature trace <slug> . --json",
            "specspine feature pr <slug> . --json",
        ),
        "outputs": (
            "review notes",
            "quality gate updates",
        ),
    },
)

SAFETY_NOTES: tuple[str, ...] = (
    "The loop packet is local and deterministic.",
    "The builder does not call GitHub APIs, read or write tokens, invoke subprocesses, probe adapters, or access the network.",
    "Recommended commands are plan data only; every command is marked executed=false.",
    "The only write performed by the CLI is an explicit --output text packet write.",
)
