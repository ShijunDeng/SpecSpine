# Adapter Handoff Artifacts Quality

Feature ID: adapter-handoff-artifacts
Status: validated
Why: Artifact export is only trustworthy if it is deterministic, reviewable, overwrite-safe, and proven not to execute or probe external systems.

## Required Checks

- [x] Unit tests verify output-dir artifact files exist and contain expected adapter-specific content.
- [x] Unit tests verify manifest JSON shape, safety flags, and artifact paths.
- [x] Unit tests verify no overwrite without `--force`, unknown file preservation, and force overwrite of managed files.
- [x] Unit tests verify `--json --output-dir` stdout remains parseable full report JSON.
- [x] Unit tests verify `--output` compatibility with `--output-dir`.
- [x] Unit tests preserve invalid slug and missing bundle behavior.
- [x] Unit tests verify artifact writing does not call subprocesses, network services, adapter probes, or token reads.
- [x] Documentation and agent guidance describe the artifact export workflow and safety boundary.
- [x] Dogfood readiness passes with default checks.
- [x] Dogfood readiness passes with `--require-coverage`.

## Test Coverage

- [x] AC001 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_output_dir_writes_reviewable_adapter_artifacts
- [x] AC002 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_output_dir_writes_reviewable_adapter_artifacts
- [x] AC003 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_output_dir_manifest_shape_safety_flags_and_artifact_paths
- [x] AC004 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_output_dir_overwrite_requires_force_and_preserves_unknown_files
- [x] AC005 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_output_dir_overwrite_requires_force_and_preserves_unknown_files
- [x] AC006 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_json_output_dir_stdout_remains_parseable_full_report
- [x] AC007 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_output_file_and_output_dir_can_be_used_together
- [x] AC008 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_missing_bundle_and_invalid_slug_exit_codes
- [x] AC009 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_handoff_does_not_call_subprocess_network_probe_or_read_tokens
- [x] AC010 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_adapter_handoff_artifacts_dogfood_bundle_passes_default_and_coverage_gates

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_adapter_handoff`.
- Run `PYTHONPATH=src python3 -m unittest tests.test_dogfood_artifacts`.
- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine adapters handoff adapter-handoff-artifacts . --output-dir .specspine/adapter-handoff-artifacts-test --force --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready adapter-handoff-artifacts . --json --require-coverage`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.

## Review Notes

- The artifact writer consumes the already-built adapter handoff report and writes local files only.
- The manifest repeats explicit false safety flags so artifact consumers do not infer execution.
- Unknown files in the output directory are left untouched.

## Release Readiness

- [x] Focused adapter artifact tests pass.
- [x] Full unit test suite passes.
- [x] Fused feature validation passes.
- [x] Artifact export dogfood command writes reviewable files.
- [x] Default and coverage-required readiness gates pass.
