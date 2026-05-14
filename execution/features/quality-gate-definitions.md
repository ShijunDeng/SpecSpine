# Quality Gate Definitions Execution

Feature ID: quality-gate-definitions
Status: validated
Why: Repository-level quality checklists should become deterministic local gate definitions for agents and CI planning without executing checks or touching GitHub.

## Milestones

- Add a repository-level quality gate parser.
- Expose the parser through a new `specspine gates` command.
- Preserve missing-source reporting as a reportable non-success state.
- Document the command and local quality-gate workflow.
- Dogfood the feature with validated native artifacts and focused tests.

## Tasks

- [x] Implement a small quality gate module for parsing `quality/checklist.md`.
- [x] Parse `## Required Checks` checkbox items into `GATE001` records.
- [x] Parse `## Definition Of Done` bullet items into `DOD001` records.
- [x] Build stable JSON and compact text renderers.
- [x] Wire `specspine gates [path] [--json]` into the CLI.
- [x] Return `0` when the source exists and `1` when the source is missing.
- [x] Keep the command extractive and free of subprocess, network, GitHub, token, upstream CLI, and dependency paths.
- [x] Add unit tests for JSON parsing, text output, missing source, section boundaries, and external-tool isolation.
- [x] Update README, architecture docs, product spec, execution plan, review notes, and agent guidance.
- [x] Add this dogfood bundle and verify readiness and validation.
- [x] Run the required unit, validation, gates, readiness, diff, and token-prefix checks.

## Dependencies

- Existing base workspace artifact `quality/checklist.md`.
- Existing CLI command and renderer patterns.
- Existing native feature readiness and validation contracts.

## Open Questions

- Whether future releases should sync exported CI check names into remote branch-protection policy after explicit confirmation.
- Whether later remote sync should map local gate definitions to GitHub branch-protection required checks or project policy fields.

## Agent Handoff

- Run `specspine gates . --json` to inspect repository-level quality gate definitions.
- Run `specspine status . --json --validate` for workspace context plus validation summary.
- Run `specspine feature handoff quality-gate-definitions . --json`.
- Run `specspine feature tests quality-gate-definitions . --json`.
- Run `specspine feature ready quality-gate-definitions . --json`.
- Run `specspine validate . --fusion --features`.
