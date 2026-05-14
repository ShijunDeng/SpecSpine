# Product Spec

## Scope

SpecSpine is a local CLI and file convention for spec-driven AI development. The product surface includes:

- Workspace initialization for intent, product, architecture, execution, and quality artifacts.
- Agent instruction generation through `specspine agents init`.
- Native feature bundles spanning `specs/features/`, `execution/features/`, and `quality/features/`, with generated guidance for spec, execution, quality, handoff, task issue drafts, tests, PR drafts, readiness, and validation.
- Native feature lifecycle status query/update across feature peer files, with an opt-in enforced transition policy for ordered lifecycle updates.
- Native feature task export from execution checklists.
- Native feature task issue draft packages with one local GitHub issue draft per execution task.
- Native feature traceability export across acceptance criteria, tasks, required checks, and test plans.
- Native feature readiness gate across peer files, lifecycle status, trace gaps, completed checklists, test plan evidence, release readiness, and optional completed local coverage links.
- Optional workspace readiness policy export from `.specspine/policy.yaml`, including policy-selected coverage-required readiness.
- Native feature handoff packets that compose status, trace, tasks, readiness, release readiness, next actions, and recommended commands.
- Native feature acceptance-test packets that map acceptance criteria to deterministic test cases, attach explicit local test coverage links, and surface existing test plans, quality checks, gaps, and blockers.
- Local GitHub issue draft generation from feature bundles without API calls.
- Local GitHub Pull Request draft generation from feature bundles without API calls.
- Local GitHub CLI synchronization plan and artifact generation from feature bundles without execution or API calls.
- Repository-level quality gate definition export from `quality/checklist.md` without executing checks.
- Fusion initialization for OpenSpec, Spec Kit, and Superpowers as external adapters.
- Adapter lifecycle mapping export for OpenSpec, Spec Kit, and Superpowers without probing upstream tools.
- Feature-specific adapter handoff export and optional local artifact materialization that combines native feature evidence with OpenSpec, Spec Kit, and Superpowers lifecycle context without executing upstream tools.
- Status, optional status validation summaries, opt-in validation warning details, optional filterable and policy-aware feature summaries, validation, doctor, and adapter inspection commands suitable for CI and coding agents.

## Non-Goals

- Hosting a server, database, or background daemon.
- Vendoring OpenSpec, Spec Kit, Superpowers, or any upstream source tree.
- Owning upstream lifecycle files after an external tool generates them.
- Reading GitHub tokens, writing GitHub tokens, or creating remote GitHub issues or pull requests by default.
- Replacing OpenSpec proposals, Spec Kit plans, or Superpowers skills with private reimplementations.

## User Workflows

- Initialize a base workspace with `specspine init .` and create agent guidance with `specspine agents init .`.
- Initialize the full fusion layer with `specspine fuse . --agent codex`, which writes adapter contracts but does not invoke upstream tools.
- Run `specspine status . --json` before work to understand missing artifacts, enabled upstreams, and next recommendations; add `--validate` when a single packet should also show quality-gate summary and failed check ids; add `--validation-warnings` with `--validate` only when scaffold warning details are needed; add `--feature-summaries` only when choosing or comparing multiple native features; add local summary filters such as `--feature-status validated --feature-ready yes --feature-priority high --feature-sort priority` when a multi-feature workspace needs triage; add `--feature-require-coverage` when all candidate readiness must include checked local AC coverage links, or `--feature-policy` when `.specspine/policy.yaml` should decide per feature.
- Create new requirements with `specspine feature new <slug> . --title "..." --why "..."`; the generated spec starts with local triage metadata for priority, owner, milestone, target release, project, and effort, and the peer files prompt for non-goals, edge cases, constraints, dependencies, open questions, traceability notes, focused handoff/task-issues/tests/pr/ready commands, and local validation gates.
- Move feature bundles through `proposed`, `planned`, `in-progress`, `implemented`, `validated`, and `archived` with `specspine feature status <slug> . --set STATUS`; add `--enforce-transition` when agents or CI should reject out-of-order transitions.
- Before archiving with `--enforce-transition`, pass `specspine feature ready <slug> . --json` so incomplete bundles cannot be archived by lifecycle status alone.
- Start implementation, acceptance, and review agent work with `specspine feature handoff <slug> . --json`.
- Hand execution checklists to implementation agents with `specspine feature tasks <slug> . --json`.
- Draft one local GitHub issue per execution task with `specspine feature task-issues <slug> . --json` or `--output`.
- Hand a full traceability packet to agents or reviewers with `specspine feature trace <slug> . --json`.
- Fail or pass a per-feature readiness gate with `specspine feature ready <slug> . --json`; add `--require-coverage` for high-risk or pre-release checks that require every AC to have a checked local `## Test Coverage` link; add `--policy` when the workspace policy should decide whether that stricter gate applies.
- Export the optional local governance context with `specspine policy . --json`; missing policy files return defaults with `source_missing: true` and do not make status or validation fail.
- Hand an acceptance-test packet with explicit local test coverage links to QA or testing agents with `specspine feature tests <slug> . --json`.
- Generate an offline issue draft with `specspine feature issue <slug> . --json` or `--output`.
- Generate an offline Pull Request draft with `specspine feature pr <slug> . --json` or `--output`.
- Review GitHub CLI synchronization intent with `specspine feature sync-plan <slug> . --json`, `--output`, or `--output-dir .specspine/sync-plan/<slug>` before any human decides to run `gh`.
- Export repository-level completion policy with `specspine gates . --json` before implementation, review, or CI wiring; this reports gate definitions only and does not run the recommended commands.
- Export adapter lifecycle mappings with `specspine adapters lifecycle . --json` before future adapter sync work; this reports local mapping definitions only and does not run upstream tools.
- Export `specspine adapters handoff <slug> . --json` when an agent needs a feature-specific OpenSpec, Spec Kit, and Superpowers handoff packet; add `--output-dir .specspine/adapter-handoff/<slug>` when separate reviewable adapter files and a manifest are needed. This reports recommended upstream steps as unexecuted plan data only.
- Verify readiness with `specspine validate . --fusion --features` and the unit test suite.

