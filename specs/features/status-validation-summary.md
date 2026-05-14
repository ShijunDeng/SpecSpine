# Status Validation Summary

Feature ID: status-validation-summary
Status: validated

## Why

Agents currently read `specspine status . --json` for compact workspace context, then need a separate `specspine validate` call to learn whether the workspace, fusion layer, and native feature bundles satisfy the local quality gate. That split increases agent round trips and leaves an open product question about exposing richer validation summaries in status JSON.

## Users

- AI coding agents that need context and quality-gate state in one local command.
- Maintainers who want `status` to remain a report command while surfacing validation failures.
- CI or local scripts that want a stable summary without printing every passing validation check.

## Scope

- Add `specspine status [path] [--json] [--adapters] [--validate]`.
- Keep existing `status --json` output compatible when `--validate` is not passed.
- When `--validate` is passed, attach `validation` with `ok`, `summary`, `failed_checks`, and `included`.
- Default status validation to workspace, fusion, and feature checks.
- Run external adapter availability probes only when users pass both `--adapters` and `--validate`.
- Add a short text `Validation` section with result, summary counts, and failed check ids only.
- Keep `status` exit code `0` even when validation failures are reported.

## Non-Goals

- Replacing `specspine validate` as the CI gate command.
- Printing every passing validation check in status text output.
- Probing external commands by default.
- Adding runtime dependencies or network calls.

## Acceptance Criteria

- [x] `status --json` without `--validate` does not include `validation`.
- [x] `status --json --validate` includes `ok`, `summary`, `failed_checks`, and `included`.
- [x] `status --validate` text output includes a concise validation result and summary.
- [x] Failed validation checks appear in `failed_checks` while `status` still returns `0`.
- [x] `--adapters --validate` includes adapter validation only through an explicit probe path.
- [x] The repository dogfood status lists this feature as `validated`.
