# Status Validation Warnings

Feature ID: status-validation-warnings
Status: validated

## Why

Workspace status validation should surface local scaffold cleanup work without turning a newly initialized workspace into a failed validation gate. Agents need warning detail when they ask for it, while the default status packet should remain compact and compatible.

## Goals

- Detect base workspace Markdown files that still contain generated scaffold prompts.
- Represent scaffold findings as validation warnings, not failures.
- Keep `validate` success and exit code driven only by failing checks.
- Keep `status --json --validate` focused on failed checks unless warning details are explicitly requested.
- Provide text and JSON status surfaces for warning details through `--validation-warnings`.

## Non-Goals

- Checking `.specspine/spine.yaml`, `.gitkeep`, feature bundle templates, upstream files, or external services for placeholder content.
- Calling GitHub APIs, reading tokens, invoking upstream CLIs, using network access, or adding dependencies.
- Making warning checks block readiness or validation exit code.

## Acceptance Criteria

- [x] Fresh `specspine init` workspaces produce stable `workspace.placeholder:<path>` warning checks for unchanged base Markdown scaffold content.
- [x] Warning checks use `status=warn` and `severity=warning`.
- [x] `specspine validate` returns zero when only warning checks are present.
- [x] `status --json --validate` omits `warning_checks` by default and continues to include `failed_checks`.
- [x] `status --json --validate --validation-warnings` includes `validation.warning_checks` as the list of warning check dictionaries, or an empty array when none exist.
- [x] `status --validate --validation-warnings` shows warning check ids under `Warning checks:`, while default text status validation does not.
- [x] `status --validation-warnings` without `--validate` returns code `2` with a clear local CLI error.

## Edge Cases

- Missing workspace Markdown files are still reported by required-file failures; placeholder checks are skipped for missing or unreadable files.
- A workspace can contain both failures and warnings; `ok` remains false only when failures exist.
- Rewritten project-specific workspace files should not produce placeholder warnings.

## Traceability

- Validation behavior is implemented in `src/specspine/validation.py`.
- Status CLI and text rendering are implemented in `src/specspine/cli.py` and `src/specspine/status.py`.
- CLI behavior is covered by `tests/test_validation.py` and `tests/test_status.py`.
