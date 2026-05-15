# Status Readiness Rollup

Feature ID: status-readiness-rollup
Status: validated
Priority: high
Owner: SpecSpine maintainers
Project: Native feature bundles
Effort: M

## Why

Agents and CI can validate one feature with `specspine feature ready`, but workspace triage still requires opening each feature separately to know which bundles are ready. Status needs an opt-in rollup so a single local packet can show ready and not-ready feature readiness without changing the compact default status contract.

## Users

- Coding agents selecting the next feature to implement, review, or archive.
- CI jobs that need deterministic feature readiness counts in one JSON packet.
- Maintainers reviewing workspace readiness across many native feature bundles.

## Scope

- Add `specspine status [path] --readiness-summary`.
- Keep default text status and default `status --json` unchanged unless the new flag is present.
- Add a top-level JSON `readiness_summary` containing workspace counts, compact per-feature readiness records, and commands for not-ready feature details.
- Reuse `build_feature_ready_report` for readiness decisions.
- Add `--readiness-require-coverage` to force every feature through the coverage-required readiness gate.
- Add `--readiness-policy` to use `.specspine/policy.yaml` when deciding per-feature coverage requirements.
- Make explicit coverage mode override policy selection so every feature requires coverage when both are present.
- Reject `--readiness-require-coverage` and `--readiness-policy` without `--readiness-summary` with return code `2`.
- Append a short text section only when `--readiness-summary` is requested.
- Keep the command local-only: no tests executed, subprocess calls, network calls, token reads, upstream CLIs, or new dependencies.

## Non-Goals

- Making workspace readiness rollups part of default status output.
- Replacing focused `specspine feature ready <slug>` detail reports.
- Running tests, validating selectors, calling CI, or inferring implementation coverage.
- Changing existing `--feature-summaries` filters or field semantics.

## Acceptance Criteria

- [x] Default `specspine status --json` and default text status omit readiness rollup fields and sections.
- [x] `specspine status --readiness-summary --json` emits `readiness_summary` with `features_total`, `ready`, `not_ready`, `blocking_checks_total`, `gaps_total`, `coverage_required_total`, compact `features`, and rollup `recommended_commands`.
- [x] Each compact feature record includes `feature_id`, `status`, `ready`, `coverage_required`, `policy_coverage_required`, `blocking_checks`, `gaps`, `missing_files`, `next_actions`, and `recommended_commands`.
- [x] Not-ready feature records include a command such as `specspine feature ready <slug> . --json` for focused inspection.
- [x] `--readiness-require-coverage` changes readiness counts through the same coverage gate as `feature ready --require-coverage` and marks all feature records with `coverage_required=true`.
- [x] `--readiness-policy` loads `.specspine/policy.yaml`, includes policy fields and policy-selected coverage counts, and uses policy-selected coverage requirements per feature.
- [x] `--readiness-require-coverage` overrides policy selection by requiring coverage for every feature when both flags are present.
- [x] Text status appends a short Readiness summary section only when requested and lists not-ready features.
- [x] `--readiness-require-coverage` or `--readiness-policy` without `--readiness-summary` returns code `2`.
- [x] The rollup remains deterministic and local-only without subprocesses, network access, token reads, upstream CLIs, or new dependencies.
- [x] This dogfood bundle passes default and coverage-required readiness gates with checked local coverage links.
