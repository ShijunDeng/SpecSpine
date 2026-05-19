# AC-to-Test Scaffold Generator

Feature ID: ac-test-scaffold-generator
Status: implemented
Priority: medium
Owner: unassigned
Milestone: unassigned
Target Release: unassigned
Project: unassigned
Effort: unknown

## Why

Generate structured test scaffolds from acceptance criteria to close coverage gaps identified in retrospective. Provides deterministic test scaffolds for humans and AI agents to implement.

## Users

- AI agents that need test scaffolds for uncovered acceptance criteria.
- Maintainers who want deterministic test stubs mapped to ACs before implementation.

## Scope

- Add `specspine scaffold <slug> [path] [--json]` command under the main CLI.
- Parse feature trace to extract acceptance criteria for the given slug.
- Generate test class with one method per uncovered AC, named `test_<ac_id>_<keyword>`.
- Map each AC to a target test file path and class name in the coverage links.
- Produce a remediation plan with actionable steps for each uncovered AC.
- Output stable JSON with feature_id, status, test_methods, coverage_links, skipped_criteria, remediation_plan, and safety_notes.
- Output concise text with method list, skipped criteria, and remediation actions.

## Non-Goals

- Running tests, calling subprocesses, or making network calls.
- Generating fully implemented test methods; all scaffolds contain `self.fail()` placeholders.
- Modifying quality files; test coverage link updates are a separate workflow.

## Acceptance Criteria

- [x] `specspine scaffold <slug> [path] [--json]` generates a scaffold report for a valid feature slug.
- [x] JSON output includes `feature_id`, `status`, `scaffold_file`, `test_methods`, `coverage_links`, `skipped_criteria`, `remediation_plan`, and `safety_notes`.
- [x] Generated test methods are named `test_<ac_id_snake>_<keyword>` where keyword is extracted from AC text.
- [x] Coverage links map each uncovered AC to a target test file path, class name, and method name.
- [x] Already-covered ACs are listed in `skipped_criteria` with reason "Already has completed test coverage link".
- [x] Remediation plan provides actionable steps for each uncovered AC with target path, class, and method.
- [x] Text output lists methods, skipped criteria, and remediation actions with safety notes.
- [x] Invalid slugs return exit code 2 with a clear error.
- [x] Missing feature bundles return exit code 1 with guidance.
- [x] Safety notes confirm scaffold generation is read-only with placeholder-only methods.

## Edge Cases

- Features with no acceptance criteria generate a test class with a single `test_no_criteria` method.
- Features where all ACs are already covered produce an empty test_methods list and list all in skipped_criteria.
- Quality files without a `## Test Coverage` section are handled gracefully without errors.

## Constraints

- Read-only operation: no file writes, subprocess calls, or network access.
- Zero dependencies beyond the existing SpecSpine codebase.

## Traceability Notes

- Implementation: `src/specspine/scaffold.py`
- CLI integration: `src/specspine/cli.py`
- Tests: `tests/test_scaffold.py`
