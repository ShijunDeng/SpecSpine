# AGENTS.md

SpecSpine is a zero-dependency Python CLI for spec-driven AI development. Treat `specs/`, `execution/`, `quality/`, and `.specspine/` as the local project context before changing code.

## Commands

```bash
PYTHONPATH=src python3 -m specspine status . --json --validate
PYTHONPATH=src python3 -m specspine status . --json --validate --validation-warnings
PYTHONPATH=src python3 -m specspine status . --json --validate --feature-summaries
PYTHONPATH=src python3 -m specspine status . --json --validate --feature-summaries --feature-status validated --feature-ready yes --feature-sort slug
PYTHONPATH=src python3 -m specspine status . --json --validate --feature-summaries --feature-require-coverage --feature-ready yes --feature-sort priority
PYTHONPATH=src python3 -m specspine status . --json --feature-summaries --feature-policy --feature-ready yes
PYTHONPATH=src python3 -m specspine policy . --json
PYTHONPATH=src python3 -m specspine gates . --json
PYTHONPATH=src python3 -m specspine adapters lifecycle . --json
PYTHONPATH=src python3 -m specspine adapters handoff <slug> . --json
PYTHONPATH=src python3 -m specspine adapters handoff <slug> . --output-dir .specspine/adapter-handoff/<slug>
PYTHONPATH=src python3 -m specspine validate . --fusion --features
PYTHONPATH=src python3 -m unittest discover -s tests
```

For new user-facing requirements, create a native bundle first:

```bash
PYTHONPATH=src python3 -m specspine feature new <slug> . --title "..." --why "..."
PYTHONPATH=src python3 -m specspine feature status <slug> . --json
PYTHONPATH=src python3 -m specspine feature status <slug> . --set planned --enforce-transition --json
PYTHONPATH=src python3 -m specspine feature handoff <slug> . --json
PYTHONPATH=src python3 -m specspine adapters handoff <slug> . --json
PYTHONPATH=src python3 -m specspine adapters handoff <slug> . --output-dir .specspine/adapter-handoff/<slug>
PYTHONPATH=src python3 -m specspine feature tasks <slug> . --json
PYTHONPATH=src python3 -m specspine feature task-issues <slug> . --json
PYTHONPATH=src python3 -m specspine feature trace <slug> . --json
PYTHONPATH=src python3 -m specspine feature ready <slug> . --json
PYTHONPATH=src python3 -m specspine feature ready <slug> . --json --require-coverage
PYTHONPATH=src python3 -m specspine feature ready <slug> . --json --policy
PYTHONPATH=src python3 -m specspine feature tests <slug> . --json
PYTHONPATH=src python3 -m specspine feature pr <slug> . --json
PYTHONPATH=src python3 -m specspine feature sync-plan <slug> . --json
PYTHONPATH=src python3 -m specspine feature sync-plan <slug> . --output-dir .specspine/sync-plan/<slug>
```

## Rules

- Start by reading `specspine status . --json --validate`; add `--validation-warnings` only when scaffold warning check ids are needed; use `specspine status . --json --validate --feature-summaries` when choosing or comparing multiple native features, and add local filters such as `--feature-status validated --feature-ready yes --feature-sort slug` for triage; add `--feature-require-coverage` when every candidate must use the stricter local AC coverage gate, or `--feature-policy` when `.specspine/policy.yaml` should decide per feature; use `specspine policy . --json` for workspace readiness governance; use `specspine gates . --json` when repository-level quality policy is needed; use `specspine adapters lifecycle . --json` for local adapter lifecycle mappings and `specspine adapters handoff <slug> . --json` or `--output-dir .specspine/adapter-handoff/<slug>` for feature-specific adapter handoff context; finish with `specspine validate . --fusion --features` and the unit test command above.
- Keep feature specs, implementation tasks, and quality checks traceable by `Feature ID`.
- Use `specspine feature new` as the starting workflow for new requirements; the generated peer files include focused handoff, task issue drafts, tests, PR, ready, and validation guidance, plus sync-plan review.
- Keep native feature peer files on a consistent lifecycle status with `specspine feature status`; prefer `--enforce-transition` when advancing lifecycle state.
- Before archiving, run `specspine feature ready <slug> . --json`; use `--require-coverage` for high-risk or release-bound features, use `--policy` when workspace readiness policy should select coverage requirements, then archive with `specspine feature status <slug> . --set archived --enforce-transition`.
- Start implementation, acceptance, and review handoffs with `specspine feature handoff <slug> . --json`; use `feature tasks`, `feature task-issues`, `feature trace`, `feature ready`, `feature ready --require-coverage`, `feature ready --policy`, and `feature tests` for focused follow-up views. For QA context, add local `## Test Coverage` checklist links such as `- [ ] AC001 -> tests/test_features.py` in `quality/features/<slug>.md`.
- Keep feature spec metadata local and explicit: priority, owner, milestone, target release, project, and effort are draft context for status, handoff, issue, PR, and sync-plan outputs, not automatic GitHub Issue Fields or Project updates.
- Use `specspine feature pr <slug> . --json` to prepare an offline Pull Request draft from local evidence without reading tokens or calling GitHub.
- Use `specspine feature sync-plan <slug> . --json` to review GitHub CLI sync intent without executing `gh`, reading tokens, or calling GitHub; use `--output-dir .specspine/sync-plan/<slug>` when maintainers need local body files, manifest, and review-only `commands.sh`.
- Use `specspine gates . --json` to export quality gate definitions and optional severity/owner/CI metadata only; do not treat it as executing tests, CI, or status checks.
- Use `specspine adapters lifecycle . --json` to export adapter lifecycle definitions only; do not treat it as invoking upstream tools.
- Use `specspine adapters handoff <slug> . --json` to export feature-specific OpenSpec, Spec Kit, and Superpowers adapter handoff data only; use `--output-dir .specspine/adapter-handoff/<slug>` to write local `manifest.json`, `combined.md`, and focused per-adapter Markdown files. Do not treat recommended upstream steps as executed commands.
- OpenSpec, Spec Kit, and Superpowers are external adapters only. Do not vendor upstream source code.
- Do not read or write GitHub tokens, and do not call GitHub APIs by default.
- Use `--run-upstream` only when the user explicitly asks to invoke upstream tools.
