# Status Validation Summary Quality

Feature ID: status-validation-summary
Status: validated
Why: Status validation summaries affect the agent context packet and must not turn `status` into a failing gate command.

## Required Checks

- [x] `status --json` without `--validate` omits `validation`.
- [x] `status --json --validate` includes `ok`, `summary`, `failed_checks`, and `included`.
- [x] `status --validate` text output includes result and summary counts.
- [x] Failed checks include stable `id`, `message`, `severity`, and `status` fields.
- [x] `status --validate` returns `0` even when validation reports failures.
- [x] Adapter availability checks run only when `--adapters --validate` is explicit and can be tested with a mock probe.
- [x] The repository status JSON lists this feature as `validated`.
- [x] Token-prefix scan does not find GitHub secret patterns.

## Test Coverage

- [x] AC001 -> tests/test_status.py::StatusTests::test_status_json_cli_output_is_parseable
- [x] AC002 -> tests/test_status.py::StatusTests::test_status_json_cli_validate_includes_validation_summary
- [x] AC003 -> tests/test_status.py::StatusTests::test_status_text_cli_validate_includes_brief_summary
- [x] AC004 -> tests/test_status.py::StatusTests::test_status_validate_reports_failed_checks_but_returns_zero
- [x] AC005 -> tests/test_status.py::StatusTests::test_status_validate_with_adapters_uses_mock_probe
- [x] AC006 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_status_validation_summary_dogfood_bundle_passes_default_and_coverage_gates

## Test Plan

- `PYTHONPATH=src python3 -m unittest discover -s tests`
- `PYTHONPATH=src python3 -m specspine status . --json --validate`
- `PYTHONPATH=src python3 -m specspine validate . --fusion --features`
- Repository token-prefix scan for GitHub secret patterns.

## Review Notes

- The implementation keeps validation detail generation in `specspine.validation` and attaches the summary from the CLI layer, avoiding a `status` to `validation` import cycle.
- The summary deliberately includes failed checks only, so status text remains compact and does not duplicate the full validate output.
- External adapter checks remain opt-in behind `--adapters` to avoid default environment probes.

## Release Readiness

- [x] CLI behavior is covered by unit tests.
- [x] Documentation describes the new command shape and report-only exit behavior.
- [x] Dogfood artifacts are present and traceable by `Feature ID`.
