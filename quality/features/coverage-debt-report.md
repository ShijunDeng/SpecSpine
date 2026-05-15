# Coverage Debt Report Quality

Feature ID: coverage-debt-report
Status: validated

## Required Checks

- [x] JSON output includes stable top-level workspace totals and per-feature coverage debt fields.
- [x] Text output stays concise and shows focused commands for debt features.
- [x] Coverage classification matches `feature ready --require-coverage`: checked local target links cover ACs, unchecked links do not, and missing targets do not.
- [x] Policy mode counts only policy-selected features as coverage-required while still reporting all discovered native features.
- [x] Missing quality files and partial native bundles produce records instead of exceptions.
- [x] The implementation reads local SpecSpine files only and does not execute tests, subprocesses, network calls, GitHub APIs, upstream CLIs, or token providers.
- [x] Documentation explains that the report complements readiness rollups by exposing exact AC coverage gaps.

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_coverage_debt`.
- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine coverage debt . --json`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready coverage-debt-report . --json --require-coverage`.

## Release Readiness

- [x] The command exits 0 when debt exists but the report is built successfully.
- [x] Invalid command usage remains argparse-controlled.
- [x] JSON and text output give agents a direct next command for each debt feature.
- [x] The dogfood bundle passes default and coverage-required readiness gates.

## Test Coverage

- [x] AC001 -> tests/test_coverage_debt.py::CoverageDebtTests::test_json_universal_counts_covered_and_missing_criteria
- [x] AC002 -> tests/test_coverage_debt.py::CoverageDebtTests::test_text_shows_only_features_with_debt_and_commands
- [x] AC003 -> tests/test_coverage_debt.py::CoverageDebtTests::test_feature_with_checked_existing_targets_for_all_criteria_has_no_debt
- [x] AC004 -> tests/test_coverage_debt.py::CoverageDebtTests::test_link_classification_reports_open_missing_target_and_unknown_ac_links
- [x] AC005 -> tests/test_coverage_debt.py::CoverageDebtTests::test_partial_bundle_missing_quality_does_not_crash
- [x] AC006 -> tests/test_coverage_debt.py::CoverageDebtTests::test_policy_mode_limits_required_debt_to_policy_selected_features
- [x] AC007 -> tests/test_coverage_debt.py::CoverageDebtTests::test_coverage_debt_does_not_call_subprocess_network_or_read_tokens
- [x] AC008 -> tests/test_coverage_debt.py::CoverageDebtTests::test_coverage_debt_help_is_available
