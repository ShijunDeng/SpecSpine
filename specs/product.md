# Product Spec

## Scope

SpecSpine is a local CLI and file convention for spec-driven AI development. The product surface includes:

- Workspace initialization for intent, product, architecture, execution, and quality artifacts.
- Agent instruction generation through `specspine agents init`.
- Native feature bundles spanning `specs/features/`, `execution/features/`, and `quality/features/`, with generated guidance for spec, execution, quality, handoff, tests, PR drafts, readiness, and validation.
- Native feature lifecycle status query/update across feature peer files, with an opt-in enforced transition policy for ordered lifecycle updates.
- Native feature task export from execution checklists.
- Native feature traceability export across acceptance criteria, tasks, required checks, and test plans.
- Native feature readiness gate across peer files, lifecycle status, trace gaps, completed checklists, test plan evidence, and release readiness.
- Native feature handoff packets that compose status, trace, tasks, readiness, release readiness, next actions, and recommended commands.
- Native feature acceptance-test packets that map acceptance criteria to deterministic test cases, attach explicit local test coverage links, and surface existing test plans, quality checks, gaps, and blockers.
- Local GitHub issue draft generation from feature bundles without API calls.
- Local GitHub Pull Request draft generation from feature bundles without API calls.
- Fusion initialization for OpenSpec, Spec Kit, and Superpowers as external adapters.
- Status, optional status validation summaries, optional filterable feature summaries, validation, doctor, and adapter inspection commands suitable for CI and coding agents.

## Non-Goals

- Hosting a server, database, or background daemon.
- Vendoring OpenSpec, Spec Kit, Superpowers, or any upstream source tree.
- Owning upstream lifecycle files after an external tool generates them.
- Reading GitHub tokens, writing GitHub tokens, or creating remote GitHub issues or pull requests by default.
- Replacing OpenSpec proposals, Spec Kit plans, or Superpowers skills with private reimplementations.

## User Workflows

- Initialize a base workspace with `specspine init .` and create agent guidance with `specspine agents init .`.
- Initialize the full fusion layer with `specspine fuse . --agent codex`, which writes adapter contracts but does not invoke upstream tools.
- Run `specspine status . --json` before work to understand missing artifacts, enabled upstreams, and next recommendations; add `--validate` when a single packet should also show quality-gate summary and failed check ids; add `--feature-summaries` only when choosing or comparing multiple native features; add local summary filters such as `--feature-status validated --feature-ready yes --feature-sort slug` when a multi-feature workspace needs triage.
- Create new requirements with `specspine feature new <slug> . --title "..." --why "..."`; the generated peer files prompt for non-goals, edge cases, constraints, dependencies, open questions, traceability notes, focused handoff/tests/pr/ready commands, and local validation gates.
- Move feature bundles through `proposed`, `planned`, `in-progress`, `implemented`, `validated`, and `archived` with `specspine feature status <slug> . --set STATUS`; add `--enforce-transition` when agents or CI should reject out-of-order transitions.
- Before archiving with `--enforce-transition`, pass `specspine feature ready <slug> . --json` so incomplete bundles cannot be archived by lifecycle status alone.
- Start implementation, acceptance, and review agent work with `specspine feature handoff <slug> . --json`.
- Hand execution checklists to implementation agents with `specspine feature tasks <slug> . --json`.
- Hand a full traceability packet to agents or reviewers with `specspine feature trace <slug> . --json`.
- Fail or pass a per-feature readiness gate with `specspine feature ready <slug> . --json`.
- Hand an acceptance-test packet with explicit local test coverage links to QA or testing agents with `specspine feature tests <slug> . --json`.
- Generate an offline issue draft with `specspine feature issue <slug> . --json` or `--output`.
- Generate an offline Pull Request draft with `specspine feature pr <slug> . --json` or `--output`.
- Verify readiness with `specspine validate . --fusion --features` and the unit test suite.

## Acceptance Criteria

- Base and fusion workspaces can be initialized without external dependencies.
- A complete fused workspace reports `workspace.complete=true` and `fusion.complete=true` in status JSON.
- `status --json --validate` reports `validation.ok`, summary counts, included check groups, and failed checks without changing the report command's zero exit behavior.
- `status --json --feature-summaries` reports compact per-feature progress, readiness, gap, blocking, next-action, and recommended-command summaries while default status JSON omits them.
- `status --feature-summaries` applies optional local `--feature-status`, `--feature-ready`, `--feature-sort`, and `--feature-sort-desc` controls to JSON and text summaries, and returns code `2` when those controls are unsupported or used without `--feature-summaries`.
- `feature tasks <slug> --json` reports stable ordered task records from `execution/features/<slug>.md`.
- `feature trace <slug> --json` reports sources, missing files, acceptance criteria, tasks, required checks, test plan entries, summary counts, and trace gaps without calling external services.
- `feature ready <slug> --json` reports stable checks, blocking checks, summary counts, missing files, and gaps, returning non-zero until the feature is implemented or validated and all required evidence is complete.
- `feature status <slug> --set STATUS --enforce-transition --json` reports stable transition success or failure payloads, preserves default manual status updates when the flag is absent, blocks writes for invalid transition edges or inconsistent current peer status, and requires readiness before enforced archive writes.
- `feature handoff <slug> --json` reports a compact feature packet with status, readiness, sources, gaps, blocking checks, trace sections, release readiness, recommended commands, deterministic next actions, and summary counts without calling external services.
- `feature tests <slug> --json` reports a QA-focused packet with status, readiness, source files, missing files, gaps, blocking checks, acceptance criteria, existing test plan, explicit `## Test Coverage` links, quality checks, deterministic `TC001 -> AC001` test cases with `covered`/`planned`/`pending` status, summary counts, and recommended local commands without running tests, generating test code, calling external services, or reading tokens.
- `feature pr <slug> --json` reports an offline Pull Request draft with title, body, status, readiness, sources, missing files, gaps, blocking checks, summary counts, and recommended commands without calling GitHub APIs, `gh`, network services, or reading tokens.
- `feature new <slug>` generates unchecked quality and release-readiness gates so structural validation can pass while `feature ready` remains blocked until acceptance criteria, test coverage, docs or PR draft, and local validation evidence are complete.
- Enabled upstream metadata reports OpenSpec, Spec Kit, and Superpowers as enabled when their adapter files are present.
- Validation passes for complete workspace, fusion artifacts, and native feature bundles with consistent allowed lifecycle status.
- Fusion config preserves `integration_mode: adapter` and `vendored_upstream_code: false`.
