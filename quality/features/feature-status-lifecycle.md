# Feature Status Lifecycle Quality

Feature ID: feature-status-lifecycle
Status: validated
Why: Status changes affect CLI behavior, validation gates, and machine-readable agent context.

## Required Checks

- [x] Querying status as JSON includes `feature_id`, `status`, `consistent`, `files`, and `missing_files`.
- [x] Setting status as JSON also includes `updated_files`.
- [x] Invalid status and slug inputs use return code `2`.
- [x] Partial bundles preserve missing file reporting and update existing peer files.
- [x] `validate --features` accepts every allowed status.
- [x] `validate --features` fails invalid or mixed statuses.
- [x] `specspine status . --json` includes this dogfood feature as consistent and validated.
- [x] Token-prefix scan does not find GitHub secret patterns.

## Test Plan

- `PYTHONPATH=src python3 -m unittest discover -s tests`
- `PYTHONPATH=src python3 -m specspine status . --json`
- `PYTHONPATH=src python3 -m specspine validate . --fusion --features`
- Repository token-prefix scan for GitHub secret patterns.

## Review Notes

- The implementation keeps lifecycle state in the peer Markdown files instead of adding a sidecar index.
- JSON output is built from local file reads only and does not touch environment tokens or network APIs.
- Status consistency is a validation failure so agents cannot accidentally treat divergent peer files as a ready feature.

## Release Readiness

- [x] CLI behavior is covered by unit tests.
- [x] Validation and status JSON behavior are covered by unit tests.
- [x] Documentation and dogfood artifacts are aligned with the implemented lifecycle states.
