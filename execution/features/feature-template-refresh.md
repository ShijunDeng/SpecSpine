# Feature Template Refresh Execution

Feature ID: feature-template-refresh
Status: validated
Why: New feature bundles should start with the same spec -> execution -> quality workflow that SpecSpine already exposes through local handoff, tests, PR, ready, and validation commands.

## Milestones

- [x] Inspect the existing feature template, trace parser, tests packet, readiness gate, and docs.
- [x] Refresh the generated spec, execution, and quality templates.
- [x] Update agent guidance and project documentation.
- [x] Add focused tests for template sections, commands, readiness behavior, trace/tests extraction, and compatibility.
- [x] Add this validated dogfood bundle.
- [x] Run the required local verification commands.

## Tasks

- [x] AC001 Update `src/specspine/features.py::build_feature_files` with focused spec sections for edge cases, constraints, and traceability notes.
- [x] AC002 Update the generated execution template with an Agent Handoff section listing local handoff, tasks, trace, tests, ready, PR, and validation commands.
- [x] AC003 Update the generated quality template with unchecked acceptance, test coverage, docs or PR draft, ready, validation, and release-readiness gates.
- [x] AC004 Keep `feature new` CLI arguments and overwrite/force behavior unchanged.
- [x] AC005 Update README, docs, specs, execution notes, quality review notes, root `AGENTS.md`, and `src/specspine/agents.py`.
- [x] AC006 Add or update unit tests for the refreshed template workflow.
- [x] AC007 Add validated dogfood peer files for `feature-template-refresh`.
- [x] AC008 Validate this dogfood feature bundle and confirm it passes the readiness gate.

## Dependencies

- [x] Existing `normalize_template()` behavior.
- [x] Existing `feature handoff`, `feature tasks`, `feature trace`, `feature tests`, `feature ready`, and `feature pr` exporters.
- [x] Existing `validate . --fusion --features` contract.
- [x] Existing feature overwrite and `--force` tests.

## Open Questions

- [x] No open questions remain for this round; keep the template minimal and revisit after future dogfood cycles.

## Agent Handoff

- [x] Run `PYTHONPATH=src python3 -m specspine feature handoff feature-template-refresh . --json` for the implementation and review packet.
- [x] Run `PYTHONPATH=src python3 -m specspine feature tasks feature-template-refresh . --json` for the focused implementation checklist.
- [x] Run `PYTHONPATH=src python3 -m specspine feature trace feature-template-refresh . --json` for traceability evidence.
- [x] Run `PYTHONPATH=src python3 -m specspine feature tests feature-template-refresh . --json` for acceptance-test packet evidence.
- [x] Run `PYTHONPATH=src python3 -m specspine feature ready feature-template-refresh . --json` for the feature readiness gate.
- [x] Run `PYTHONPATH=src python3 -m specspine feature pr feature-template-refresh . --json` for local PR draft evidence.
- [x] Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features` for the project-level gate.
