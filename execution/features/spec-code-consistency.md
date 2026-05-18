# Spec-Code Consistency Scanner Execution

Feature ID: spec-code-consistency
Status: validated
Why: Provide a local, deterministic scanner that links feature intent to code, tests, docs, and changed paths before review.

## Milestones

- [x] M1: Define the local consistency report contract and command surface.
- [x] M2: Implement the scanner, CLI parser, JSON renderer, and text renderer.
- [x] M3: Add focused unit and CLI tests for references, changed paths, missing features, invalid slugs, and safety notes.
- [x] M4: Update generated templates, agent instructions, docs, and dogfood artifacts.
- [x] M5: Run focused and full validation before committing.

## Tasks

- [x] TASK001: AC001 AC002 - Add `src/specspine/consistency.py` with stable dataclasses, report builder, JSON renderer, and text renderer.
- [x] TASK002: AC001 AC004 - Wire `specspine consistency scan` in `src/specspine/cli.py` with `--json`, `--feature`, `--changed`, missing-feature exit `1`, and invalid-slug exit `2`.
- [x] TASK003: AC002 AC003 - Extract local feature peer references, categorize implementation/test/documentation evidence, compose test coverage targets, and normalize changed paths.
- [x] TASK004: AC005 - Preserve the read-only local boundary and keep recommended commands advisory.
- [x] TASK005: AC006 - Update `src/specspine/features.py`, `src/specspine/proposer.py`, `src/specspine/agents.py`, root `AGENTS.md`, and matching template tests.
- [x] TASK006: AC007 - Update README, architecture, product, execution, and quality docs with command syntax, fields, exit codes, and safety notes.
- [x] TASK007: AC008 - Replace the dogfood bundle placeholders with validated, checked traceability and coverage evidence.
- [x] TASK008: AC001 AC008 - Run `tests/test_consistency.py`, template tests, dogfood tests, full unittest discovery, validation, and forbidden-content scans.

## Dependencies

- Existing native feature bundle discovery and status helpers in `src/specspine/features.py`.
- Existing feature tests packet coverage parsing for `## Test Coverage` links.
- Existing CLI conventions for local packet commands and exit codes.

## Open Questions

- Should a later release add configurable repository path categories for non-`src/specspine` projects?
- Should a later release let policy decide when warning checks become failing checks?

## Agent Handoff

- Run `specspine feature handoff spec-code-consistency . --json` before implementation or review handoff.
- Run `specspine adapters handoff spec-code-consistency . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks spec-code-consistency . --json` for the focused implementation checklist.
- Run `specspine feature task-issues spec-code-consistency . --json` to draft one local issue per execution task.
- Run `specspine feature trace spec-code-consistency . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests spec-code-consistency . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature spec-code-consistency --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature spec-code-consistency --json` to inspect local spec-code-test-doc drift.
- Run `specspine verify matrix spec-code-consistency . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature spec-code-consistency --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature spec-code-consistency --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature spec-code-consistency --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature spec-code-consistency --json` to compose local pre-merge review evidence.
- Run `specspine feature ready spec-code-consistency . --json` after implementation evidence is complete.
- Run `specspine feature pr spec-code-consistency . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan spec-code-consistency . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature archive spec-code-consistency . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
