# Quality Gate Metadata Quality

Feature ID: quality-gate-metadata
Status: validated
Why: Gate metadata changes the machine-readable quality contract, so tests and docs must prove compatibility, parsing, warnings, summaries, and local-only behavior.

## Required Checks

- [x] Unit tests cover unlabeled gates and stable default metadata.
- [x] Unit tests cover multi-label parsing, label stripping, raw text, and case-insensitive keys.
- [x] Unit tests cover unsupported severity warnings without command failure.
- [x] Unit tests cover severity distribution and metadata coverage summary counts.
- [x] Unit tests cover compact text metadata output.
- [x] Unit tests cover missing-source metadata summary stability.
- [x] Dogfood tests cover the native feature bundle and coverage-required readiness.
- [x] Documentation describes syntax, defaults, warning behavior, summary fields, and the non-executing boundary.

## Test Coverage

- [x] AC001 -> tests/test_gates.py::QualityGateTests::test_gates_json_parses_initialized_workspace_quality_checklist
- [x] AC002 -> tests/test_gates.py::QualityGateTests::test_gates_parse_metadata_tags_case_insensitively_and_strip_text
- [x] AC003 -> tests/test_gates.py::QualityGateTests::test_gates_parse_metadata_tags_case_insensitively_and_strip_text
- [x] AC004 -> tests/test_gates.py::QualityGateTests::test_gates_invalid_severity_warns_and_keeps_medium
- [x] AC005 -> tests/test_gates.py::QualityGateTests::test_gates_summary_counts_metadata_coverage
- [x] AC006 -> tests/test_gates.py::QualityGateTests::test_gates_text_includes_explicit_metadata
- [x] AC007 -> tests/test_gates.py::QualityGateTests::test_gates_source_missing_returns_one_with_empty_json_lists
- [x] AC008 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_quality_gate_metadata_dogfood_bundle_passes_default_and_coverage_gates

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine gates . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready quality-gate-metadata . --json --require-coverage`.

## Review Notes

- Metadata labels are parsed only from repository-level `quality/checklist.md` required checks.
- Invalid severity values are warnings attached to the gate record, not command failures.
- `ci_check` is exported as a label only; SpecSpine does not run it.

## Release Readiness

- [x] Backward-compatible JSON fields remain present.
- [x] Metadata labels are documented and tested.
- [x] Local validation and feature readiness pass.
- [x] Coverage-required readiness passes through existing local test links.
