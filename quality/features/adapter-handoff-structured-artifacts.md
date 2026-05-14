# Adapter Handoff Structured Artifacts Quality

Feature ID: adapter-handoff-structured-artifacts
Status: validated
Why: Structured adapter artifact exports are only useful if their JSON shape, checksum metadata, overwrite safety, and offline boundary are covered by tests.

## Required Checks

- [x] Unit tests verify `combined.json` and focused per-adapter JSON files are written with expected content.
- [x] Unit tests verify focused adapter JSON files contain feature evidence, safety flags, summary, recommended commands, and only the selected adapter entry.
- [x] Unit tests verify manifest path keys include existing Markdown paths plus new JSON paths.
- [x] Unit tests verify manifest SHA-256 checksums match artifact file bytes and exclude `manifest.json`.
- [x] Unit tests verify overwrite protection includes the new JSON files and `--force` preserves unknown files.
- [x] Unit tests verify `--json --output-dir` stdout includes artifact paths, artifact directory, checksum algorithm, and checksums.
- [x] Unit tests verify artifact writing does not call subprocesses, network services, adapter probes, upstream CLIs, or token reads.
- [x] Documentation and agent guidance describe structured JSON artifacts and checksums.
- [x] Dogfood readiness passes with default checks.
- [x] Dogfood readiness passes with `--require-coverage`.

## Test Coverage

- [x] AC001 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_output_dir_writes_reviewable_adapter_artifacts
- [x] AC002 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_output_dir_writes_reviewable_adapter_artifacts
- [x] AC003 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_output_dir_writes_reviewable_adapter_artifacts
- [x] AC004 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_output_dir_writes_reviewable_adapter_artifacts
- [x] AC005 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_output_dir_manifest_shape_safety_flags_and_artifact_paths
- [x] AC006 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_output_dir_manifest_shape_safety_flags_and_artifact_paths
- [x] AC007 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_output_dir_overwrite_requires_force_and_preserves_unknown_files
- [x] AC008 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_json_output_dir_stdout_remains_parseable_full_report
- [x] AC009 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_handoff_does_not_call_subprocess_network_probe_or_read_tokens
- [x] AC010 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_adapter_handoff_structured_artifacts_dogfood_bundle_passes_default_and_coverage_gates

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_adapter_handoff`.
- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready adapter-handoff-structured-artifacts . --json --require-coverage`.
- Run the repository token-prefix scan requested for this feature.

## Review Notes

- `manifest.json` intentionally excludes its own checksum to avoid self-referential digest churn.
- JSON artifacts are generated from the already-built adapter handoff report; the writer does not probe adapters or inspect external runtime state.
- Unknown files in artifact directories remain outside command ownership.

## Release Readiness

- [x] Focused adapter handoff tests pass.
- [x] Full unit test suite passes.
- [x] Fused feature validation passes.
- [x] Coverage-required readiness passes.
- [x] Token pattern scan has no matches.
