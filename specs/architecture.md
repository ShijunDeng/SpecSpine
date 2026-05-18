# Architecture

## System Shape

SpecSpine is a small Python package under `src/specspine` with a command-line entry point. The architecture is file-first:

- `workspace` owns base workspace templates and required artifact checks.
- `agents` writes project-local `AGENTS.md` instructions.
- `features` creates and reads native feature bundles, updates lifecycle status, exports execution task handoffs, exports task issue draft packages, exports traceability handoffs, evaluates readiness gates including optional coverage-required readiness, exports compact feature handoff packets, exports acceptance-test packets, exports offline issue and Pull Request drafts, and exports local GitHub sync plans plus review artifacts.
- `archive` composes existing native feature evidence into a local archive report and optional package files before lifecycle closure.
- `proposer` parses meaningful natural-language intent with deterministic string heuristics, derives valid feature slugs, generates EARS-like acceptance criteria, decomposes execution tasks with boundary/dependency annotations, and maps quality checks plus coverage placeholders into native feature bundle content.
- `adapters` describes external upstream tools, probes local availability only for explicit adapter checks, exports lifecycle mappings, builds feature-specific adapter handoff packets, and materializes optional local per-adapter handoff artifacts.
- `fusion` writes the OpenSpec + Spec Kit + Superpowers adapter layer.
- `gates` exports repository-level quality gate definitions and optional severity, owner, and CI metadata from `quality/checklist.md` without executing checks.
- `policy` reads optional `.specspine/policy.yaml` governance rules and exports policy-selected readiness coverage requirements without dependencies.
- `coverage` reports workspace-level coverage debt by combining native feature acceptance criteria, local Test Coverage links, and optional policy selection.
- `analysis` reports read-only native feature consistency and coverage findings by combining discovery, trace, readiness, task, quality, and Test Coverage evidence.
- `impact` reports local static source-to-test impact by mapping `src/specspine/*.py` modules to `tests/test_*.py` imports and feature coverage targets.
- `verification` reports local AC-level verification matrices by composing trace, tests, and coverage-required readiness evidence.
- `change` classifies changed paths, assigns local advisory risk, infers feature ids from native peer files, and composes feature readiness evidence.
- `security` detects local security-sensitive review cues from changed path text without printing file contents, proving vulnerabilities, or running scanners.
- `review` composes local pre-merge review packets from validation, quality gate definitions, static test impact, and optional native feature evidence.
- `status` builds machine-readable workspace summaries, recommendations, optional validation summaries, optional filterable native feature summaries, and optional workspace readiness rollups.
- `loop` builds local, deterministic agent loop packets from status feature summaries, readiness rollups, upstream metadata, lifecycle guidance, subagent roles, validation commands, and safety notes.
- `validation` turns workspace, fusion, adapter, and feature contracts into checks and compact summary records.
- `cli` maps command-line arguments to those modules.

## Data And Interfaces

