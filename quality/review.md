# Review Notes

## Current Review Focus

This repository is now being used as a SpecSpine workspace. Reviews should check both code behavior and the project-level artifacts that guide agents.

## Findings

- No current blocking defects recorded in project-level artifacts.
- The generated workspace templates were too generic for dogfooding and have been replaced with repository-specific intent, product, architecture, execution, and quality content.
- Native feature lifecycle status can now be queried, updated, listed in status JSON, and validated across peer files.
- `specspine status --validate` now reports workspace, fusion, and feature validation summaries without becoming a failing gate command.
- `specspine status --validate --validation-warnings` now exposes warning check ids when scaffold placeholder details are needed, while default status validation remains compact.
- `specspine feature tasks` now exports execution checklist items into stable text and JSON task lists for implementation agents.
- `specspine feature task-issues` now exports one local GitHub issue draft per execution task without GitHub API calls, token reads, `gh`, subprocesses, or network access.
- `specspine feature trace` now exports a local traceability handoff that connects acceptance criteria, tasks, required checks, test plan entries, sources, and gaps.
- `specspine feature ready` now evaluates a local per-feature readiness gate with blocking checks and failing exit codes.
- `specspine feature ready --require-coverage` now optionally blocks readiness until every acceptance criterion has checked local test coverage evidence.
- `specspine feature handoff` now exports a compact feature packet that composes status, tasks, trace, readiness, release readiness, next actions, and key commands.
- `specspine status --feature-summaries` now adds optional compact per-feature progress, readiness, gaps, blocking counts, next actions, and local status/readiness/sort controls without changing default status output.
- `specspine status --feature-summaries --feature-require-coverage` now lets summary readiness, blockers, next actions, and `--feature-ready` filters use the same coverage gate as `feature ready --require-coverage`.
- `specspine policy`, `feature ready --policy`, and `status --feature-summaries --feature-policy` now encode optional workspace readiness coverage rules in local machine-readable context.
- `specspine status --readiness-summary` now exposes an opt-in workspace readiness rollup with ready/not-ready counts, compact per-feature readiness records, coverage-required and policy modes, and focused `feature ready` commands without changing default status output.
- `specspine coverage debt` now reports exact workspace AC coverage debt from local native feature bundles, including open coverage links, missing targets, unknown AC links, universal mode, and policy-selected mode.
- `specspine analyze` now reports read-only native feature consistency, traceability, readiness, and coverage findings with feature filtering and opt-in failing issue exits.
- `specspine tests impact` now reports local static source-to-test impact recommendations and optional feature coverage targets without running tests, invoking subprocesses, calling network services, or reading tokens.
- `specspine loop packet` now exports a local, deterministic agent loop packet with root, deadline, core_features, summary, context_commands, lifecycle_steps, subagents, validation_commands, safety_notes, upstreams, and recommended_commands.
- `specspine propose` now turns meaningful natural-language intent into populated native feature bundles with EARS-like acceptance criteria, boundary/dependency-annotated execution tasks, mapped quality checks, dry-run previews, JSON output, metadata flags, conflict protection, and no external calls.
- `specspine feature status --enforce-transition` now provides an opt-in lifecycle policy that blocks out-of-order writes and requires readiness before enforced archive writes while preserving default manual status updates.
- `specspine feature pr` now exports offline Pull Request drafts that compose local feature evidence without GitHub API calls, token reads, `gh`, or network access.
- `specspine feature sync-plan` now exports reviewable GitHub CLI argv plans and optional local artifact directories for feature issues, task issues, and draft PRs without executing `gh`, reading tokens, calling APIs, invoking subprocesses, or using network access.
- `specspine feature archive` now exports durable local archive evidence and optional package artifacts without marking lifecycle status, running tests, invoking subprocesses, calling network services, or reading tokens.
- `specspine feature tests` now exports acceptance-test packets that map acceptance criteria to test cases, attach explicit local `## Test Coverage` links, and surface existing test plan, quality checks, gaps, and blockers without running tests or generating code.
- `specspine feature new` now generates native feature bundles with focused spec, execution, quality, handoff, task issue draft, tests, PR, ready, validation guidance, and initial spec-level priority, owner, milestone, target release, project, and effort metadata instead of broad generic placeholders.
- `specspine gates` now exports repository-level quality gate definitions from `quality/checklist.md` without executing commands, reading tokens, requiring `gh`, or calling network services.
- Repository quality gates can carry optional `[severity: ...]`, `[owner: ...]`, and `[ci: ...]` labels; unlabeled gates keep stable defaults, invalid severities become gate-level warnings, and CI labels are never executed by the exporter.
- `specspine adapters lifecycle` now exports local lifecycle mappings for OpenSpec, Spec Kit, and Superpowers without probing upstream tools, reading tokens, calling GitHub, or using network services.
- `specspine adapters handoff` now exports a feature-specific OpenSpec, Spec Kit, and Superpowers handoff packet and optional per-adapter review artifacts without executing upstream tools, probing adapters, reading tokens, or using network services.
- No upstream code should be copied into this repository as part of fusion work.

