# Status Readiness Rollup Execution

Feature ID: status-readiness-rollup
Status: validated
Why: Workspace status should optionally expose feature readiness counts and blockers in one packet so agents and CI can triage without running one command per feature.

## Milestones

- Add status CLI flags for `--readiness-summary`, `--readiness-require-coverage`, and `--readiness-policy`.
- Implement a dedicated readiness rollup builder that reuses `build_feature_ready_report`.
- Preserve default status JSON and text output when the rollup flag is absent.
- Emit compact JSON counts, per-feature records, and recommended focused readiness commands.
- Append concise text output with totals and not-ready feature rows only when requested.
- Validate coverage-required and policy-selected readiness behavior.
- Update docs, agent guidance, product specs, architecture notes, execution plan, and review notes.
- Dogfood the feature with checked local coverage links.

## Tasks

- [x] AC001 Add parser support for `--readiness-summary`.
- [x] AC002 Add parser support for `--readiness-require-coverage` and `--readiness-policy`.
- [x] AC003 Reject readiness-only options without `--readiness-summary` with return code `2`.
- [x] AC004 Build top-level `readiness_summary` only when requested.
- [x] AC005 Reuse `build_feature_ready_report` for every feature readiness decision.
- [x] AC006 Include workspace totals for features, ready/not-ready, blocking checks, gaps, and coverage-required records.
- [x] AC007 Include compact per-feature records with status, readiness, coverage, policy, blocker, gap, missing-file, action, and command fields.
- [x] AC008 Make coverage-required mode require coverage for every feature.
- [x] AC009 Make policy mode load `.specspine/policy.yaml` and report policy-selected coverage counts.
- [x] AC010 Keep default `--feature-summaries` semantics unchanged.
- [x] AC011 Add JSON, text, invalid-option, coverage, policy, and local-only tests.
- [x] AC011 Update README, AGENTS, product, architecture, execution, quality, and docs architecture.

## Dependencies

- Existing feature discovery from `list_feature_bundles`.
- Existing local readiness logic in `build_feature_ready_report`.
- Existing workspace readiness policy parser from `.specspine/policy.yaml`.
- Existing status rendering and JSON rendering code.

## Open Questions

- Resolved: readiness summaries should be available from workspace status as an explicit opt-in rollup, while default status remains compact.
