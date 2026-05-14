# Feature Traceability Export

Feature ID: feature-traceability-export
Status: validated

## Why

Implementation agents need a single local handoff that connects feature intent, acceptance criteria, execution tasks, quality checks, and test plan evidence. The existing task and issue exports cover pieces of that story, but they do not provide a native traceability packet that answers why the work exists, what must be true, how it is being completed, and how it will be verified.

## Users

- Maintainers coordinating multi-agent implementation rounds.
- Implementation agents that need stable machine-readable feature context.
- Reviewers checking that specs, tasks, and quality evidence remain aligned.

## Scope

- Add `specspine feature trace <slug> [path] [--json] [--output FILE] [--force]`.
- Parse acceptance criteria checklist items from `specs/features/<slug>.md`.
- Parse execution task checklist items from `execution/features/<slug>.md`.
- Parse required quality checklist items and test plan content from `quality/features/<slug>.md`.
- Emit deterministic text and JSON reports without calling upstream CLIs, GitHub APIs, or token sources.
- Report missing peer files and missing trace sections as explicit gaps.

## Non-Goals

- Inferring relationships between acceptance criteria, tasks, checks, and test plan lines.
- Generating new tasks, tests, or acceptance criteria from prose.
- Creating remote GitHub issues or reading credentials.
- Importing third-party Markdown parsers.

## Acceptance Criteria

- [x] `feature trace` returns non-zero when no native feature files exist for the slug.
- [x] JSON output includes `feature_id`, `status`, `sources`, `missing_files`, `acceptance_criteria`, `tasks`, `quality_checks`, `test_plan`, `summary`, and `gaps`.
- [x] Acceptance criteria, tasks, and quality checks use stable source-order IDs with `AC001`, `T001`, and `Q001` prefixes.
- [x] Text output is a concise agent handoff containing sources, counts, gaps, and ordered trace content.
- [x] `--json --output` prints JSON to stdout while writing the text handoff to the output file.
- [x] Partial bundles return zero while reporting missing files and trace gaps.

