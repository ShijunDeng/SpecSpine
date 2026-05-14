# Status Validation Warnings Execution

Feature ID: status-validation-warnings
Status: validated

## Summary

The implementation adds local warning checks for generated base workspace Markdown placeholders and exposes their details only when status callers opt in with `--validation-warnings`.

## Tasks

- [x] Add deterministic scaffold placeholder phrase checks for base Markdown workspace files.
- [x] Emit stable `workspace.placeholder:<path>` warning checks with warning severity.
- [x] Preserve validation `ok` and exit code behavior so warning-only reports pass.
- [x] Add `status --validation-warnings` with a code `2` error when used without `--validate`.
- [x] Keep default `status --json --validate` compact by omitting warning details.
- [x] Add JSON and text status warning detail output when the flag is present.
- [x] Update README, architecture docs, product spec, execution plan, tasks, review notes, agent guidance, and generated agent template text.
- [x] Add unit tests for validation warnings, status JSON shape, status text output, flag misuse, and dogfood readiness.

## Validation Commands

- `PYTHONPATH=src python3 -m unittest tests.test_validation tests.test_status tests.test_dogfood_artifacts`
- `PYTHONPATH=src python3 -m specspine validate . --fusion --features`
- `PYTHONPATH=src python3 -m specspine feature ready status-validation-warnings . --json`

## Handoff Notes

- Warning checks are local-only and do not probe adapters unless the caller already requested adapter validation.
- The status summary shape stays backward compatible unless `--validation-warnings` is explicitly provided with `--validate`.
- No network, GitHub token, subprocess, upstream CLI, or dependency behavior is introduced.