## Acceptance Criteria

- Base and fusion workspaces can be initialized without external dependencies.
- A complete fused workspace reports `workspace.complete=true` and `fusion.complete=true` in status JSON.
- `status --json --validate` reports `validation.ok`, summary counts, included check groups, and failed checks without changing the report command's zero exit behavior.
- `status --json --validate --validation-warnings` reports `validation.warning_checks`, while default status validation omits warning details and `status --validation-warnings` without `--validate` returns code `2`.
- `status --json --feature-summaries` reports compact per-feature lifecycle, priority, owner, progress, readiness, gap, blocking, next-action, and recommended-command summaries while default status JSON omits them.
- `status --feature-summaries` applies optional local `--feature-status`, `--feature-ready`, `--feature-priority`, `--feature-owner`, `--feature-sort`, and `--feature-sort-desc` controls to JSON and text summaries, and returns code `2` when those controls are unsupported or used without `--feature-summaries`.
- `status --feature-summaries --feature-require-coverage` computes summary readiness, blocking counts, next actions, and `--feature-ready` filters through the same local coverage gate as `feature ready --require-coverage`, adds `coverage_required: true` to those summaries, and leaves default summary fields unchanged when absent.
- `policy --json` reports `root`, `source_file`, `source_missing`, `readiness.require_coverage`, `summary`, and `recommended_commands`; the optional policy supports `enabled`, `default`, `priorities`, `statuses`, and `feature_ids`, warns on unknown priority/status values without failing, and requires no new dependency.
- `feature ready <slug> --json --policy` applies workspace policy to decide whether coverage is required, includes stable policy fields in JSON, and preserves explicit `--require-coverage` as an override.
- `status --feature-summaries --feature-policy` computes each feature summary with policy-selected coverage requirements, adds stable policy fields to those summaries, applies `--feature-ready yes/no` to policy readiness, returns code `2` without `--feature-summaries`, and preserves default status compatibility when absent.
- `status --feature-summaries` supports local metadata filters for milestone, target release, project, and effort, plus metadata sort keys for `milestone`, `target-release`, `project`, and `effort`; missing assignment fields normalize to `unassigned`, missing effort normalizes to `unknown`, and metadata defaults sort last.
- `feature tasks <slug> --json` reports stable ordered task records from `execution/features/<slug>.md`.
- `feature task-issues <slug> --json` reports a local issue draft package with one issue per execution task, including stable titles, bodies, source lines, task metadata, summary counts, and recommended local commands without calling GitHub APIs, `gh`, network services, upstream CLIs, or reading tokens.
- `feature trace <slug> --json` reports sources, missing files, acceptance criteria, tasks, required checks, test plan entries, summary counts, and trace gaps without calling external services.
- `feature ready <slug> --json` reports stable checks, blocking checks, summary counts, missing files, and gaps, returning non-zero until the feature is implemented or validated and all required evidence is complete; by default it does not require coverage links.
- `feature ready <slug> --json --require-coverage` appends `feature.test_coverage`, reports `coverage_required: true`, returns non-zero when any acceptance criterion lacks a checked link to an existing local relative target file, lists affected AC ids, and does not run tests, invoke subprocesses, call network services, read tokens, or add dependencies.
- `feature status <slug> --set STATUS --enforce-transition --json` reports stable transition success or failure payloads, preserves default manual status updates when the flag is absent, blocks writes for invalid transition edges or inconsistent current peer status, and requires readiness before enforced archive writes.
- `feature handoff <slug> --json` reports a compact feature packet with status, readiness, sources, gaps, blocking checks, trace sections, release readiness, recommended commands, deterministic next actions, and summary counts without calling external services.
- `feature tests <slug> --json` reports a QA-focused packet with status, readiness, source files, missing files, gaps, blocking checks, acceptance criteria, existing test plan, explicit `## Test Coverage` links, quality checks, deterministic `TC001 -> AC001` test cases with `covered`/`planned`/`pending` status, summary counts, and recommended local commands without running tests, generating test code, calling external services, or reading tokens.
- `feature pr <slug> --json` reports an offline Pull Request draft with title, body, status, readiness, sources, missing files, gaps, blocking checks, summary counts, and recommended commands without calling GitHub APIs, `gh`, network services, or reading tokens.
- `feature sync-plan <slug> --json` reports local GitHub CLI argv arrays for a feature issue, execution task issues, and a draft Pull Request, plus extended feature metadata, safety flags, notes, and recommended local commands without executing `gh`, calling GitHub APIs, using network services, invoking subprocesses, or reading tokens.
- `feature sync-plan <slug> --output-dir DIR` writes reviewable local artifacts including `manifest.json`, body Markdown files, and review-only `commands.sh`; it preserves JSON stdout compatibility, refuses command-owned file overwrites unless `--force` is passed, keeps PR commands draft-only, omits the PR dry-run flag, and preserves unknown files in existing directories.
- `gates --json` reports repository quality gate definitions from `quality/checklist.md`, including stable `GATE###` required checks, stable `DOD###` Definition Of Done items, optional required-gate metadata labels for severity, owner, and CI check names, default metadata values for unlabeled gates, non-failing metadata warnings, summary counts, source-missing state, and recommended local commands without executing checks, calling GitHub APIs, requiring `gh`, using network services, reading tokens, invoking upstream CLIs, or adding dependencies.
- `adapters lifecycle --json` reports OpenSpec, Spec Kit, and Superpowers lifecycle mappings for the six native statuses, including stable ids, native status meanings, upstream phases, upstream artifacts, agent focus, local commands, adapter enablement, local config paths, config existence, summary counts, and recommended local commands without executing shell commands, calling GitHub APIs, requiring `gh`, using network services, reading tokens, invoking upstream CLIs, or adding dependencies.
- `adapters handoff <slug> --json` reports native feature evidence plus selected OpenSpec, Spec Kit, and Superpowers mappings, adapter config state, upstream phases, artifacts, agent focus, local commands, notes, safe unexecuted recommended upstream steps, summary counts, and recommended local commands; `--output-dir DIR` writes `manifest.json`, `combined.md`, `combined.json`, focused per-adapter Markdown files, focused per-adapter JSON files, explicit false safety flags, and SHA-256 checksums for non-manifest managed artifacts with overwrite protection; partial bundles return `0`, missing bundles return `1`, invalid slugs return `2`, and the command does not execute subprocesses, probe tools, call network services, read tokens, invoke upstream CLIs, or add dependencies.
- `feature new <slug>` generates spec-level priority, owner, milestone, target release, project, and effort metadata plus unchecked quality and release-readiness gates so structural validation can pass while `feature ready` remains blocked until acceptance criteria, test coverage, docs or PR draft, and local validation evidence are complete.
- Enabled upstream metadata reports OpenSpec, Spec Kit, and Superpowers as enabled when their adapter files are present.
- Validation passes for complete workspace, fusion artifacts, and native feature bundles with consistent allowed lifecycle status; unchanged base workspace Markdown scaffold content is reported as warning checks rather than failures.
- Fusion config preserves `integration_mode: adapter` and `vendored_upstream_code: false`.
