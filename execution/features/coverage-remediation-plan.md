# Coverage Remediation Plan Execution

Feature ID: coverage-remediation-plan
Status: validated

## Tasks

- [x] AC001 Add coverage plan builders and renderers in `src/specspine/coverage.py` that reuse feature discovery, trace parsing, Test Coverage parsing, metadata, policy selection, and coverage debt semantics.
- [x] AC002 Add `specspine coverage plan [path] [--json] [--policy] [--feature SLUG] [--limit N]` CLI parsing and return-code handling.
- [x] AC003 Emit stable JSON fields for root, mode, feature filter, plan items, summary, recommended commands, and safety notes.
- [x] AC004 Include per-item feature id, status, priority, owner, missing AC details, candidate test files, suggested quality links, recommended commands, and risk notes.
- [x] AC005 Keep summary counts independent from item limiting and keep ordinary debt reports as successful advisory output.
- [x] AC006 Add unit coverage for JSON, text, policy mode, feature filters, limits, missing features, invalid usage, no-debt output, and local-only safety.
- [x] AC007 Add dogfood artifacts and coverage links for default and coverage-required readiness.
- [x] AC008 Update README, AGENTS, agent template, and dogfood tests so the planner appears in reviewer and agent workflows.

## Verification

- Run `PYTHONPATH=src python3 -m unittest tests.test_coverage_plan`.
- Run `PYTHONPATH=src python3 -m unittest tests.test_coverage_debt tests.test_agents tests.test_dogfood_artifacts`.
- Run `PYTHONPATH=src python3 -m specspine coverage plan . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready coverage-remediation-plan . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready coverage-remediation-plan . --json --require-coverage`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features --json`.
