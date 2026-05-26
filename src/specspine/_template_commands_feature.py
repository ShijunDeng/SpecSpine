from __future__ import annotations

__all__ = [
    "_TEMPLATE_COMMANDS_FEATURE",
]

_TEMPLATE_COMMANDS_FEATURE = """
    ## Feature Lifecycle Commands

    ```bash
    specspine retrospective report . --json
    specspine retrospective report . --feature <slug> --limit 3 --json
    specspine verify matrix <slug> . --json
    specspine change risk . --json
    specspine change risk . --feature <slug> --json
    specspine security cues . --json
    specspine security cues . --feature <slug> --json
    specspine provenance manifest . --json
    specspine provenance manifest . --feature <slug> --json
    specspine review packet . --json
    specspine review packet . --feature <slug> --json
    specspine loop packet . --json
    specspine gates . --json
    specspine adapters lifecycle . --json
    specspine validate .
    specspine validate . --features
    specspine validate . --fusion --features
    specspine propose "..." . --slug <slug> --dry-run
    specspine propose "..." . --slug <slug> --json
    specspine feature new <slug> . --title "..." --why "..."
    specspine feature status <slug> . --json
    specspine feature status <slug> . --set planned --enforce-transition --json
    specspine feature handoff <slug> . --json
    specspine feature tasks <slug> . --json
    specspine feature task-issues <slug> . --json
    specspine feature trace <slug> . --json
    specspine feature ready <slug> . --json
    specspine feature tests <slug> . --json
    specspine feature issue <slug> . --json
    specspine feature pr <slug> . --json
    specspine feature sync-plan <slug> . --json
    specspine feature archive <slug> . --json
    PYTHONPATH=src python3 -m unittest discover -s tests
    ```
"""
