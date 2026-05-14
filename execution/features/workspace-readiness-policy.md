# Workspace Readiness Policy Execution

Feature ID: workspace-readiness-policy
Status: validated

## Milestones

- [x] Define a local policy model and dependency-free parser for `.specspine/policy.yaml`.
- [x] Expose policy export through `specspine policy`.
- [x] Wire policy-selected coverage into `feature ready --policy`.
- [x] Wire per-feature policy readiness into status summaries.
- [x] Document the governance file and dogfood it in this repository.

## Tasks

- [x] Add policy loading, defaults, warnings, JSON/text rendering, and coverage selector evaluation.
- [x] Add CLI arguments for `policy`, `feature ready --policy`, and `status --feature-policy`.
- [x] Preserve existing default readiness and status output when policy flags are absent.
- [x] Add tests for missing policy, parser selectors, warnings, readiness policy application, explicit overrides, status option validation, policy filters, compatibility, and dogfood artifacts.
- [x] Add `.specspine/policy.yaml` targeting only `workspace-readiness-policy`.
- [x] Update README, product, architecture, execution, quality, and agent guidance.

## Dependencies

- Existing native feature metadata and readiness parsing.
- Existing Test Coverage link parser for acceptance-criterion coverage checks.

## Open Questions

- None for this release.

## Agent Handoff

- Use `PYTHONPATH=src python3 -m specspine policy . --json` to inspect the effective workspace policy.
- Use `PYTHONPATH=src python3 -m specspine feature ready workspace-readiness-policy . --json --policy` to verify policy-selected coverage readiness.
- Use `PYTHONPATH=src python3 -m specspine status . --json --feature-summaries --feature-policy --feature-ready yes` to verify policy-aware summary filtering.
