# Review Notes

## Current Review Focus

This repository is now being used as a SpecSpine workspace. Reviews should check both code behavior and the project-level artifacts that guide agents.

## Findings

- No current blocking defects recorded in project-level artifacts.
- The generated workspace templates were too generic for dogfooding and have been replaced with repository-specific intent, product, architecture, execution, and quality content.
- Native feature lifecycle status can now be queried, updated, listed in status JSON, and validated across peer files.
- `specspine status --validate` now reports workspace, fusion, and feature validation summaries without becoming a failing gate command.
- `specspine feature tasks` now exports execution checklist items into stable text and JSON task lists for implementation agents.
- `specspine feature trace` now exports a local traceability handoff that connects acceptance criteria, tasks, required checks, test plan entries, sources, and gaps.
- `specspine feature ready` now evaluates a local per-feature readiness gate with blocking checks and failing exit codes.
- `specspine feature handoff` now exports a compact feature packet that composes status, tasks, trace, readiness, release readiness, next actions, and key commands.
- No upstream code should be copied into this repository as part of fusion work.

## Decisions

- Treat `specspine status . --json` as the first context packet for future agents.
- Use `specspine status . --json --validate` when agents need context and failed quality checks together.
- Treat `specspine feature handoff <slug> . --json` as the default local feature packet for implementation, acceptance, and review agents.
- Use `specspine feature tasks <slug> . --json` as the focused execution checklist view when an agent only needs tasks.
- Treat `specspine feature trace <slug> . --json` as the local traceability handoff when reviewers need a complete feature packet.
- Treat `specspine feature ready <slug> . --json` as the local per-feature acceptance and release gate after implementation evidence is complete.
- Treat `specspine validate . --fusion --features` plus the unit test suite as the local completion gate.
- Keep GitHub issue generation offline and token-free by default.
- Keep native feature peer files on a consistent allowed lifecycle status.
- Use `--run-upstream` only after explicit user instruction.

## Release Notes

- The repository itself now contains a complete SpecSpine fusion workspace.
- Future feature work should start with native feature bundles under `specs/features/`, `execution/features/`, and `quality/features/`.
- Feature bundles support `proposed`, `planned`, `in-progress`, `implemented`, `validated`, and `archived` statuses.
- Status packets can now include compact validation summaries with failed checks only.
- Feature execution checklists can now be exported without generation, GitHub credentials, or upstream tool calls.
- Feature bundles can now be exported as deterministic traceability packets without generation, GitHub credentials, or upstream tool calls.
- Feature bundles can now be checked with deterministic readiness gates that fail on missing files, inconsistent statuses, trace gaps, incomplete checklist evidence, missing test plans, or open release readiness items.
- Feature bundles can now be exported as compact handoff packets without generation, GitHub credentials, token reads, network calls, upstream CLIs, or new dependencies.
