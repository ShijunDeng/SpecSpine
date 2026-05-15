# Feature Test Packet Quality

Feature ID: feature-test-packet
Status: validated
Why: The acceptance-test packet is valuable only if it is deterministic, local, non-generative, token-free, and honest about missing evidence.

## Required Checks

- [x] Unit tests cover `feature tests` JSON and text output for ready bundles.
- [x] Unit tests cover deterministic `TC001 -> AC001` mapping from acceptance criteria.
- [x] Unit tests cover partial bundles with missing files, trace gaps, empty test plan or quality sections, and blocking readiness checks.
- [x] Unit tests cover missing bundles returning a packet and non-zero exit code.
- [x] Unit tests cover invalid slugs returning exit code `2`.
- [x] Unit tests cover `--output`, overwrite refusal, `--force`, and `--json --output`.
- [x] Unit tests cover operation without GitHub tokens, `gh`, network access, upstream CLIs, or new dependencies.
- [x] Documentation, agent guidance, and dogfood artifacts describe the acceptance-test packet.

## Test Coverage

- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_feature_tests_cli_text_and_json_outputs_ready_bundle
- [x] AC002 -> tests/test_features.py::FeatureBundleTests::test_feature_tests_does_not_require_gh_network_tokens_or_dependencies
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_feature_tests_cli_text_and_json_outputs_ready_bundle
- [x] AC004 -> tests/test_features.py::FeatureBundleTests::test_build_feature_tests_report_maps_one_test_case_per_acceptance_criterion
- [x] AC005 -> tests/test_features.py::FeatureBundleTests::test_feature_tests_cli_text_and_json_outputs_ready_bundle
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_feature_tests_cli_text_and_json_outputs_ready_bundle
- [x] AC007 -> tests/test_features.py::FeatureBundleTests::test_feature_tests_cli_output_file_overwrite_force_and_json_output
- [x] AC008 -> tests/test_features.py::FeatureBundleTests::test_feature_tests_cli_reports_partial_bundle_gaps
- [x] AC008 -> tests/test_features.py::FeatureBundleTests::test_feature_tests_cli_missing_bundle_returns_packet_and_nonzero
- [x] AC008 -> tests/test_features.py::FeatureBundleTests::test_feature_tests_cli_invalid_slug_returns_two
- [x] AC009 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_feature_test_packet_documentation_describes_workflow
- [x] AC009 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_feature_test_packet_dogfood_exports_test_cases

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-test-packet . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature tests feature-test-packet . --json`.
- Run the requested repository credential-prefix scan and confirm no token prefixes are present.

## Review Notes

- The command composes existing local reports and peer files; it does not invent feature behavior beyond the deterministic AC-to-TC wrapper.
- Test cases intentionally remain pending checklist items because the packet is context for testing, not proof that tests were run.
- Partial bundles stay exportable so QA agents can see missing quality evidence before asking another agent to repair the bundle.

## Release Readiness

- [x] `feature-test-packet` has complete spec, execution, and quality peer files.
- [x] Lifecycle status is `validated` across all peer files.
- [x] Acceptance criteria, tasks, required checks, test plan, and release readiness evidence are complete.
- [x] Local verification commands for this round pass.
