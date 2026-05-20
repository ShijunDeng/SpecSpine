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

- [x] AC001 Add policy loading, defaults, warnings, JSON/text rendering, and coverage selector evaluation.
- [x] AC002 Add CLI arguments for `policy`, `feature ready --policy`, and `status --feature-policy`.
- [x] AC003 Preserve existing default readiness and status output when policy flags are absent.
- [x] AC004 Add tests for missing policy, parser selectors, warnings, readiness policy application, explicit overrides, status option validation, policy filters, compatibility, and dogfood artifacts.
- [x] AC005 Add `.specspine/policy.yaml` targeting only `workspace-readiness-policy`.
- [x] AC006 Update README, product, architecture, execution, quality, and agent guidance.
- [x] AC007 Add policy summary mode with stable policy fields and `--feature-ready yes/no` filtering for policy readiness.
- [x] AC008 Preserve default `status` and `feature ready` behavior and JSON field compatibility when policy flags are absent.
- [x] AC009 Add `.specspine/policy.yaml` targeting only `workspace-readiness-policy` in this repository.
- [x] AC010 Validate this dogfood bundle passes default, `--require-coverage`, and `--policy` readiness gates.

## Dependencies

- Existing native feature metadata and readiness parsing.
- Existing Test Coverage link parser for acceptance-criterion coverage checks.

## Open Questions

- None for this release.

## Agent Handoff

- Use `PYTHONPATH=src python3 -m specspine policy . --json` to inspect the effective workspace policy.
- Use `PYTHONPATH=src python3 -m specspine feature ready workspace-readiness-policy . --json --policy` to verify policy-selected coverage readiness.
- Use `PYTHONPATH=src python3 -m specspine status . --json --feature-summaries --feature-policy --feature-ready yes` to verify policy-aware summary filtering.
