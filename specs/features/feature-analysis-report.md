# Feature Analysis Report

Feature ID: feature-analysis-report
Status: validated
Priority: high
Owner: SpecSpine Maintainers
Milestone: workspace quality gates
Target Release: 2026.5
Project: Native feature bundles
Effort: M

## Why

Agents need a read-only workspace analysis command that checks native feature bundles for cross-artifact consistency and coverage gaps before implementation starts.

## Acceptance Criteria

- [x] `specspine analyze [path] [--json] [--feature SLUG]` runs against local native feature bundles and defaults to report-only exit `0`.
- [x] JSON output includes `root`, `feature_filter`, summary feature counts, issue counts by severity and category, per-feature metrics and issues, a flat issue list, and recommended commands.
- [x] Text output stays compact with a summary, issue rows grouped by feature, recommendations, and a success message when no issues are found.
- [x] Analysis detects missing native artifacts, existing readiness blockers, acceptance criteria without task references, acceptance criteria without coverage links, and tasks without AC/test/quality references.
- [x] Analysis classifies Test Coverage links that point to unknown acceptance criteria, checked links whose local target is missing, and open coverage links.
- [x] The command is deterministic, read-only, local-only, and does not invoke subprocesses, probe adapters, read tokens, call remote services, or access the network.
- [x] Focused tests cover JSON shape, text output, feature filtering, issue detection in temporary workspaces, missing or invalid filters, and local-only safety behavior.
- [x] User-facing docs and agent guidance describe when to use the analysis command alongside readiness, coverage debt, and validation commands.

## Notes

- The report complements `specspine feature trace`, `specspine feature ready --require-coverage`, and `specspine coverage debt` by combining high-signal consistency checks into one workspace-level packet.
- `--fail-on-issues` is an optional CI-style mode; without it, detected issues do not make the command fail.
