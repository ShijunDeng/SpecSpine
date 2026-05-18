# Feature Analysis Report Quality

Feature ID: feature-analysis-report
Status: validated

## Required Checks

- [x] JSON output is stable, sorted, and includes workspace summary counts plus deterministic issue ids.
- [x] Text output is readable for humans and remains compact for agent logs.
- [x] Feature filtering analyzes only the requested slug and reports a missing bundle without crashing.
- [x] Issue detection covers artifact, readiness, traceability, coverage, and AC quality findings.
- [x] `--fail-on-issues` is the only mode where detected findings make the command return nonzero.
- [x] Analysis does not write files, run tests, invoke subprocesses, probe adapters, access the network, call GitHub, or read tokens.
- [x] Documentation positions analysis as a read-only pre-implementation consistency and coverage report.

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_analysis`.
- Run `PYTHONPATH=src python3 -m specspine analyze . --json`.
- Run `PYTHONPATH=src python3 -m specspine analyze .`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-analysis-report . --json`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features --json`.

## Release Readiness

- [x] The analysis command is report-only by default and returns `0` when a report is built.
- [x] JSON and text outputs are deterministic enough for agents and CI logs.
- [x] The dogfood bundle passes default and coverage-required feature readiness gates.
- [x] Local-only safety expectations are covered by unit tests and docs.

## Test Coverage

- [x] AC001 -> tests/test_analysis.py::AnalysisCommandTests::test_text_output_is_report_only_and_fail_flag_is_opt_in
- [x] AC002 -> tests/test_analysis.py::AnalysisCommandTests::test_json_shape_and_feature_filter
- [x] AC003 -> tests/test_analysis.py::AnalysisCommandTests::test_text_output_is_report_only_and_fail_flag_is_opt_in
- [x] AC004 -> tests/test_analysis.py::AnalysisCommandTests::test_issue_detection_from_local_artifacts
- [x] AC005 -> tests/test_analysis.py::AnalysisCommandTests::test_issue_detection_from_local_artifacts
- [x] AC006 -> tests/test_analysis.py::AnalysisCommandTests::test_analyze_is_read_only_local_and_does_not_probe_external_services
- [x] AC007 -> tests/test_analysis.py::AnalysisCommandTests::test_missing_feature_filter_reports_issue_without_crashing
- [x] AC007 -> tests/test_analysis.py::AnalysisCommandTests::test_invalid_feature_filter_returns_two
- [x] AC008 -> tests/test_analysis.py
