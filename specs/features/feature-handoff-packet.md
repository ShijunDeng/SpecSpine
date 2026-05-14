# Feature Handoff Packet

Feature ID: feature-handoff-packet
Status: validated

## Why

Implementation, acceptance, and review agents need one compact local packet before they touch a feature. Existing `feature tasks`, `feature trace`, and `feature ready` commands expose the right evidence, but agents still have to stitch several commands together manually. A native handoff packet keeps the context boundary small and high signal.

## Users

- Implementation agents starting feature work from local repository evidence.
- Review agents checking readiness, gaps, open tasks, and blocking checks.
- Maintainers who want a deterministic packet without GitHub API calls, upstream CLIs, tokens, network access, or new dependencies.

## Scope

- Add `specspine feature handoff <slug> [path] [--json] [--output FILE] [--force]` under the `feature` command group.
- Compose the packet from local feature status, trace, ready, tasks, and release readiness evidence.
- Emit stable JSON with summary counts, sources, missing files, gaps, blocking checks, trace sections, release readiness, recommended commands, and deterministic next actions.
- Emit concise text suitable for pasting directly to another agent.
- Return `1` with a packet when no native feature files exist, return `2` for invalid slugs, and return `0` for partial bundles with explicit missing files, gaps, and next actions.

## Non-Goals

- Calling GitHub APIs, reading tokens, invoking upstream CLIs, or adding third-party Markdown dependencies.
- Inferring semantic coverage between acceptance criteria, tasks, checks, and test plans.
- Replacing focused `feature tasks`, `feature trace`, or `feature ready` views.

## Acceptance Criteria

- [x] `specspine feature handoff <slug> [path] [--json] [--output FILE] [--force]` is registered under the `feature` subcommand group.
- [x] JSON output includes `feature_id`, `status`, `ready`, `sources`, `missing_files`, `gaps`, `blocking_checks`, `summary`, `acceptance_criteria`, `tasks`, `quality_checks`, `test_plan`, `release_readiness`, `recommended_commands`, and `next_actions`.
- [x] Summary includes trace total/done/open, ready pass/fail/total, tasks total/done/open, gap count, and blocking check count.
- [x] Next actions are deterministic for missing bundles, partial bundles, trace gaps, open tasks, blocking checks, and ready bundles.
- [x] Text output includes feature/status/ready, counts, sources, next actions, open tasks, blocking checks, and key commands.
- [x] `--output` writes text, refuses overwrite by default, honors `--force`, and keeps stdout JSON when combined with `--json`.
- [x] Missing bundles return `1` with create-or-restore guidance; invalid slugs return `2`; partial bundles return `0` with missing files and gaps.
- [x] Documentation, agent guidance, tests, and this dogfood bundle describe the handoff workflow.
