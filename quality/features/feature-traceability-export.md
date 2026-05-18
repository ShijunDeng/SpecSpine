# Feature Traceability Export Quality

Feature ID: feature-traceability-export
Status: validated
Why: The trace export must be trustworthy as a local handoff for future agents and reviewers.

## Required Checks

- [x] Unit tests cover acceptance criteria parsing, required check parsing, test plan extraction, and reused task parsing behavior.
- [x] CLI tests cover text output, JSON output, missing peer files, all-files-missing return code, and output overwrite protection.
- [x] Dogfood tests assert that `feature-traceability-export` is validated and has no missing trace gaps.
- [x] Documentation describes the command surface and offline boundaries.
- [x] The implementation does not call GitHub APIs, read tokens, call upstream CLIs, or add third-party dependencies.

## Test Coverage

- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_feature_trace_cli_all_files_missing_returns_nonzero
- [x] AC002 -> tests/test_features.py::FeatureBundleTests::test_feature_trace_cli_text_and_json_outputs
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_feature_trace_cli_text_and_json_outputs
- [x] AC004 -> tests/test_features.py::FeatureBundleTests::test_feature_trace_cli_text_and_json_outputs
- [x] AC005 -> tests/test_features.py::FeatureBundleTests::test_feature_trace_cli_output_file_overwrite_force_and_json_output
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_feature_trace_cli_reports_partial_bundle_gaps
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_dogfood_feature_traceability_export_is_validated_and_complete
- [x] AC006 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_feature_traceability_export_dogfood_bundle_passes_default_and_coverage_gates

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine feature trace feature-traceability-export . --json`.
- Run the repository token-prefix scan requested for this round and confirm no credential patterns are present.

## Review Notes

- The trace report intentionally remains extractive and deterministic; it does not infer AC-to-task coverage.
- Text file output is always the human handoff, even when JSON is printed to stdout.

## Release Readiness

- [x] The command is documented.
- [x] The dogfood bundle is complete and validated.
- [x] Required local checks pass.
