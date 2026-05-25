from __future__ import annotations

__all__ = [
    "_TEMPLATE_RULES",
]

_TEMPLATE_RULES = """
    ## Working Rules

    - Read `specspine status . --json --validate` before planning or editing; add `--validation-warnings` only when scaffold warning check ids are needed.
    - Use `specspine status . --json --validate --feature-summaries` when choosing or comparing multiple native features; add local filters such as `--feature-status validated --feature-ready yes --feature-sort slug` for triage, and add `--feature-require-coverage` when candidate readiness must include checked local AC coverage links.
    - Use `specspine status . --json --readiness-summary` when an agent or CI job needs whole-workspace ready/not-ready counts; add `--readiness-policy` or `--readiness-require-coverage` when policy or universal coverage gates should apply.
    - Use `specspine coverage debt . --json` after coverage-required rollups to see exact feature and AC coverage gaps; add `--policy` when only policy-selected features should count as required debt. Use `specspine coverage plan . --json` to turn missing AC coverage into read-only reviewer or agent remediation steps; add `--feature <slug>`, `--limit N`, or `--policy` for focused local planning.
    - Use `specspine analyze . --json` before implementation to check native feature cross-artifact consistency, task traceability, and coverage evidence without changing files.
    - Use `specspine tests impact . --json` before and after edits to inspect local source-to-test impact recommendations; add `--changed PATH` for focused changes or `--feature <slug>` to include feature coverage targets.
    - Use `specspine consistency scan . --json` before and after implementation to inspect local spec-code-test-doc drift; add `--changed PATH` for focused changes or `--feature <slug>` for one native feature. Recommended commands are advisory and are not executed.
    - Use `specspine hygiene scan . --json` before review or commit to inspect generated cache artifacts and denylisted repository residue; add `--changed PATH` for focused context and `--strict` when high-risk findings should fail the command.
    - Use `specspine coverage plan . --json` to export local remediation planning evidence only. Do not treat coverage plan recommended commands as executed commands or proof that tests ran.
    - Use `specspine retrospective report . --json` before planning the next iteration or after review to inspect local feature delivery themes, blockers, coverage gaps, open tasks, and deterministic follow-up recommendations. Add `--feature <slug>` for one native feature or `--limit N` to trim recommendation rows only. Do not treat retrospective recommended commands as executed commands.
    - Use `specspine verify matrix <slug> . --json` before review or release to inspect AC-level verification evidence. Do not treat verification matrix recommended commands as executed commands or proof that tests ran.
    - Use `specspine change risk . --json` before review to classify changed paths by source, tests, feature peers, docs, or config and surface local risk evidence; add `--changed PATH` for focused changes or `--feature <slug>` for feature readiness context.
    - Use `specspine security cues . --json` before review to surface local security-sensitive keywords and path cues without proving vulnerabilities; add `--changed PATH` for focused changes or `--feature <slug>` for feature readiness context.
    - Use `specspine provenance manifest . --json` before review or archive to hash local evidence files and export feature provenance without reading file contents into the report; add `--include PATH` for focused artifacts or `--feature <slug>` for native feature evidence.
    - Use `specspine review packet . --json` before review or merge to compose local pre-merge review evidence from validation, quality gates, test impact, and optional feature packets; add `--feature <slug>` for focused native feature evidence. Recommended commands are advisory and are not executed.
    - Use `specspine loop packet . --json` when a worker needs a local, deterministic agent loop packet. Do not treat loop packet recommended commands as executed commands.
    - Use `specspine hygiene scan . --json` to export local repository hygiene evidence only. Do not treat hygiene scan recommended commands as executed commands.
    - Use `specspine gates . --json` when an agent or reviewer needs repository-level quality gate definitions; it exports definitions and does not execute checks.
    - Use `specspine adapters lifecycle . --json` when adapter lifecycle definitions are needed; it exports static local mappings and does not execute upstream tools.
    - For new natural-language requirements, start with `specspine propose "..." . --slug <slug> --dry-run` to preview the deterministic native bundle, then rerun without `--dry-run` when the spec, execution, and quality peers should be written. Use `specspine feature new` when a maintainer wants a manual template; the generated peer files include focused handoff, task issue drafts, tests, PR, readiness, and validation guidance, plus sync-plan review.
    - Keep feature peer files on a consistent lifecycle status with `specspine feature status`; prefer `--enforce-transition` when advancing lifecycle state.
    - Before archiving, run `specspine feature ready <slug> . --json`, package durable local evidence with `specspine feature archive <slug> . --json`, then archive with `specspine feature status <slug> . --set archived --enforce-transition`.
    - Start feature implementation, review, and acceptance handoffs with `specspine feature handoff <slug> . --json`.
    - Use `specspine feature tasks`, `specspine feature task-issues`, `specspine feature trace`, `specspine feature ready`, and `specspine feature tests` for focused task, task issue draft, trace, gate, and acceptance-test views.
    - For QA context, add local `## Test Coverage` checklist links such as `- [ ] AC001 -> tests/test_features.py` in `quality/features/<slug>.md`.
    - Use `specspine feature pr <slug> . --json` to prepare an offline Pull Request draft from local evidence without reading tokens or calling GitHub.
    - Use `specspine feature sync-plan <slug> . --json` to review GitHub CLI sync intent without executing `gh`, reading tokens, or calling GitHub.
    - Use `specspine feature archive <slug> . --json` to review local archive evidence before lifecycle closure; add `--output-dir .specspine/archive/<slug>` when maintainers need package files.
    - Run `specspine validate .` before and after edits; use `specspine validate . --fusion --features` when feature bundles or fusion artifacts are involved.
    - Keep OpenSpec, Spec Kit, and Superpowers as external adapters. Do not vendor upstream code.
    - By default, do not read or write GitHub tokens and do not call the GitHub API.
    - Use `--run-upstream` only when the user explicitly asks to invoke upstream tools.
"""
