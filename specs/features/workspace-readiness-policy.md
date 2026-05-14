# Workspace Readiness Policy

Feature ID: workspace-readiness-policy
Status: validated
Priority: high
Owner: SpecSpine maintainers

## Why

Coverage-required readiness is already available, but agents and reviewers must remember to pass the stricter flag. A local, auditable policy file lets a workspace encode which features require acceptance-criterion coverage without changing default behavior for older repositories.

## Users

- Agents deciding whether a feature can move through a stricter release gate.
- Maintainers dogfooding coverage-required readiness for selected high-risk features.
- Reviewers auditing project governance from local files.

## Scope

- Add optional `.specspine/policy.yaml` with a dependency-free YAML subset for readiness coverage rules.
- Add `specspine policy [path] [--json]` that reports defaults successfully when the policy file is absent.
- Support `readiness.require_coverage` selectors for `enabled`, `default`, `priorities`, `statuses`, and `feature_ids`.
- Warn, without failing, when policy priorities or statuses are unknown.
- Add `feature ready --policy` so policy-selected features behave like `--require-coverage`.
- Add `status --feature-summaries --feature-policy` so per-feature summaries compute readiness through the policy.
- Keep `--require-coverage` and `--feature-require-coverage` as explicit overrides.
- Preserve default `feature ready` and default `status` compatibility.
- Keep all behavior local-only, with no subprocesses, network calls, token reads, upstream CLIs, or new dependencies.

## Non-Goals

- Requiring coverage for every historical SpecSpine feature by default.
- Executing tests from coverage links.
- Validating arbitrary YAML syntax beyond the documented local subset.
- Making policy files mandatory for workspace validation.

## Acceptance Criteria

- [x] Missing `.specspine/policy.yaml` reports policy defaults with `source_missing: true` and return code `0`.
- [x] The parser handles enabled/default booleans and priority, status, and feature-id lists.
- [x] Unknown priority and status values produce policy warnings without failing the command.
- [x] `feature ready --policy` requires coverage when the feature id, priority, status, or default selector matches.
- [x] Explicit `--require-coverage` still requires coverage even when policy does not.
- [x] `status --feature-policy` is rejected with code `2` unless `--feature-summaries` is present.
- [x] Policy summary mode adds stable policy fields and applies `--feature-ready yes/no` filtering to policy readiness.
- [x] Default `status` and `feature ready` behavior and JSON fields remain compatible.
- [x] This repository includes a policy that targets only `workspace-readiness-policy`.
- [x] This dogfood bundle passes default, `--require-coverage`, and `--policy` readiness.
