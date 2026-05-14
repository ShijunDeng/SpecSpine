# Status Coverage Readiness Summaries Execution

Feature ID: status-coverage-readiness-summaries
Status: validated
Why: Status summaries need an opt-in coverage-required readiness mode so agents can select release candidates using the same strict gate as focused feature readiness.

## Milestones

- Add the `--feature-require-coverage` CLI option under `specspine status`.
- Gate the option behind `--feature-summaries` with code `2` validation.
- Thread coverage-required readiness through feature summary construction.
- Preserve default summary JSON fields, readiness counts, filtering, sorting, and text output.
- Add tests for JSON/text output, invalid option use, coverage-aware filtering, and dogfood readiness.
- Update command documentation and agent workflow guidance.
- Dogfood the feature with checked local coverage links.

## Tasks

- [x] Add status CLI parsing for `--feature-require-coverage`.
- [x] Include the new flag in summary-only option validation and error text.
- [x] Allow feature handoff summary construction to reuse `build_feature_ready_report(..., require_coverage=True)`.
- [x] Add `coverage_required: true` only when coverage-required summaries are requested.
- [x] Ensure `ready`, `ready_summary`, `blocking_checks`, and `next_actions` reflect coverage blockers.
- [x] Ensure `--feature-ready` filtering uses the coverage-required result.
- [x] Add a concise coverage marker to text summaries under the new flag.
- [x] Add unit and dogfood coverage for compatibility, filters, text, and errors.
- [x] Update README, product, architecture, execution, quality, and agent guidance.

## Dependencies

- Existing `build_feature_ready_report` coverage-required gate.
- Existing feature handoff summary, task summary, and next-action logic.
- Existing `## Test Coverage` parser and local target existence checks.

## Open Questions

- Should a future workspace policy decide when `--feature-require-coverage` is automatically required by priority, owner, or lifecycle status?
