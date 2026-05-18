# AGENTS.md

SpecSpine is a zero-dependency Python CLI for spec-driven AI development. Treat `specs/`, `execution/`, `quality/`, and `.specspine/` as the local project context before changing code.

## Commands

```bash
PYTHONPATH=src python3 -m specspine status . --json --validate
PYTHONPATH=src python3 -m specspine status . --json --validate --validation-warnings
PYTHONPATH=src python3 -m specspine status . --json --validate --feature-summaries
PYTHONPATH=src python3 -m specspine status . --json --validate --feature-summaries --feature-status validated --feature-ready yes --feature-sort slug
PYTHONPATH=src python3 -m specspine status . --json --validate --feature-summaries --feature-require-coverage --feature-ready yes --feature-sort priority
PYTHONPATH=src python3 -m specspine status . --json --feature-summaries --feature-project "Native feature bundles" --feature-sort effort
PYTHONPATH=src python3 -m specspine status . --json --feature-summaries --feature-policy --feature-ready yes
PYTHONPATH=src python3 -m specspine status . --json --readiness-summary
PYTHONPATH=src python3 -m specspine status . --json --readiness-summary --readiness-policy
PYTHONPATH=src python3 -m specspine coverage debt . --json
PYTHONPATH=src python3 -m specspine coverage debt . --json --policy
PYTHONPATH=src python3 -m specspine analyze . --json
PYTHONPATH=src python3 -m specspine analyze . --json --feature <slug>
PYTHONPATH=src python3 -m specspine tests impact . --json
PYTHONPATH=src python3 -m specspine tests impact . --feature <slug> --json
PYTHONPATH=src python3 -m specspine change risk . --json
PYTHONPATH=src python3 -m specspine change risk . --feature <slug> --json
PYTHONPATH=src python3 -m specspine security cues . --json
PYTHONPATH=src python3 -m specspine security cues . --feature <slug> --json
PYTHONPATH=src python3 -m specspine review packet . --json
PYTHONPATH=src python3 -m specspine review packet . --feature <slug> --json
PYTHONPATH=src python3 -m specspine loop packet . --json
PYTHONPATH=src python3 -m specspine policy . --json
PYTHONPATH=src python3 -m specspine gates . --json
PYTHONPATH=src python3 -m specspine adapters lifecycle . --json
PYTHONPATH=src python3 -m specspine adapters handoff <slug> . --json
PYTHONPATH=src python3 -m specspine adapters handoff <slug> . --output-dir .specspine/adapter-handoff/<slug>
PYTHONPATH=src python3 -m specspine propose "add dark mode toggle" . --slug dark-mode-toggle --dry-run
PYTHONPATH=src python3 -m specspine validate . --fusion --features
PYTHONPATH=src python3 -m unittest discover -s tests
```

For new user-facing requirements, create a native bundle first:

```bash
PYTHONPATH=src python3 -m specspine propose "..." . --slug <slug> --json
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
PYTHONPATH=src python3 -m specspine feature archive <slug> . --json
PYTHONPATH=src python3 -m specspine feature archive <slug> . --output-dir .specspine/archive/<slug>
```

## Rules

