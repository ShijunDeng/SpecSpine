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

- [x] AC001 Add status CLI parsing for `--feature-require-coverage`.
- [x] AC002 Include the new flag in summary-only option validation and error text.
- [x] AC003 Allow feature handoff summary construction to reuse `build_feature_ready_report(..., require_coverage=True)`.
- [x] AC004 Add `coverage_required: true` only when coverage-required summaries are requested.
- [x] AC005 Ensure `ready`, `ready_summary`, `blocking_checks`, and `next_actions` reflect coverage blockers.
- [x] AC006 Ensure `--feature-ready` filtering uses the coverage-required result.
- [x] AC007 Add a concise coverage marker to text summaries under the new flag.
- [x] AC008 Add unit and dogfood coverage for compatibility, filters, text, and errors.
- [x] AC009 Update README, product, architecture, execution, quality, and agent guidance.

## Dependencies

- Existing `build_feature_ready_report` coverage-required gate.
- Existing feature handoff summary, task summary, and next-action logic.
- Existing `## Test Coverage` parser and local target existence checks.

## Open Questions

- Should a future workspace policy decide when `--feature-require-coverage` is automatically required by priority, owner, or lifecycle status?
