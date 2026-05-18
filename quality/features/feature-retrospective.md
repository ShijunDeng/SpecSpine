# Feature Retrospective & Self-Improvement Quality

Feature ID: feature-retrospective
Status: validated
Why: Scan completed feature bundles to compute deterministic local retrospective analytics and feed actionable improvement signals back into the next iteration.

## Required Checks

- [x] Acceptance criteria are reviewed against the implementation in `src/specspine/retrospective.py` and `src/specspine/cli.py`.
- [x] Focused tests cover report fields, feature filtering, limit validation, recommendation ranking, themes, missing bundles, text rendering, and safety output.
- [x] Generated templates and project-local agent instructions include the retrospective command.
- [x] Documentation describes syntax, JSON fields, limit behavior, and read-only safety boundaries.
- [x] `specspine feature ready feature-retrospective . --json --require-coverage` has no blocking checks after evidence is complete.
- [x] `specspine validate . --fusion --features` passes.

## Test Coverage

Use `- [ ] AC001 -> tests/...` to link existing local test files or test selectors.

- [x] AC001 -> tests/test_retrospective.py::RetrospectiveReportTests
- [x] AC002 -> tests/test_retrospective.py::RetrospectiveReportTests
- [x] AC003 -> tests/test_retrospective.py::RetrospectiveReportTests
- [x] AC004 -> tests/test_retrospective.py::RetrospectiveReportTests
- [x] AC005 -> tests/test_retrospective.py::RetrospectiveReportTests
- [x] AC006 -> tests/test_retrospective.py::RetrospectiveReportTests
- [x] AC007 -> tests/test_retrospective.py::RetrospectiveReportTests
- [x] AC008 -> tests/test_agents.py::AgentsTests
- [x] AC008 -> tests/test_features.py::FeatureBundleTests
- [x] AC009 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests
- [x] AC010 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_retrospective`.
- Run `PYTHONPATH=src python3 -m unittest tests.test_agents tests.test_features tests.test_dogfood_artifacts`.
- Run `PYTHONPATH=src python3 -m specspine retrospective report . --json`.
- Run `PYTHONPATH=src python3 -m specspine retrospective report . --feature feature-retrospective --limit 3 --json`.
- Run `PYTHONPATH=src python3 -m specspine verify matrix feature-retrospective . --json`.
- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine hygiene scan . --json --strict`.

## Review Notes

- Retrospective output is an evidence index, not a substitute for human review or release approval.
- Recommendation ranking is deterministic and local so agents can repeat the same next-action ordering.

## Release Readiness

- [x] Acceptance criteria, tasks, required checks, and test plan evidence are complete.
- [x] Docs, release notes, or `specspine feature pr feature-retrospective . --json` output are ready for reviewers.
- [x] `specspine tests impact . --feature feature-retrospective --json` has been reviewed for focused local test commands.
- [x] `specspine consistency scan . --feature feature-retrospective --json` has been reviewed for local spec-code-test-doc drift.
- [x] `specspine hygiene scan . --json` has been reviewed for generated artifacts and denylisted repository residue.
- [x] `specspine retrospective report . --json` has been reviewed for local feature improvement signals.
- [x] `specspine verify matrix feature-retrospective . --json` has been reviewed for AC-level verification evidence.
- [x] `specspine change risk . --feature feature-retrospective --json` has been reviewed for changed-path risk evidence.
- [x] `specspine security cues . --feature feature-retrospective --json` has been reviewed for security-sensitive cues.
- [x] `specspine provenance manifest . --feature feature-retrospective --json` has been reviewed for local evidence hashes.
- [x] `specspine review packet . --feature feature-retrospective --json` has been reviewed for local pre-merge evidence.
- [x] `specspine feature sync-plan feature-retrospective . --json` or `--output-dir .specspine/sync-plan/feature-retrospective` has been reviewed before any remote GitHub sync.
- [x] `specspine feature archive feature-retrospective . --json` has been reviewed before marking status archived.
- [x] `specspine feature ready feature-retrospective . --json --require-coverage` and `specspine validate . --fusion --features` have been run.
- [x] No known blockers remain, or blockers are documented in review notes.
