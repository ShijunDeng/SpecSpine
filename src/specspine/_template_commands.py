from __future__ import annotations

__all__ = [
    "_TEMPLATE_COMMANDS",
]

_TEMPLATE_COMMANDS = """
    ## Common Commands

    ```bash
    specspine status . --json --validate
    specspine status . --json --validate --validation-warnings
    specspine status . --json --validate --feature-summaries
    specspine status . --json --validate --feature-summaries --feature-status validated --feature-ready yes --feature-sort slug
    specspine status . --json --validate --feature-summaries --feature-require-coverage --feature-ready yes --feature-sort priority
    specspine status . --json --readiness-summary
    specspine status . --json --readiness-summary --readiness-policy
    specspine coverage debt . --json
    specspine coverage debt . --json --policy
    specspine coverage plan . --json
    specspine coverage plan . --feature <slug> --limit 3 --json
    specspine analyze . --json
    specspine analyze . --json --feature <slug>
    specspine tests impact . --json
    specspine tests impact . --feature <slug> --json
    specspine consistency scan . --json
    specspine consistency scan . --feature <slug> --json
    specspine hygiene scan . --json
    specspine hygiene scan . --strict --json
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
