# Spec-Code Consistency Scanner Quality

Feature ID: spec-code-consistency
Status: validated
Why: Provide reviewable local evidence that feature specs, implementation files, tests, docs, and changed paths still line up.

## Required Checks

- [x] Acceptance criteria are reviewed against the implementation in `src/specspine/consistency.py` and `src/specspine/cli.py`.
- [x] Focused unit and CLI tests cover report fields, reference extraction, changed paths, missing features, invalid slugs, and safety output.
- [x] Generated templates and project-local agent instructions include the consistency scan command.
- [x] Documentation describes syntax, JSON fields, exit codes, and read-only safety boundaries.
- [x] `specspine feature ready spec-code-consistency . --json --require-coverage` has no blocking checks.
- [x] `specspine validate . --fusion --features` passes.

## Test Coverage

- [x] AC001 -> tests/test_consistency.py::ConsistencyReportTests
- [x] AC002 -> tests/test_consistency.py::ConsistencyReportTests
- [x] AC003 -> tests/test_consistency.py::ConsistencyReportTests
- [x] AC004 -> tests/test_consistency.py::ConsistencyReportTests
- [x] AC005 -> tests/test_consistency.py::ConsistencyReportTests
- [x] AC006 -> tests/test_features.py::FeatureBundleTests
- [x] AC006 -> tests/test_agents.py::AgentsTests
- [x] AC007 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests
- [x] AC008 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_consistency`.
- Run `PYTHONPATH=src python3 -m unittest tests.test_agents tests.test_features tests.test_dogfood_artifacts`.
- Run `PYTHONPATH=src python3 -m specspine consistency scan . --feature spec-code-consistency --json`.
- Run `PYTHONPATH=src python3 -m specspine consistency scan . --feature missing-feature --json` and confirm exit code `1`.
- Run `PYTHONPATH=src python3 -m specspine consistency scan . --feature Bad --json` and confirm exit code `2`.
- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run the forbidden-content scans before commit.

## Review Notes

- The scanner is advisory evidence, not proof that tests ran.
- The scanner reuses local feature test coverage parsing so selectors normalize to existing local test files.
- Focused missing-feature behavior mirrors other local packet commands by returning structured JSON with a nonzero exit code.
- No remote calls, subprocess execution, upstream tool invocation, or credential reads are introduced.

## Release Readiness

- [x] RR001: Acceptance criteria, tasks, required checks, and test plan evidence are complete.
- [x] RR002: Docs, release notes, or `specspine feature pr spec-code-consistency . --json` output are ready for reviewers.
- [x] RR003: `specspine tests impact . --feature spec-code-consistency --json` has been reviewed for focused local test commands.
- [x] RR004: `specspine consistency scan . --feature spec-code-consistency --json` has been reviewed for local spec-code-test-doc drift.
- [x] RR005: `specspine verify matrix spec-code-consistency . --json` has been reviewed for AC-level verification evidence.
- [x] RR006: `specspine change risk . --feature spec-code-consistency --json` has been reviewed for changed-path risk evidence.
- [x] RR007: `specspine security cues . --feature spec-code-consistency --json` has been reviewed for security-sensitive cues.
- [x] RR008: `specspine provenance manifest . --feature spec-code-consistency --json` has been reviewed for local evidence hashes.
- [x] RR009: `specspine review packet . --feature spec-code-consistency --json` has been reviewed for local pre-merge evidence.
- [x] RR010: `specspine feature sync-plan spec-code-consistency . --json` has been reviewed before any remote sync.
- [x] RR011: `specspine feature archive spec-code-consistency . --json` has been reviewed before marking status archived.
- [x] RR012: `specspine feature ready spec-code-consistency . --json --require-coverage` and `specspine validate . --fusion --features` have been run.
- [x] RR013: No known blockers remain.
