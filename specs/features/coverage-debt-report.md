# Coverage Debt Report

Feature ID: coverage-debt-report
Status: validated
Priority: high
Owner: SpecSpine Maintainers
Milestone: workspace quality gates
Target Release: 2026.5
Project: Native feature bundles
Effort: M

## Why

Agents can see that workspace readiness fails under coverage-required gates, but they need a focused local report that names the exact feature and acceptance-criterion coverage gaps without running tests or touching remote systems.

## Acceptance Criteria

- [x] `specspine coverage debt [path] --json` reports universal coverage debt for all native feature bundles.
- [x] Text output summarizes totals and lists only features with coverage debt by default.
- [x] Features whose acceptance criteria all have checked local coverage links to existing targets report no debt.
- [x] Open coverage links, checked links with missing local targets, and links to unknown acceptance criteria are classified separately.
- [x] Partial bundles and missing quality files are reported without crashing.
- [x] `--policy` mode limits required coverage debt to features selected by `.specspine/policy.yaml` and exposes policy fields.
- [x] The command is local-only and does not run subprocesses, call network services, read GitHub tokens, or invoke upstream tools.
- [x] CLI help exposes `specspine coverage debt` with stable command usage.

## Notes

- The report complements `specspine status --readiness-summary --readiness-require-coverage` by turning workspace not-ready counts into actionable AC-level coverage gaps.
- A criterion is covered only when a checked `## Test Coverage` link references that AC id and the target path exists locally, matching `feature ready --require-coverage`.
