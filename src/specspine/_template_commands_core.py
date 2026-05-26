from __future__ import annotations

__all__ = [
    "_TEMPLATE_COMMANDS_CORE",
]

_TEMPLATE_COMMANDS_CORE = """
    ## Core Commands

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
    ```
"""
