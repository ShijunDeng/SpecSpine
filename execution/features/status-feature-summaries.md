# Status Feature Summaries Execution

Feature ID: status-feature-summaries
Status: validated
Why: Workspace status needs an optional repository-grounded feature progress view while preserving the compact default startup packet.

## Milestones

- Extend status construction with opt-in feature summary data.
- Extend CLI parsing and rendering without changing default output.
- Update repository and agent guidance.
- Add dogfood evidence and tests for JSON, text, validation, partial bundles, invalid slugs, and template guidance.

## Tasks

- [x] Add `include_feature_summaries` support to workspace status construction.
- [x] Build summaries from `list_feature_bundles` and `build_feature_handoff_report`.
- [x] Add `--feature-summaries` to the `status` CLI.
- [x] Render a compact text section only when summaries are present.
- [x] Preserve `--validate` and `--adapters` behavior with the new flag.
- [x] Handle invalid feature filenames with not-ready summary output.
- [x] Update docs, specs, execution plan, quality review, AGENTS.md, and the AGENTS template.
- [x] Add focused unit and dogfood artifact coverage.
- [x] Run the required validation, status, readiness, unit, and token-prefix checks.

## Dependencies

- Existing native feature bundle discovery.
- Existing compact feature handoff report construction.
- Existing readiness gate and validation summary helpers.

## Open Questions

- Future rounds can decide whether workspace summaries should expose additional lifecycle filters after real multi-feature usage patterns are observed.
