# Quality Gate Definitions Quality

Feature ID: quality-gate-definitions
Status: validated
Why: Repository-level quality policy affects completion decisions, so the exported gate definitions must be deterministic, local, and explicitly non-executing.

## Required Checks

- [x] Unit tests verify initialized workspace JSON parsing from `quality/checklist.md`.
- [x] Unit tests verify text output includes summary counts and stable gate ids.
- [x] Unit tests verify missing source behavior returns code `1` and reports empty lists.
- [x] Unit tests verify only `## Required Checks` and `## Definition Of Done` are parsed.
- [x] Unit tests verify nested same-named headings such as `### Required Checks` are ignored.
- [x] Unit tests verify the command reads only `quality/checklist.md` and does not call subprocesses or fake `gh`.
- [x] JSON recommended commands include local validation and status validation commands.
- [x] Documentation describes the new command, output shape, return codes, and offline boundaries.
- [x] Dogfood validation verifies this bundle has consistent `validated` lifecycle status.
- [x] Dogfood readiness verifies this bundle passes the local feature gate.
- [x] Token-prefix scanning verifies no GitHub token was added.

## Test Coverage

- [x] AC001 -> tests/test_gates.py::QualityGateTests::test_gates_json_parses_initialized_workspace_quality_checklist
- [x] AC006 -> tests/test_gates.py::QualityGateTests::test_gates_text_includes_summary_and_ids
- [x] AC007 -> tests/test_gates.py::QualityGateTests::test_gates_source_missing_returns_one_with_empty_json_lists
- [x] AC008 -> tests/test_gates.py::QualityGateTests::test_gates_only_parse_required_checks_and_definition_of_done
- [x] AC008 -> tests/test_gates.py::QualityGateTests::test_gates_ignore_nested_same_named_headings
- [x] AC009 -> tests/test_gates.py::QualityGateTests::test_gates_reads_only_quality_checklist_and_skips_external_tools

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features --json`.
- Run `PYTHONPATH=src python3 -m specspine gates . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready quality-gate-definitions . --json`.
- Run `git diff --check`.
- Run the repository GitHub token-prefix scan and confirm it produces no matches.

## Review Notes

- The command exports definitions only; open required checks are data, not command failures.
- The parser is section-bounded and does not infer gates from other Markdown lists.
- Missing `quality/checklist.md` is represented as a stable report with a non-zero exit code.
- No GitHub API, `gh`, network, token, subprocess, upstream CLI, dependency, or command-execution path is introduced.

## Release Readiness

- [x] `specspine gates . --json` works for this repository.
- [x] Missing-source JSON and text output are clear.
- [x] Unit tests and repository validation pass.
- [x] Documentation and agent guidance include the local gate-definition workflow.
- [x] The dogfood bundle is ready and validated.
