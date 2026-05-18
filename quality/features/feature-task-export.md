# Feature Task Export Quality

Feature ID: feature-task-export
Status: validated
Why: Task export becomes an agent execution input, so ordering, line numbers, and empty-state behavior must be deterministic.

## Required Checks

- [x] Parser extracts ordered checkbox tasks with stable ids, done flags, source file, and line numbers.
- [x] JSON output includes the required top-level fields and deterministic summary counts.
- [x] Text output stays short and directly executable by an agent.
- [x] Missing execution files in partial bundles produce empty tasks with explicit source-missing metadata.
- [x] All missing feature files return non-zero.
- [x] Output file overwrite protection and `--force` behavior are tested.
- [x] `--json --output` prints JSON to stdout and writes text to the file.
- [x] No GitHub token, `gh`, API, or upstream tool is required.
- [x] This dogfood bundle exports tasks through the new command and is validated.

## Test Coverage

- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_parse_feature_tasks_preserves_order_lines_and_done_flags
- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_parse_feature_tasks_keeps_lower_heading_tasks_and_markdown_text
- [x] AC002 -> tests/test_features.py::FeatureBundleTests::test_feature_tasks_cli_text_and_json_outputs
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_feature_tasks_cli_text_and_json_outputs
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_build_feature_tasks_report_matches_summary
- [x] AC004 -> tests/test_features.py::FeatureBundleTests::test_feature_tasks_cli_reports_no_tasks_found
- [x] AC004 -> tests/test_features.py::FeatureBundleTests::test_feature_tasks_cli_handles_missing_execution_partial_bundle
- [x] AC004 -> tests/test_features.py::FeatureBundleTests::test_feature_tasks_cli_text_reports_missing_execution_source
- [x] AC005 -> tests/test_features.py::FeatureBundleTests::test_feature_tasks_cli_all_files_missing_returns_nonzero
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_feature_tasks_cli_output_file_overwrite_force_and_json_output
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_feature_tasks_cli_output_creates_missing_parent_directories
- [x] AC007 -> tests/test_features.py::FeatureBundleTests::test_feature_tasks_cli_all_files_missing_does_not_call_gh_or_leak_tokens
- [x] AC007 -> tests/test_features.py::FeatureBundleTests::test_feature_tasks_cli_does_not_require_gh_or_github_tokens
- [x] AC007 -> tests/test_features.py::FeatureBundleTests::test_dogfood_feature_task_export_is_validated_and_exports_tasks
- [x] AC007 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_feature_task_export_dogfood_bundle_passes_default_and_coverage_gates

## Test Plan

- `PYTHONPATH=src python3 -m unittest discover -s tests`
- `PYTHONPATH=src python3 -m specspine feature tasks feature-task-export . --json`
- `PYTHONPATH=src python3 -m specspine status . --json --validate`
- `PYTHONPATH=src python3 -m specspine validate . --fusion --features`
- Repository token-prefix scan for GitHub secret patterns.

## Review Notes

- The implementation is intentionally non-generative: it only exports checklist items already written in the execution artifact.
- Partial bundle handling matches the local-file workflow by allowing spec and quality files to exist before execution details are available.
- The command follows issue export output semantics so scripts can combine JSON stdout with a text file handoff.

## Release Readiness

- [x] CLI and parser behavior are covered by unit tests.
- [x] Dogfood artifacts are present and traceable by `Feature ID`.
- [x] Documentation describes command behavior and missing-source semantics.