- `.specspine/spine.yaml` maps the backbone files for a workspace.
- `.specspine/policy.yaml` is an optional local governance file. Missing files report defaults and do not affect existing workspace validation.
- `.specspine/fusion.yaml` records enabled upstreams, the selected agent profile, and the adapter/no-vendor boundary.
- `.specspine/fusion-map.md` and `.specspine/adapters/*.md` document the human-facing integration contract.
- `specs/`, `execution/`, and `quality/` carry the repository-owned source of truth.
- Native feature bundles use peer files with matching `Feature ID: <slug>` markers and one allowed lifecycle `Status`.
- Feature specs carry local triage metadata for priority, owner, milestone, target release, project, and effort; old specs without optional fields parse with stable defaults.
- Generated native feature bundles include spec sections for acceptance and review, execution sections for dependencies/open questions and focused handoff commands, and quality sections for tests, PR draft, readiness, and validation gates.
- The main machine interfaces are `specspine status . --json`, `specspine status . --json --validate`, `specspine status . --json --validate --feature-summaries`, `specspine status . --json --validate --feature-summaries --feature-status validated --feature-ready yes --feature-sort slug`, `specspine status . --json --validate --feature-summaries --feature-require-coverage --feature-ready yes --feature-sort priority`, `specspine status . --json --feature-summaries --feature-policy --feature-ready yes`, `specspine status . --json --readiness-summary`, `specspine status . --json --readiness-summary --readiness-policy`, `specspine coverage debt . --json`, `specspine coverage debt . --json --policy`, `specspine analyze . --json`, `specspine analyze . --json --feature <slug>`, `specspine tests impact . --json`, `specspine tests impact . --changed src/specspine/features.py --json`, `specspine tests impact . --feature <slug> --json`, `specspine verify matrix <slug> . --json`, `specspine change risk . --json`, `specspine change risk . --feature <slug> --changed src/specspine/features.py --json`, `specspine security cues . --json`, `specspine security cues . --feature <slug> --changed src/specspine/features.py --json`, `specspine provenance manifest . --json`, `specspine provenance manifest . --feature <slug> --include src/specspine/features.py --json`, `specspine review packet . --json`, `specspine review packet . --feature <slug> --changed src/specspine/review.py --json`, `specspine loop packet . --json`, `specspine policy . --json`, `specspine gates . --json`, `specspine propose "..." . --json`, `specspine propose "..." . --dry-run`, `specspine feature handoff <slug> . --json`, `specspine adapters handoff <slug> . --json`, `specspine adapters handoff <slug> . --output-dir .specspine/adapter-handoff/<slug>`, `specspine feature task-issues <slug> . --json`, `specspine feature trace <slug> . --json`, `specspine feature ready <slug> . --json`, `specspine feature ready <slug> . --json --require-coverage`, `specspine feature ready <slug> . --json --policy`, `specspine feature tests <slug> . --json`, `specspine feature pr <slug> . --json`, `specspine feature sync-plan <slug> . --json`, `specspine feature sync-plan <slug> . --output-dir .specspine/sync-plan/<slug>`, `specspine feature archive <slug> . --json`, `specspine feature archive <slug> . --output-dir .specspine/archive/<slug>`, and `specspine validate . --fusion --features`.

## Decisions

