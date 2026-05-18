# Feature Analysis Report Execution

Feature ID: feature-analysis-report
Status: validated

## Tasks

- [x] AC001 Add a top-level `specspine analyze` CLI command with `path`, `--json`, `--feature`, and opt-in `--fail-on-issues` controls.
- [x] AC002 Build a reusable `specspine.analysis` module that emits deterministic JSON with workspace, summary, feature, issue, and recommendation fields.
- [x] AC003 Render compact text output with grouped issues and a clean success path.
- [x] AC004 Reuse existing native feature discovery, trace, readiness, task, quality, and coverage parsers for cross-artifact checks.
- [x] AC005 Classify Test Coverage links for unknown AC ids, missing local targets, and unchecked links.
- [x] AC006 Keep analysis read-only and local-only by avoiding subprocesses, adapter probes, token reads, network calls, and writes.
- [x] AC007 Add focused unit tests for JSON shape, text output, feature filters, issue detection, missing or invalid feature filters, and safety behavior.
- [x] AC008 Update README, AGENTS, architecture, product, execution, quality, and generated agent template references.

## Verification

- Run `PYTHONPATH=src python3 -m unittest tests.test_analysis`.
- Run `PYTHONPATH=src python3 -m specspine analyze . --json`.
- Run `PYTHONPATH=src python3 -m specspine analyze .`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-analysis-report . --json`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features --json`.
