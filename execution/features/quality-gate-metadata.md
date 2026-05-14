# Quality Gate Metadata Execution

Feature ID: quality-gate-metadata
Status: validated
Why: `specspine gates --json` should expose auditable gate metadata without changing the local, extractive command boundary.

## Milestones

- Extend the repository quality gate parser with lightweight inline metadata labels.
- Preserve existing JSON and text output semantics while appending stable metadata fields.
- Add summary metadata coverage counts.
- Document the label syntax and non-executing boundary.
- Dogfood the feature with ready and coverage-ready native artifacts.

## Tasks

- [x] Implement case-insensitive parsing for severity, owner, and CI labels.
- [x] Add stable default metadata values for unlabeled gates.
- [x] Strip recognized labels from exported gate text while preserving raw text.
- [x] Add non-failing warnings for unsupported severity labels.
- [x] Extend quality gate summary counts for severity distribution, owners, and CI checks.
- [x] Update compact text output to show metadata.
- [x] Add unit tests for defaults, parsing, warnings, summary counts, text output, missing source, and dogfood artifacts.
- [x] Update README, product, architecture, execution, quality, checklist, and agent guidance.
- [x] Run unit tests, repository validation, gates JSON export, and coverage-required feature readiness.

## Dependencies

- Existing `specspine gates` parser and renderers.
- Existing native feature readiness and coverage link parsing.
- Existing repository dogfood validation tests.

## Open Questions

- Whether a future remote sync should map `ci_check` directly to GitHub branch-protection required checks.
- Whether owners should later support a configured role registry.

## Agent Handoff

- Run `specspine gates . --json` to inspect gate metadata.
- Run `specspine feature ready quality-gate-metadata . --json`.
- Run `specspine feature ready quality-gate-metadata . --json --require-coverage`.
- Run `specspine feature tests quality-gate-metadata . --json`.
- Run `specspine validate . --fusion --features`.
