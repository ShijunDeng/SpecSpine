# Feature Retrospective & Self-Improvement Execution

Feature ID: feature-retrospective
Status: validated
Why: Scan completed feature bundles to compute deterministic local retrospective analytics and feed actionable improvement signals back into the next iteration.

## Milestones

- [x] M1: Define the retrospective report contract and command surface.
- [x] M2: Implement local report building, rendering, and CLI behavior.
- [x] M3: Update templates, docs, and dogfood evidence.
- [x] M4: Validate focused tests, full tests, readiness, and hygiene scans.

## Tasks

- [x] AC001 TASK001: AC001 AC002 AC005 AC006 - Add `src/specspine/retrospective.py` with stable report builder, summary/theme aggregation, recommendation ranking, JSON renderer, and text renderer.
- [x] AC002 TASK002: AC001 AC003 AC004 AC007 - Wire `specspine retrospective report` in `src/specspine/cli.py` with `--json`, `--feature`, `--limit`, invalid slug handling, invalid limit handling, and missing bundle exit behavior.
- [x] AC003 TASK003: AC001 AC002 AC003 AC004 AC005 AC006 AC007 - Add `tests/test_retrospective.py` for clean workspace output, focused feature output, missing/invalid feature behavior, limit behavior, theme aggregation, deterministic ranking, and safety notes.
- [x] AC004 TASK004: AC008 - Update `src/specspine/agents.py`, `AGENTS.md`, feature templates, proposer templates, and template tests with the retrospective command.
- [x] AC005 TASK005: AC009 - Update README, architecture, product, execution, and quality docs with workflow, JSON fields, limit behavior, and safety boundary.
- [x] AC006 TASK006: AC010 - Replace this dogfood bundle's placeholder content with checked implementation, coverage, test plan, and release-readiness evidence.
- [x] AC007 TASK007: AC010 - Update dogfood tests to include `feature-retrospective` status consistency, documentation snippets, no-placeholder checks, and readiness gates.
- [x] AC008 TASK008: AC001 AC010 - Run focused retrospective tests, template tests, dogfood tests, full unittest discovery, validation, hygiene scan, and forbidden-content scans.

## Dependencies

- Existing feature parsing and readiness helpers in `src/specspine/features.py`.
- Existing status metadata defaults and native feature bundle discovery.
- Existing dogfood test patterns for documentation and readiness coverage.

## Open Questions

- Should a later release persist retrospective snapshots as archive artifacts, or keep this report purely on-demand?
- Should recommendation ranking later be configurable by policy, or stay deterministic and built-in until real workflows need tuning?

## Agent Handoff

- Run `specspine feature handoff feature-retrospective . --json` before implementation or review handoff.
- Run `specspine adapters handoff feature-retrospective . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks feature-retrospective . --json` for the focused implementation checklist.
- Run `specspine feature task-issues feature-retrospective . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace feature-retrospective . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests feature-retrospective . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature feature-retrospective --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature feature-retrospective --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine verify matrix feature-retrospective . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature feature-retrospective --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature feature-retrospective --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature feature-retrospective --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature feature-retrospective --json` to compose local pre-merge review evidence.
- Run `specspine feature ready feature-retrospective . --json` after implementation evidence is complete.
- Run `specspine feature pr feature-retrospective . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan feature-retrospective . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan feature-retrospective . --output-dir .specspine/sync-plan/feature-retrospective` to materialize local sync review artifacts.
- Run `specspine feature archive feature-retrospective . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