## Decisions

- Treat `specspine status . --json` as the first context packet for future agents.
- Use `specspine status . --json --validate` when agents need context and failed quality checks together.
- Add `--validation-warnings` only when agents need warning check details for unchanged scaffold placeholders.
- Use `specspine status . --json --validate --feature-summaries` only when agents need to choose or compare multiple native features, and add `--feature-status`, `--feature-ready`, `--feature-priority`, `--feature-owner`, or `--feature-sort` when the workspace has enough features to need local triage; add `--feature-require-coverage` when all candidates must include checked local AC coverage, or `--feature-policy` when the workspace policy should decide per feature.
- Use `specspine status . --json --readiness-summary` when agents or CI need workspace-wide ready/not-ready feature counts in one packet; add `--readiness-require-coverage` or `--readiness-policy` when coverage gates should be universal or policy-selected.
- Use `specspine coverage debt . --json` when a coverage-required readiness rollup shows not-ready features and agents need exact missing AC coverage evidence; add `--policy` to limit required debt to policy-selected features.
- Use `specspine analyze . --json` before implementation when reviewers or agents need one read-only packet for cross-artifact consistency, AC task references, readiness blockers, and coverage evidence; use `--fail-on-issues` only for CI-style failure behavior.
- Use `specspine tests impact . --json`, optionally with `--changed PATH` and `--feature <slug>`, when agents or reviewers need focused local unittest recommendations without executing the tests.
- Treat `specspine loop packet . --json` as the workspace-level local agent loop packet before delegating implementation, validation, or review work. It does not call GitHub, read or write tokens, invoke subprocesses, probe adapters, or access the network.
- Treat `specspine propose "..." . --json` as the default seed for natural-language feature requests; use `--dry-run` before writing when a reviewer wants to inspect generated artifacts.
- Treat `specspine feature handoff <slug> . --json` as the default local feature packet for implementation, acceptance, and review agents.
- Use `specspine feature tasks <slug> . --json` as the focused execution checklist view when an agent only needs tasks.
- Use `specspine feature task-issues <slug> . --json` when a maintainer or agent needs local task-level issue drafts before any remote GitHub issue exists.
- Treat `specspine feature trace <slug> . --json` as the local traceability handoff when reviewers need a complete feature packet.
- Treat `specspine feature ready <slug> . --json` as the local per-feature acceptance and release gate after implementation evidence is complete; add `--require-coverage` for high-risk or pre-release reviews that require completed local AC coverage links, and add `--policy` when `.specspine/policy.yaml` should decide.
- Treat `specspine policy . --json` as the workspace readiness governance packet; missing files mean defaults, not a validation failure.
- Treat `specspine feature tests <slug> . --json` as the focused local packet for QA and testing agents, and use `## Test Coverage` links in quality files to point AC ids at existing local tests.
- Treat `specspine feature pr <slug> . --json` as the local Pull Request draft bridge after readiness and trace evidence are available.
- Treat `specspine feature sync-plan <slug> . --json` as the local review packet for GitHub CLI sync intent, and `specspine feature sync-plan <slug> . --output-dir .specspine/sync-plan/<slug>` as the local body-file and manifest materialization step before a human runs any remote command.
- Treat `specspine feature archive <slug> . --json` as the local closure packet before lifecycle archiving, and `specspine feature archive <slug> . --output-dir .specspine/archive/<slug>` as the local archive package materialization step.
- Treat feature metadata as local draft context only; milestone, target release, project, and effort are not synced to GitHub Issue Fields or Projects by SpecSpine.
- Treat `specspine gates . --json` as the repository-level quality policy packet before implementation, review, or CI wiring; it exports definitions, metadata, and coverage counts, and does not run checks.
- Treat `specspine adapters lifecycle . --json` as the local adapter lifecycle policy packet before future adapter sync, upstream planning, or remote issue/PR mapping work.
- Treat `specspine adapters handoff <slug> . --json` as the feature-specific adapter packet before handing a native feature to OpenSpec, Spec Kit, or Superpowers workflows; use `--output-dir .specspine/adapter-handoff/<slug>` when separate focused Markdown files and a safety manifest are easier to review.
- Treat `specspine validate . --fusion --features` plus the unit test suite as the local completion gate.
- Treat generated feature templates as the starting workflow contract for new requirements: keep acceptance criteria testable, tasks traceable, quality gates unchecked until evidence exists, and handoff/task-issues/tests/pr/ready commands visible.
- Keep GitHub issue and Pull Request draft generation offline and token-free by default.
- Keep GitHub sync planning and artifact materialization offline and token-free; remote issue/PR creation remains a future explicit workflow, not default behavior.
- Keep test impact reporting advisory and local; recommended commands are not executed by SpecSpine.
- Keep native feature peer files on a consistent allowed lifecycle status.
- Prefer `specspine feature status <slug> . --set STATUS --enforce-transition` when lifecycle order matters; run `specspine feature ready <slug> . --json` and `specspine feature archive <slug> . --json` before archiving.
- Use `--run-upstream` only after explicit user instruction.

