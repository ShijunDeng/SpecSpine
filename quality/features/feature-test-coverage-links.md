# Feature Test Coverage Links Quality

Feature ID: feature-test-coverage-links
Status: validated
Why: Coverage links are useful only if they remain local, deterministic, source-attributed, and honest about target existence.

## Required Checks

- [x] Unit tests cover parsing checked, unchecked, selector-bearing, missing-target, and unknown-AC coverage links.
- [x] Unit tests cover JSON and text output for coverage links and linked test case status.
- [x] Unit tests cover summary coverage counts and local target existence.
- [x] Unit tests cover token-free, network-free, upstream-free, and dependency-free `feature tests` behavior.
- [x] Template generation includes Test Coverage guidance.
- [x] Dogfood artifacts are validated and pass readiness.

## Test Coverage

- [x] AC005 -> tests/test_features.py::FeatureBundleTests::test_feature_tests_cli_json_and_text_include_coverage_links
- [x] AC008 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_feature_test_coverage_links_dogfood_bundle_passes_its_gate

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-test-coverage-links . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature tests feature-test-coverage-links . --json`.

## Review Notes

- Coverage links are authored metadata, not test execution evidence.
- `target_exists` checks only the local path before any `::` selector; selector validity remains the test runner's responsibility.
- Unknown-AC checklist rows remain exportable so malformed metadata is visible instead of crashing the packet.

## Release Readiness

- [x] `feature-test-coverage-links` has complete spec, execution, and quality peer files.
- [x] Lifecycle status is `validated` across all peer files.
- [x] Acceptance criteria, tasks, required checks, test plan, test coverage links, and release readiness evidence are complete.
- [x] Local verification commands for this round pass.
