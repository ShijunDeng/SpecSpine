# Status Validation Summary Execution

Feature ID: status-validation-summary
Status: validated
Why: Agents need one status packet that can include both workspace context and local quality-gate state.

## Milestones

- Extend the CLI parser with `status --validate`.
- Reuse the existing validation engine without introducing a status-to-validation import cycle.
- Add a compact validation summary shape for status payloads.
- Render a brief text validation section that avoids listing passing checks.
- Cover JSON compatibility, validation summaries, failure reporting, exit code behavior, and adapter probes.
- Dogfood the feature with native SpecSpine artifacts and repository validation.

## Tasks

- [x] AC001 Add `--validate` to the status command.
- [x] AC002 Build status validation summaries from `build_validation_report`.
- [x] AC003 Include workspace, fusion, and feature checks by default.
- [x] AC004 Include adapter availability checks only when `--adapters` is also passed.
- [x] AC005 Preserve the existing no-validation status JSON shape.
- [x] AC006 Keep status command return code `0` for report-only behavior.
- [x] AC006 Update README, architecture docs, agent guidance, execution tasks, and review notes.
- [x] AC006 Add unit tests for JSON, text, failure, mock adapter, and dogfood behavior.

## Dependencies

- Python standard library only.
- Existing `specspine.validation` check records and summary counts.
- Existing status renderer and CLI command dispatch.

## Open Questions

- Whether a future status payload should expose selected warning checks in addition to failed checks.
- Whether downstream agents will prefer a single `status --json --validate` startup command over separate status and validate calls.
