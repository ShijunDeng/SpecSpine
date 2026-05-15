# Coverage Debt Report Execution

Feature ID: coverage-debt-report
Status: validated

## Tasks

- [x] Add a local `specspine.coverage` report builder that reuses native feature discovery, trace parsing, Test Coverage parsing, metadata, and policy logic.
- [x] Add `specspine coverage debt [path] [--json] [--policy]` CLI parsing and rendering.
- [x] Compute stable workspace totals for required features, covered ACs, missing ACs, debt features, and focused recommended commands.
- [x] Emit per-feature records with coverage requirement, policy selection, missing AC ids, open link ids, missing target link ids, unknown AC link ids, source files, missing files, and commands.
- [x] Keep the command read-only and local-only by avoiding subprocesses, network access, upstream CLIs, GitHub operations, and token reads.
- [x] Add unit coverage for universal JSON counts, text output, no-debt features, link classification, partial bundles, policy mode, local-only safety, and CLI help.
- [x] Add this dogfood bundle and coverage links that validate the new feature under the coverage-required readiness gate.
- [x] Update README, AGENTS, architecture docs, product specs, execution plan, and review notes to describe the coverage debt workflow.

## Verification

- Run `PYTHONPATH=src python3 -m unittest tests.test_coverage_debt`.
- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine coverage debt . --json`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready coverage-debt-report . --json --require-coverage`.
