# Status Validation Warnings Quality

Feature ID: status-validation-warnings
Status: validated

## Required Checks

- [x] Fresh initialized workspace validation reports placeholder warnings without failing.
- [x] Warning checks are excluded from default status validation summaries.
- [x] Opt-in JSON status includes warning check dictionaries and uses an empty array when there are no warnings.
- [x] Opt-in text status lists warning check ids under `Warning checks:`.
- [x] `--validation-warnings` without `--validate` returns code `2`.
- [x] Documentation and agent guidance describe the compact default and warning-detail opt-in.

## Test Plan

- Run focused validation and status unit tests.
- Run dogfood artifact tests for the repository feature bundle.
- Run repository validation with fusion and feature checks enabled.

## Review Notes

- The feature keeps warning details out of default status payloads to preserve compact startup context.
- The validation engine already counted warnings separately, so the implementation only adds local checks and opt-in summary transport.
- No GitHub token reads, API calls, network access, upstream CLI calls, subprocess calls, or dependency additions are part of the change.

## Release Readiness

- [x] Validation warnings do not block `validate` when no failures exist.
- [x] Default status JSON remains compact and compatible.
- [x] Warning detail output is explicitly gated by `--validate --validation-warnings`.
- [x] The dogfood feature bundle is validated and ready.