- Start by reading `specspine status . --json --validate`; use `specspine loop packet . --json` when a worker needs a local, deterministic agent loop packet with feature summaries, readiness counts, lifecycle steps, subagents, validation commands, upstream metadata, and safety notes; add `--validation-warnings` only when scaffold warning check ids are needed; use `specspine status . --json --validate --feature-summaries` when choosing or comparing multiple native features, and add local filters such as `--feature-status validated --feature-ready yes --feature-project "Native feature bundles" --feature-sort effort` for triage; add `--feature-require-coverage` when every candidate must use the stricter local AC coverage gate, or `--feature-policy` when `.specspine/policy.yaml` should decide per feature; use `specspine status . --json --readiness-summary` when an agent or CI job needs ready/not-ready counts for the whole workspace in one packet, and add `--readiness-policy` or `--readiness-require-coverage` for policy-selected or universal coverage gates; use `specspine coverage debt . --json` after coverage-required rollups to see exact feature and AC coverage gaps, or add `--policy` when only policy-selected features should count as required debt; use `specspine analyze . --json` before implementation to check cross-artifact consistency, task traceability, and coverage evidence without changing files; use `specspine tests impact . --json` before and after edits to inspect local source-to-test impact recommendations, add `--changed PATH` for focused changes, or add `--feature <slug>` to include feature coverage targets; use `specspine change risk . --json` before review to classify changed paths and surface local risk evidence, add `--changed PATH` for focused changes, or add `--feature <slug>` for feature readiness context; use `specspine security cues . --json` before review to surface local security-sensitive cues without treating them as proven vulnerabilities; use `specspine review packet . --json` before review or merge to compose local pre-merge review evidence from validation, quality gates, test impact, and optional feature packets, and add `--feature <slug>` for focused native feature evidence; use `specspine policy . --json` for workspace readiness governance; use `specspine gates . --json` when repository-level quality policy is needed; use `specspine adapters lifecycle . --json` for local adapter lifecycle mappings and `specspine adapters handoff <slug> . --json` or `--output-dir .specspine/adapter-handoff/<slug>` for feature-specific adapter handoff context; finish with `specspine validate . --fusion --features` and the unit test command above.
- Keep feature specs, implementation tasks, and quality checks traceable by `Feature ID`.
- Use `specspine propose "..."` as the starting workflow when the requirement is natural-language intent; it deterministically generates spec, execution, and quality peers with EARS-like acceptance criteria, dependency-annotated tasks, and quality mappings. Use `specspine feature new` when a maintainer wants a manual template instead; generated peer files include focused handoff, task issue drafts, tests, PR, ready, and validation guidance.
- Keep native feature peer files on a consistent lifecycle status with `specspine feature status`; prefer `--enforce-transition` when advancing lifecycle state.
- Before archiving, run `specspine feature ready <slug> . --json`; use `--require-coverage` for high-risk or release-bound features, use `--policy` when workspace readiness policy should select coverage requirements, package durable local evidence with `specspine feature archive <slug> . --json` or `--output-dir .specspine/archive/<slug>`, then archive with `specspine feature status <slug> . --set archived --enforce-transition`.
- Start implementation, acceptance, and review handoffs with `specspine feature handoff <slug> . --json`; use `feature tasks`, `feature task-issues`, `feature trace`, `feature ready`, `feature ready --require-coverage`, `feature ready --policy`, and `feature tests` for focused follow-up views. For QA context, add local `## Test Coverage` checklist links such as `- [ ] AC001 -> tests/test_features.py` in `quality/features/<slug>.md`.
- Keep feature spec metadata local and explicit: priority, owner, milestone, target release, project, and effort are draft context for status, handoff, issue, PR, and sync-plan outputs, not automatic GitHub Issue Fields or Project updates.
- Use `specspine feature pr <slug> . --json` to prepare an offline Pull Request draft from local evidence without reading tokens or calling GitHub.
- Use `specspine feature sync-plan <slug> . --json` to review GitHub CLI sync intent without executing `gh`, reading tokens, or calling GitHub; use `--output-dir .specspine/sync-plan/<slug>` when maintainers need local body files, manifest, and review-only `commands.sh`.
- Use `specspine feature archive <slug> . --json` before lifecycle closure to review durable local archive evidence; use `--output-dir .specspine/archive/<slug>` when maintainers need `README.md`, `archive.json`, and source snapshots. The command does not mark status archived.
- Use `specspine gates . --json` to export quality gate definitions and optional severity/owner/CI metadata only; do not treat it as executing tests, CI, or status checks.
- Use `specspine adapters lifecycle . --json` to export adapter lifecycle definitions only; do not treat it as invoking upstream tools.
- Use `specspine adapters handoff <slug> . --json` to export feature-specific OpenSpec, Spec Kit, and Superpowers adapter handoff data only; use `--output-dir .specspine/adapter-handoff/<slug>` to write local `manifest.json`, `combined.md`, `combined.json`, focused per-adapter Markdown files, focused per-adapter JSON files, and SHA-256 checksums. Do not treat recommended upstream steps as executed commands.
- Use `specspine loop packet . --json` to export local loop context only. Do not treat loop packet recommended commands as executed commands.
- Use `specspine change risk . --json` to export local changed-path risk evidence only. Do not treat change risk recommended commands as executed commands.
- Use `specspine security cues . --json` to export local security-sensitive review cues only. Do not treat security cue recommended commands as executed commands or vulnerability proof.
- Use `specspine review packet . --json` to export local pre-merge review evidence only. Do not treat review packet recommended commands as executed commands.
- OpenSpec, Spec Kit, and Superpowers are external adapters only. Do not vendor upstream source code.
- Do not read or write GitHub tokens, and do not call GitHub APIs by default.
- Use `--run-upstream` only when the user explicitly asks to invoke upstream tools.
