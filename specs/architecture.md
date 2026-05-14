# Architecture

## System Shape

SpecSpine is a small Python package under `src/specspine` with a command-line entry point. The architecture is file-first:

- `workspace` owns base workspace templates and required artifact checks.
- `agents` writes project-local `AGENTS.md` instructions.
- `features` creates and reads native feature bundles, updates lifecycle status, exports execution task handoffs, exports task issue draft packages, exports traceability handoffs, evaluates readiness gates including optional coverage-required readiness, exports compact feature handoff packets, exports acceptance-test packets, exports offline issue and Pull Request drafts, and exports local GitHub sync plans plus review artifacts.
- `adapters` describes external upstream tools, probes local availability only for explicit adapter checks, exports lifecycle mappings, builds feature-specific adapter handoff packets, and materializes optional local per-adapter handoff artifacts.
- `fusion` writes the OpenSpec + Spec Kit + Superpowers adapter layer.
- `gates` exports repository-level quality gate definitions and optional severity, owner, and CI metadata from `quality/checklist.md` without executing checks.
- `policy` reads optional `.specspine/policy.yaml` governance rules and exports policy-selected readiness coverage requirements without dependencies.
- `status` builds machine-readable workspace summaries, recommendations, optional validation summaries, and optional filterable native feature summaries.
- `validation` turns workspace, fusion, adapter, and feature contracts into checks and compact summary records.
- `cli` maps command-line arguments to those modules.

## Data And Interfaces

- `.specspine/spine.yaml` maps the backbone files for a workspace.
- `.specspine/policy.yaml` is an optional local governance file. Missing files report defaults and do not affect existing workspace validation.
- `.specspine/fusion.yaml` records enabled upstreams, the selected agent profile, and the adapter/no-vendor boundary.
- `.specspine/fusion-map.md` and `.specspine/adapters/*.md` document the human-facing integration contract.
- `specs/`, `execution/`, and `quality/` carry the repository-owned source of truth.
- Native feature bundles use peer files with matching `Feature ID: <slug>` markers and one allowed lifecycle `Status`.
- Generated native feature bundles include spec sections for acceptance and review, execution sections for dependencies/open questions and focused handoff commands, and quality sections for tests, PR draft, readiness, and validation gates.
- The main machine interfaces are `specspine status . --json`, `specspine status . --json --validate`, `specspine status . --json --validate --feature-summaries`, `specspine status . --json --validate --feature-summaries --feature-status validated --feature-ready yes --feature-sort slug`, `specspine status . --json --validate --feature-summaries --feature-require-coverage --feature-ready yes --feature-sort priority`, `specspine status . --json --feature-summaries --feature-policy --feature-ready yes`, `specspine policy . --json`, `specspine gates . --json`, `specspine feature handoff <slug> . --json`, `specspine adapters handoff <slug> . --json`, `specspine adapters handoff <slug> . --output-dir .specspine/adapter-handoff/<slug>`, `specspine feature task-issues <slug> . --json`, `specspine feature trace <slug> . --json`, `specspine feature ready <slug> . --json`, `specspine feature ready <slug> . --json --require-coverage`, `specspine feature ready <slug> . --json --policy`, `specspine feature tests <slug> . --json`, `specspine feature pr <slug> . --json`, `specspine feature sync-plan <slug> . --json`, `specspine feature sync-plan <slug> . --output-dir .specspine/sync-plan/<slug>`, and `specspine validate . --fusion --features`.

## Decisions

- Keep the CLI zero-dependency so it runs in constrained agent environments and source checkouts.
- Treat upstream tools as adapters. SpecSpine can print install hints and optionally run public initializer commands, but it does not copy or own upstream code.
- Keep GitHub issue support offline by drafting structured text/JSON instead of requiring `gh`, tokens, or API access.
- Keep task issue draft packages offline by deriving one local issue body per execution checklist task without remote sync.
- Keep GitHub Pull Request support offline by composing local feature evidence into review-ready Markdown instead of requiring `gh`, tokens, API access, or network calls.
- Keep GitHub sync planning local by exporting reviewable `gh` argv arrays, labels, body sources, optional artifact directories, and safety notes without executing `gh`, reading tokens, calling network services, or invoking subprocesses.
- Keep feature traceability export offline and extractive by parsing native Markdown sections without AI inference, upstream CLIs, GitHub APIs, or token reads.
- Keep feature readiness gates deterministic by deriving pass/fail checks from native files, trace gaps, lifecycle status, completed checklists, release readiness evidence, and opt-in local coverage link evidence when `--require-coverage` is passed.
- Keep workspace readiness policy optional and local: the parser supports only the documented YAML subset, warning on unknown priority/status selectors, and policy mode delegates coverage enforcement to the existing readiness gate.
- Keep feature handoff packets compact by composing existing local status, trace, task, readiness, and release readiness evidence rather than generating new content.
- Keep adapter feature handoff packets and artifact directories local by composing feature handoff evidence with static adapter lifecycle mappings, marking all upstream recommendations as unexecuted plan data, and writing only managed review files unless `--force` is passed.
- Keep acceptance-test packets deterministic and non-generative by mapping acceptance criteria to pending test cases and surfacing existing test plans, quality checks, gaps, and blockers without running tests or creating code.
- Keep generated feature templates focused on the current handoff/task-issues/tests/pr/sync-plan/ready workflow so agents start with local commands and unchecked gates instead of generic placeholders.
- Keep workspace feature summaries opt-in so default status remains a minimal startup context; compose summaries from local feature handoff evidence when multi-feature comparison is needed, then apply local status, readiness, explicit coverage-required readiness, policy-selected readiness, and sort controls only after `--feature-summaries` is explicitly requested.
- Keep repository quality gate metadata lightweight by parsing Markdown inline labels, defaulting missing metadata, warning on unsupported severities, and never executing the named CI check.
- Make validation executable and local so agents can detect missing files and broken contracts before and after edits.
- Keep `status --validate` as a report surface that summarizes failed checks while `validate` remains the failing gate command.

## Risks

- Template drift can make generated artifacts too generic. Dogfood this repository and update templates when repeated manual corrections appear.
- Upstream command surfaces may change. Keep adapter docs explicit and probe availability separately from core validation.
- Feature bundles can diverge across spec, execution, and quality files. Validate matching IDs, allowed statuses, and peer-file status consistency.
- Agent instructions can become stale. Prefer short rules that point back to status, validation, and repository specs.
