# Repository Hygiene Scanner Quality

Feature ID: repo-hygiene-scan
Status: validated
Why: Provide reviewable local evidence that the repository contains no generated cache residue or denylisted hygiene violations before commit.

## Required Checks

- [x] Acceptance criteria are reviewed against the implementation in `src/specspine/hygiene.py` and `src/specspine/cli.py`.
- [x] Focused unit and CLI tests cover report fields, generated artifacts, denylisted paths, denylisted content, changed paths, strict mode, and safety output.
- [x] Generated templates and project-local agent instructions include the hygiene scan command.
- [x] Documentation describes syntax, JSON fields, strict mode, and read-only safety boundaries.
- [x] `specspine feature ready repo-hygiene-scan . --json --require-coverage` has no blocking checks.
- [x] `specspine validate . --fusion --features` passes.

## Test Coverage

- [x] AC001 -> tests/test_hygiene.py::HygieneReportTests
- [x] AC002 -> tests/test_hygiene.py::HygieneReportTests
- [x] AC003 -> tests/test_hygiene.py::HygieneReportTests
- [x] AC004 -> tests/test_hygiene.py::HygieneReportTests
- [x] AC005 -> tests/test_hygiene.py::HygieneReportTests
- [x] AC006 -> tests/test_hygiene.py::HygieneReportTests
- [x] AC007 -> tests/test_hygiene.py::HygieneReportTests
- [x] AC008 -> tests/test_features.py::FeatureBundleTests
- [x] AC008 -> tests/test_agents.py::AgentsTests
- [x] AC009 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests
- [x] AC010 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_hygiene`.
- Run `PYTHONPATH=src python3 -m unittest tests.test_agents tests.test_features tests.test_dogfood_artifacts`.
- Run `PYTHONPATH=src python3 -m specspine hygiene scan . --json`.
- Run `PYTHONPATH=src python3 -m specspine hygiene scan . --json --strict` and confirm the current clean workspace exits `0`.
- Run `PYTHONPATH=src python3 -m specspine verify matrix repo-hygiene-scan . --json`.
- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run the forbidden-content scans before commit.

## Review Notes

- The scanner is advisory evidence by default; strict mode is the opt-in failing gate for high-risk findings.
- The scanner reports metadata for denylisted content cues without printing matched file content.
- Scanner-owned source and test files are excluded from denylisted content scanning so rule definitions do not create self-findings.
- No remote calls, subprocess execution, upstream tool invocation, environment reads, or credential reads are introduced.

## Release Readiness

- [x] RR001: Acceptance criteria, tasks, required checks, and test plan evidence are complete.
- [x] RR002: Docs, release notes, or `specspine feature pr repo-hygiene-scan . --json` output are ready for reviewers.
- [x] RR003: `specspine tests impact . --feature repo-hygiene-scan --json` has been reviewed for focused local test commands.
- [x] RR004: `specspine consistency scan . --feature repo-hygiene-scan --json` has been reviewed for local spec-code-test-doc drift.
- [x] RR005: `specspine hygiene scan . --json` has been reviewed for generated artifacts and denylisted residue.
- [x] RR006: `specspine verify matrix repo-hygiene-scan . --json` has been reviewed for AC-level verification evidence.
- [x] RR007: `specspine change risk . --feature repo-hygiene-scan --json` has been reviewed for changed-path risk evidence.
- [x] RR008: `specspine security cues . --feature repo-hygiene-scan --json` has been reviewed for security-sensitive cues.
- [x] RR009: `specspine provenance manifest . --feature repo-hygiene-scan --json` has been reviewed for local evidence hashes.
- [x] RR010: `specspine review packet . --feature repo-hygiene-scan --json` has been reviewed for local pre-merge evidence.
- [x] RR011: `specspine feature sync-plan repo-hygiene-scan . --json` has been reviewed before any remote sync.
- [x] RR012: `specspine feature archive repo-hygiene-scan . --json` has been reviewed before marking status archived.
- [x] RR013: `specspine feature ready repo-hygiene-scan . --json --require-coverage` and `specspine validate . --fusion --features` have been run.
- [x] RR014: No known blockers remain.
