# Feature Coverage Readiness Quality

Feature ID: feature-coverage-readiness
Status: validated
Why: The optional readiness gate must be strict enough for release reviewers while remaining compatible, deterministic, and local-only.

## Required Checks

- [x] Default readiness does not add `feature.test_coverage` or require coverage links.
- [x] Coverage-required readiness passes with checked links to existing local relative target files.
- [x] Coverage-required readiness fails for missing links, unchecked links, and missing target files, with affected AC ids in the message.
- [x] JSON and text output expose the opt-in check and preserve exit-code behavior.
- [x] Missing and partial bundles do not crash when coverage is required.
- [x] Safety tests guard against subprocess, network, and token reads.
- [x] Documentation and agent workflow guidance describe when to use the stricter gate.

## Test Coverage

- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_feature_ready_default_does_not_require_coverage_links
- [x] AC002 -> tests/test_features.py::FeatureBundleTests::test_feature_ready_require_coverage_passes_with_checked_existing_targets
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_feature_ready_require_coverage_passes_with_checked_existing_targets
- [x] AC004 -> tests/test_features.py::FeatureBundleTests::test_feature_ready_require_coverage_fails_for_missing_open_or_missing_target_links
- [x] AC005 -> tests/test_features.py::FeatureBundleTests::test_feature_ready_require_coverage_missing_bundle_does_not_crash
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_feature_ready_require_coverage_does_not_read_tokens_or_call_network
- [x] AC007 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_feature_coverage_readiness_dogfood_bundle_passes_default_and_coverage_gates

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_features.FeatureBundleTests.test_feature_ready_default_does_not_require_coverage_links tests.test_features.FeatureBundleTests.test_feature_ready_require_coverage_passes_with_checked_existing_targets tests.test_features.FeatureBundleTests.test_feature_ready_require_coverage_fails_for_missing_open_or_missing_target_links tests.test_features.FeatureBundleTests.test_feature_ready_require_coverage_missing_bundle_does_not_crash tests.test_features.FeatureBundleTests.test_feature_ready_require_coverage_does_not_read_tokens_or_call_network`.
- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-coverage-readiness . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-coverage-readiness . --json --require-coverage`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.

## Review Notes

- The coverage check is metadata validation only; it does not execute test commands or inspect selectors after `::`.
- `target_exists=true` continues to mean the path before any selector is relative to the workspace root and exists locally.
- Default readiness remains unchanged so existing automation does not become stricter unless the new flag is explicitly passed.

## Release Readiness

- [x] Implementation, tests, and documentation are complete.
- [x] The dogfood bundle has checked local coverage links for every acceptance criterion.
- [x] Default readiness passes for `feature-coverage-readiness`.
- [x] Coverage-required readiness passes for `feature-coverage-readiness`.
- [x] `specspine validate . --fusion --features` passes.
