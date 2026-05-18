# Feature Retrospective & Self-Improvement

Feature ID: feature-retrospective
Status: validated
Priority: high
Owner: SpecSpine maintainers
Milestone: continuous-improvement
Target Release: 2026.5
Project: Native feature bundles
Effort: M

## Why

SpecSpine now has many validated dogfood feature bundles. Agents can inspect one feature at a time, but there is no single local retrospective report that summarizes delivery quality, recurring blockers, coverage gaps, stale proposed work, and follow-up actions across completed feature work. A deterministic retrospective closes the SDD loop: specs define intent, implementation creates evidence, and the repository can learn from completed work before the next iteration starts.

## Users

- Maintainers who need a compact local review of feature delivery health before choosing the next iteration.
- AI coding agents that need evidence-based follow-up actions instead of relying on chat history.
- Reviewers who want to see repeated quality gaps, open tasks, and not-ready features without opening every feature file.

## Scope

- Add `specspine retrospective report [path] [--json] [--feature SLUG] [--limit N]`.
- Summarize native feature bundles using existing local status, readiness, trace, task, test, coverage, and release-readiness evidence.
- Emit stable JSON and readable text with `root`, `feature_filter`, `features`, `themes`, `summary`, `recommendations`, `recommended_commands`, and `safety_notes`.
- Rank follow-up recommendations so not-ready features, open tasks, blockers, gaps, and missing coverage rise above already-ready feature bundles.
- Update generated templates, agent instructions, project docs, and dogfood tests so retrospective reporting becomes part of the continuous iteration workflow.

## Non-Goals

- The retrospective does not call Git, inspect commit timestamps, infer deployment data, or compute DORA metrics.
- The report does not modify feature bundles, mark tasks complete, archive features, or generate new requirements automatically.
- The report does not use AI summarization, network services, upstream tools, remote APIs, environment variables, or tokens.

## Acceptance Criteria

- [x] AC001: The CLI exposes `specspine retrospective report [path] [--json] [--feature SLUG] [--limit N]` and emits stable text and JSON with `root`, `feature_filter`, `features`, `themes`, `summary`, `recommendations`, `recommended_commands`, and `safety_notes`.
- [x] AC002: The report includes one record per scanned native feature with feature id, status, ready flag, priority, owner, task counts, readiness counts, gap count, blocking checks, coverage state, source files, and recommended local commands.
- [x] AC003: `--feature SLUG` limits the report to one valid feature, missing bundles return a structured report with exit code `1`, and invalid slugs return code `2`.
- [x] AC004: `--limit N` limits recommendation rows deterministically while preserving complete summary counts; invalid limits return code `2`.
- [x] AC005: Themes aggregate recurring statuses, blockers, gaps, open tasks, missing coverage, and release-readiness issues across scanned features.
- [x] AC006: Recommendations are ranked by not-ready state, blocking checks, gaps, open tasks, missing coverage, status age bucket, and slug so the next action list is deterministic.
- [x] AC007: The command is read-only and local: it does not write files, run tests, invoke subprocesses, call network services, call GitHub, invoke upstream CLIs, read environment variables, or read tokens.
- [x] AC008: Generated feature templates and agent instructions include `specspine retrospective report . --json` as a pre-planning or post-review command.
- [x] AC009: README, architecture, product, execution, and quality docs describe the retrospective workflow, JSON fields, limit behavior, and safety boundary.
- [x] AC010: The `feature-retrospective` dogfood bundle is validated, has checked local coverage links, and passes default and coverage-required readiness gates.

## Edge Cases

- Workspaces with no native feature bundles return an empty report with summary counts and conservative commands.
- Partial feature bundles remain reportable and surface missing files or readiness blockers.
- Invalid feature slugs fail before scanning unrelated features.
- Limit `0` is allowed and returns no recommendation rows while preserving summary and theme counts.
- Older feature specs without metadata use stable defaults from existing feature metadata parsing.

## Constraints

- Reuse existing feature parsing, readiness, trace, tests, and metadata helpers where practical.
- Keep the command zero-dependency and deterministic.
- Keep all recommended commands advisory and explicitly unexecuted.
- Keep output stable enough for tests and downstream agents.

## Traceability Notes

- Implementation: `src/specspine/retrospective.py` and `src/specspine/cli.py`.
- Tests: `tests/test_retrospective.py`, `tests/test_agents.py`, `tests/test_features.py`, and `tests/test_dogfood_artifacts.py`.
- Documentation: `README.md`, `docs/architecture.md`, `specs/product.md`, `specs/architecture.md`, `execution/plan.md`, and `quality/review.md`.