## Release Notes

- The repository itself now contains a complete SpecSpine fusion workspace.
- Future feature work should start with native feature bundles under `specs/features/`, `execution/features/`, and `quality/features/`.
- Feature bundles support `proposed`, `planned`, `in-progress`, `implemented`, `validated`, and `archived` statuses.
- Status packets can now include compact validation summaries with failed checks only by default, plus opt-in warning checks through `--validation-warnings`.
- Validation can now warn on unchanged base workspace Markdown scaffold placeholders without failing warning-only workspaces.
- Status packets can now opt into compact feature summaries for multi-feature triage while omitting them by default.
- Feature summary packets can now be filtered by lifecycle status, readiness, priority, and owner, sorted by local summary fields including priority, and rejected with code `2` when summary-only options are used without `--feature-summaries`.
- Feature summary packets can now also be filtered and sorted by milestone, target release, project, and effort, using local normalized metadata and keeping missing/default metadata buckets last for metadata sorts.
- Feature summary readiness can now opt into coverage-required gating without changing default summary fields or text output.
- Workspace readiness policy can now select which features require coverage-required readiness by default, feature id, priority, or status while preserving default command compatibility.
- Workspace status can now opt into a `readiness_summary` rollup that reuses feature readiness gates and reports counts, not-ready features, coverage-required records, policy-selected coverage records, and focused local commands.
- Workspace coverage debt can now be exported as a local report that complements readiness rollups with exact AC gaps and link classifications without running tests or touching GitHub.
- Workspace analysis can now be exported as a local report that combines native feature traceability, readiness blockers, AC-to-task references, coverage link classifications, duplicate AC text, and vague AC wording without writing files or touching external services.
- Test impact packets can now be exported as local static source-to-test graphs with focused unittest recommendations and feature coverage target commands.
- Loop packets can now be exported as local agent startup packets with feature summaries, readiness counts, lifecycle guidance, subagents, validation commands, safety notes, upstream metadata, and recommended commands.
- Natural-language proposal generation can now create native spec, execution, and quality bundles deterministically without network access, subprocesses, token reads, GitHub calls, upstream CLIs, or third-party dependencies.
- Feature execution checklists can now be exported without generation, GitHub credentials, or upstream tool calls.
- Feature bundles can now be exported as deterministic traceability packets without generation, GitHub credentials, or upstream tool calls.
- Feature bundles can now be checked with deterministic readiness gates that fail on missing files, inconsistent statuses, trace gaps, incomplete checklist evidence, missing test plans, or open release readiness items.
- Feature readiness can now opt into `feature.test_coverage`, failing on missing, unchecked, or missing-target AC coverage links without changing default readiness behavior.
- Feature bundles can now be exported as compact handoff packets without generation, GitHub credentials, token reads, network calls, upstream CLIs, or new dependencies.
- Feature lifecycle updates can now opt into transition enforcement and archive readiness guards without changing default manual status updates.
- Feature bundles can now be exported as offline Pull Request drafts with GitHub Markdown checklist evidence and key local commands.
- Feature bundles can now be exported as acceptance-test packets with GitHub Markdown checklist test cases, explicit local coverage links, and existing local quality evidence.
- Repository-level quality checklists can now be exported as stable `GATE###` and `DOD###` definition records with summary counts and recommended local commands.
- Adapter lifecycle mappings can now be exported as stable OpenSpec, Spec Kit, and Superpowers records for every native feature status.
- Adapter feature handoffs can now be exported with selected lifecycle mappings and safe unexecuted upstream step recommendations for one native feature, and can be materialized as local `manifest.json`, `combined.md`, `combined.json`, focused per-adapter Markdown/JSON artifacts, and SHA-256 checksums.
- GitHub CLI sync plans can now be exported as stable local argv arrays with safety flags and notes, then materialized into review-only local body files, manifest, and `commands.sh` before any remote issue or Pull Request is created.
- Feature archive evidence can now be exported as stable local JSON or Markdown and materialized into `README.md`, `archive.json`, and source snapshots before a separate enforced lifecycle archive update.
- New feature bundles now include edge cases, constraints, traceability notes, dependencies, open questions, agent handoff commands, acceptance-test guidance, PR draft guidance, readiness checks, and validation gates from creation time.