- Keep the CLI zero-dependency so it runs in constrained agent environments and source checkouts.
- Treat upstream tools as adapters. SpecSpine can print install hints and optionally run public initializer commands, but it does not copy or own upstream code.
- Keep GitHub issue support offline by drafting structured text/JSON instead of requiring `gh`, tokens, or API access.
- Keep task issue draft packages offline by deriving one local issue body per execution checklist task without remote sync.
- Keep GitHub Pull Request support offline by composing local feature evidence into review-ready Markdown instead of requiring `gh`, tokens, API access, or network calls.
- Keep GitHub sync planning local by exporting reviewable `gh` argv arrays, labels, body sources, optional artifact directories, and safety notes without executing `gh`, reading tokens, calling network services, or invoking subprocesses.
- Keep archive packaging local by composing existing native feature evidence, writing only to an explicit `--output-dir`, and leaving the lifecycle archive status update to the existing enforced status command.
- Keep provenance manifests local by hashing selected evidence files and feature peers without printing file contents, executing commands, or treating hashes as proof that tests ran.
- Keep extended feature metadata local by carrying it into status summaries, handoffs, test packets, issue drafts, PR drafts, and sync-plan artifacts without mapping it to GitHub Issue Fields, Projects, milestones, or assignees.
- Keep feature traceability export offline and extractive by parsing native Markdown sections without AI inference, upstream CLIs, GitHub APIs, or token reads.
- Keep feature readiness gates deterministic by deriving pass/fail checks from native files, trace gaps, lifecycle status, completed checklists, release readiness evidence, and opt-in local coverage link evidence when `--require-coverage` is passed.
- Keep workspace readiness policy optional and local: the parser supports only the documented YAML subset, warning on unknown priority/status selectors, and policy mode delegates coverage enforcement to the existing readiness gate.
- Keep feature handoff packets compact by composing existing local status, trace, task, readiness, and release readiness evidence rather than generating new content.
- Keep adapter feature handoff packets and artifact directories local by composing feature handoff evidence with static adapter lifecycle mappings, marking all upstream recommendations as unexecuted plan data, writing managed Markdown and JSON review files, and recording SHA-256 checksums for non-manifest managed artifacts unless `--force` is passed.
- Keep acceptance-test packets deterministic and non-generative by mapping acceptance criteria to pending test cases and surfacing existing test plans, quality checks, gaps, and blockers without running tests or creating code.
- Keep generated feature templates focused on the current handoff/task-issues/tests/pr/sync-plan/ready workflow so agents start with local commands and unchecked gates instead of generic placeholders.
- Keep proposal generation deterministic and local: no network calls, subprocesses, token reads, GitHub calls, upstream CLIs, or third-party dependencies are allowed in the intent-to-bundle path. Long intent is capped at 5000 characters with stable warnings, and same-slug bundle conflicts fail unless `--force` is passed, including dry-run previews.
- Keep workspace feature summaries opt-in so default status remains a minimal startup context; compose summaries from local feature handoff evidence when multi-feature comparison is needed, then apply local status, readiness, priority, owner, milestone, target release, project, effort, explicit coverage-required readiness, policy-selected readiness, and sort controls only after `--feature-summaries` is explicitly requested.
- Keep workspace readiness rollups opt-in so default status remains compact; compose `readiness_summary` from `list_feature_bundles`, `read_feature_metadata`, workspace policy, and `build_feature_ready_report`, then expose only counts, compact per-feature records, and focused local commands.
- Keep workspace coverage debt reporting local and read-only: reuse feature parsers and policy selectors to show exact AC coverage gaps after readiness rollups, but never execute tests or inspect tokens.
- Keep workspace analysis local, deterministic, and read-only: reuse native feature parsers and readiness data to report consistency, traceability, and coverage findings, return `0` by default when a report is built, and reserve nonzero issue exits for explicit `--fail-on-issues`.
- Keep test impact reporting local and advisory: parse source/test imports and feature coverage links to recommend commands, but never execute those commands or inspect tokens.
- Keep verification matrices local and advisory: compose existing trace, tests, and readiness evidence into AC-level rows, but never execute tests or treat coverage links as proof of execution.
- Keep change risk reporting local and advisory: classify paths with deterministic rules, reuse feature readiness evidence for inferred or provided feature ids, and leave all commands unexecuted.
- Keep security cue reporting local and advisory: report sensitive review keywords and file/line metadata without dumping content, claiming vulnerability proof, running tools, or inspecting tokens.
- Keep review packets compositional, local, and advisory: reuse validation, gate, impact, and native feature reports, return structured blockers for reviewers, and never execute recommended commands or inspect tokens.
- Keep loop packets local and read-only by reusing `build_status(..., include_feature_summaries=True, include_readiness_summary=True, ...)`, static lifecycle/subagent command records, and status upstream metadata; `specspine loop packet [path] [--json] [--output FILE] [--force] [--deadline VALUE]` does not call GitHub, read or write tokens, invoke subprocesses, probe adapters, or access the network.
- Sort local feature metadata deterministically: milestone, target release, and project use normalized lexical order with `unassigned` last; effort uses `XS`, `S`, `M`, `L`, `XL`, `XXL`, then `unknown`; slug remains the tie-breaker.
- Keep repository quality gate metadata lightweight by parsing Markdown inline labels, defaulting missing metadata, warning on unsupported severities, and never executing the named CI check.
- Make validation executable and local so agents can detect missing files and broken contracts before and after edits.
- Keep `status --validate` as a report surface that summarizes failed checks while `validate` remains the failing gate command.

## Risks

- Template drift can make generated artifacts too generic. Dogfood this repository and update templates when repeated manual corrections appear.
- Upstream command surfaces may change. Keep adapter docs explicit and probe availability separately from core validation.
- Feature bundles can diverge across spec, execution, and quality files. Validate matching IDs, allowed statuses, and peer-file status consistency.
- Agent instructions can become stale. Prefer short rules that point back to status, validation, and repository specs.
