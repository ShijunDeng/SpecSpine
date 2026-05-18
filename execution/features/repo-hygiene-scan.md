# Repository Hygiene Scanner Execution

Feature ID: repo-hygiene-scan
Status: validated
Why: Provide a local, deterministic scanner that catches generated artifacts and denylisted residue before review or commit.

## Milestones

- [x] M1: Define the local hygiene report contract and command surface.
- [x] M2: Implement the scanner, CLI parser, JSON renderer, and text renderer.
- [x] M3: Add focused unit and CLI tests for generated artifacts, denylisted paths, denylisted content, changed paths, strict mode, and safety notes.
- [x] M4: Update generated templates, agent instructions, docs, and dogfood artifacts.
- [x] M5: Run focused and full validation before committing.

## Tasks

- [x] TASK001: AC001 AC002 - Add `src/specspine/hygiene.py` with stable dataclasses, report builder, JSON renderer, and text renderer.
- [x] TASK002: AC001 AC006 - Wire `specspine hygiene scan` in `src/specspine/cli.py` with `--json`, `--changed`, `--strict`, default exit `0`, and strict high-risk exit `1`.
- [x] TASK003: AC002 AC003 AC004 - Detect generated artifacts, denylisted paths, and denylisted content cues with deterministic finding metadata.
- [x] TASK004: AC005 - Normalize and de-duplicate repeated changed paths.
- [x] TASK005: AC007 - Preserve the read-only local boundary and keep recommended commands advisory.
- [x] TASK006: AC008 - Update `src/specspine/features.py`, `src/specspine/proposer.py`, `src/specspine/agents.py`, root `AGENTS.md`, and matching template tests.
- [x] TASK007: AC009 - Update README, architecture, product, execution, and quality docs with command syntax, fields, strict mode, and safety notes.
- [x] TASK008: AC010 - Replace the dogfood bundle placeholders with validated, checked traceability and coverage evidence.
- [x] TASK009: AC001 AC010 - Run `tests/test_hygiene.py`, template tests, dogfood tests, full unittest discovery, validation, and forbidden-content scans.

## Dependencies

- Existing CLI conventions for local packet commands and exit codes.
- Existing native feature readiness and coverage gate helpers for dogfood validation.
- Existing local review workflow around consistency, risk, security, provenance, and review packets.

## Open Questions

- Should a later release allow project-specific hygiene rules through an optional policy file?
- Should strict mode later support configurable severity thresholds after real CI usage produces enough feedback?

## Agent Handoff

- Run `specspine feature handoff repo-hygiene-scan . --json` before implementation or review handoff.
- Run `specspine adapters handoff repo-hygiene-scan . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks repo-hygiene-scan . --json` for the focused implementation checklist.
- Run `specspine feature task-issues repo-hygiene-scan . --json` to draft one local issue per execution task.
- Run `specspine feature trace repo-hygiene-scan . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests repo-hygiene-scan . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature repo-hygiene-scan --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature repo-hygiene-scan --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted residue.
- Run `specspine verify matrix repo-hygiene-scan . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature repo-hygiene-scan --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature repo-hygiene-scan --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature repo-hygiene-scan --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature repo-hygiene-scan --json` to compose local pre-merge review evidence.
- Run `specspine feature ready repo-hygiene-scan . --json` after implementation evidence is complete.
- Run `specspine feature pr repo-hygiene-scan . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan repo-hygiene-scan . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature archive repo-hygiene-scan . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
