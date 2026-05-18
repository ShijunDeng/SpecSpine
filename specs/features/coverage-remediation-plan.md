# Coverage Remediation Plan

Feature ID: coverage-remediation-plan
Status: validated
Priority: high
Owner: SpecSpine Maintainers
Milestone: workspace quality gates
Target Release: 2026.5
Project: Native feature bundles
Effort: M

## Why

Coverage debt names missing acceptance-criterion ids, but reviewers and agents need a read-only plan that turns those gaps into concrete follow-up without treating coverage links as automatic proof of test quality.

## Acceptance Criteria

- [x] `specspine coverage plan [path] --json` reports actionable remediation items for coverage-required features with missing acceptance criteria.
- [x] Text output summarizes plan counts, item risks, focused commands, and safety notes.
- [x] `--policy` limits plan items to features selected by the workspace readiness policy.
- [x] `--feature SLUG` focuses the plan and summary on one existing feature.
- [x] `--limit N` trims returned items without changing summary totals.
- [x] Missing feature filters return a structured report with exit code 1.
- [x] Invalid feature slugs and negative limits return usage errors with exit code 2.
- [x] The command is local-only, read-only, and does not run subprocesses, call network services, read token variables, or write quality files.

## Notes

- The planner complements `specspine coverage debt` by expanding missing AC ids into reviewer-ready remediation steps.
- The command must keep coverage as a gap signal and avoid claiming tests were run or that quality was proven.
