# SpecSpine Architecture

SpecSpine is organized around a single idea: every implementation step should be traceable to an explicit spec artifact.

## Backbone

The backbone is represented by `.specspine/spine.yaml`. It records where the current workspace keeps its main artifacts:

- Intent documents.
- Product and feature specs.
- Architecture notes.
- Execution plans and tasks.
- Quality checklists and review notes.
- Optional adapters for external tools.

## CLI

The CLI is intentionally thin:

- `specspine init` creates the default workspace structure.
- `specspine agents init` creates project-local `AGENTS.md` instructions for AI coding agents.
- `specspine feature new` creates a traceable native feature bundle.
- `specspine feature status` reads or updates native feature lifecycle state.
- `specspine feature tasks` exports execution checklist items as stable agent tasks.
- `specspine feature task-issues` exports one local GitHub issue draft per execution task.
- `specspine feature trace` exports a feature bundle traceability handoff.
- `specspine feature ready` evaluates a feature bundle as a local pass/fail readiness gate.
- `specspine feature handoff` exports a compact feature packet for implementation, acceptance, and review agents.
- `specspine feature tests` exports an acceptance-test packet for QA and testing agents.
- `specspine feature issue` exports a local GitHub issue draft from a native feature bundle.
- `specspine feature pr` exports a local GitHub Pull Request draft from a native feature bundle.
- `specspine feature sync-plan` exports a local GitHub CLI synchronization plan and optional review artifacts without executing it.
- `specspine fuse` creates the OpenSpec + Spec Kit + Superpowers fusion layer.
- `specspine doctor` checks whether expected files exist.
- `specspine status` emits a compact status packet for humans, agents, and scripts.
- `specspine gates` exports repository-level quality gate definitions from `quality/checklist.md`.
- `specspine validate` turns workspace and fusion contracts into executable checks for CI and agents.
- `specspine adapters doctor` checks whether external tools are installed.
- `specspine adapters install-hints` prints upstream install guidance.
- `specspine adapters lifecycle` exports static local mappings from SpecSpine lifecycle status to upstream adapter phases.
- `specspine adapters handoff` exports a feature-specific adapter handoff packet without executing upstream tools.

Future commands should remain thin orchestration layers over explicit files so the workspace stays understandable without a server.

`specspine status --json` is the preferred machine-readable context boundary. It reports:

- workspace and fusion completeness.
- core artifact existence.
- native feature status and peer-file consistency.
- enabled upstream adapters.
- recommended next actions.
- optional external adapter availability when `--adapters` is passed.

`specspine status --json --validate` adds a compact `validation` object to that context packet. The summary includes:

- whether validation is ok.
- summary counts for `pass`, `fail`, `warn`, `skip`, and `total`.
- failed checks with stable `id`, `message`, `severity`, and `status` fields.
- an `included` map showing whether workspace, fusion, feature, and adapter checks were included.

Status validation checks workspace, fusion, and native feature bundles by default. It runs external adapter availability probes only when `--adapters` is also passed. The command is still a report command and returns `0`; CI gates should continue to use `specspine validate`.

`specspine status --json --validate --validation-warnings` adds `validation.warning_checks` with warning check dictionaries. Text status with the same flag lists warning ids under `Warning checks:`. The warning flag is rejected with code `2` unless `--validate` is also present, and the default `status --json --validate` payload omits warning details to stay compact.

`specspine validate --json` is the preferred machine-readable quality gate. It reports:

- the resolved workspace root.
- whether validation is ok.
- stable check records with `id`, `status`, `message`, and `severity`.
- summary counts for `pass`, `fail`, `warn`, and `skip`.

Validation is local-first and zero-dependency. The default mode validates base workspace files only. `--fusion` requires the fusion layer and enforces adapter-mode/no-vendored-code boundaries. `--adapters` probes external upstream adapters only when explicitly requested.

Workspace validation also checks base Markdown workspace files for scaffold placeholders from `specspine init`, such as product scope prompts, execution task prompts, quality gate prompts, and review-note prompts. These checks use stable `workspace.placeholder:<path>` ids with `status=warn` and `severity=warning`; they do not affect `ok` or exit code unless another check fails.

`specspine feature new <slug> [path]` creates three peer files that start the spec -> execution -> quality workflow:

- `specs/features/<slug>.md` for intent, users, scope, non-goals, acceptance criteria, edge cases, constraints, and traceability notes.
- `execution/features/<slug>.md` for milestones, tasks, dependencies, open questions, and focused agent handoff commands.
- `quality/features/<slug>.md` for required checks, test plan, review notes, sync-plan review, and release readiness gates.

Each file records the same `Feature ID: <slug>` and starts at `Status: proposed`. The spec peer also starts with `Priority: medium` and `Owner: unassigned`; those two local fields are the source of truth for workspace feature-summary triage and are not repeated in execution or quality peers. The generated quality checklists stay unchecked so a new bundle validates as structurally complete but does not pass `specspine feature ready` until implementation, tests, docs or PR draft, `feature ready`, and `validate . --fusion --features` evidence are complete. The command refuses to overwrite existing feature files unless `--force` is passed.

Native feature lifecycle states are:

- `proposed`
- `planned`
- `in-progress`
- `implemented`
- `validated`
- `archived`

`specspine feature status <slug> [path] [--set STATUS] [--enforce-transition] [--json]` reads or updates those peer-file status lines. Without `--set`, it reports the current status and marks mixed peer files as inconsistent. With `--set`, the default path remains a manual file-native update to any supported status and fails clearly if no feature files exist.

`--enforce-transition` is an opt-in lifecycle policy for agents, reviewers, and CI jobs that want ordered transitions without changing the default command behavior. It rejects writes when the current peer status is missing, mixed, inconsistent, or unsupported. The ordered graph is `proposed -> planned|archived`, `planned -> in-progress|archived`, `in-progress -> implemented|planned|archived`, `implemented -> validated|in-progress|archived`, `validated -> archived|implemented`, with `archived` terminal. When the target status is `archived`, the command first runs the same local readiness gate as `specspine feature ready` and writes only if that gate is ready.

Status JSON includes `feature_id`, `status`, `consistent`, `files`, and `missing_files`; update JSON also includes `updated_files` and a `transition` object. Enforced transition failures return code `1`, do not write files, and produce stable JSON error payloads with transition context plus readiness blockers when archive is blocked.

`specspine feature tasks <slug> [path] [--json] [--output FILE] [--force]` reads the `## Tasks` section from `execution/features/<slug>.md` and exports only Markdown checklist items. The parser keeps the source order and emits flat task records with `id`, `text`, `done`, `source_file`, and `line`. JSON output includes `feature_id`, `status`, `source_file`, `source_missing`, `tasks`, `summary`, and `missing_files`.

Task export is local and non-generative. It does not infer tasks from prose, call upstream tools, call GitHub, read tokens, or require `gh`. If the execution file exists but contains no checklist items, the command returns an empty list with a clear no-tasks message. If spec or quality files exist while execution is missing, the command still returns an empty list and marks `source_missing=true`; if all feature files are missing, it returns non-zero.

`specspine feature trace <slug> [path] [--json] [--output FILE] [--force]` reads the native feature bundle and exports an ordered trace packet:

- `AC001` acceptance criteria from `specs/features/<slug>.md` under `## Acceptance Criteria`.
- `T001` tasks from `execution/features/<slug>.md` under `## Tasks`, using the same checklist behavior as `feature tasks`.
- `Q001` required checks from `quality/features/<slug>.md` under `## Required Checks`.
- `TP001` test plan lines from non-empty content under `## Test Plan`.

The trace report includes `feature_id`, `status`, `sources`, `missing_files`, ordered trace sections, `summary`, and `gaps`. It is extractive and deterministic: it does not infer coverage, call GitHub, call upstream CLIs, read tokens, or require dependencies beyond the Python standard library. Partial bundles return zero with missing file and missing section gaps; all-files-missing returns non-zero. `--output` writes the text handoff with overwrite protection, while `--json --output` keeps stdout as JSON and writes text to the file.

`specspine feature ready <slug> [path] [--json]` turns the trace evidence and release checklist into a failing per-feature quality gate. It checks:

- all three native peer files exist.
- peer-file lifecycle status is consistent.
- lifecycle status is `implemented` or `validated`.
- trace gaps are empty.
- acceptance criteria, tasks, required checks, and `## Release Readiness` checklist items exist and are all checked.
- `## Test Plan` has non-empty content.

The readiness report includes `feature_id`, `ready`, `status`, stable `checks`, `blocking_checks`, `summary`, `missing_files`, and `gaps`. It is local and deterministic, and does not execute the test plan or call external services. Ready returns `0`; not-ready and missing bundles return `1`; invalid slugs return `2`.

`specspine adapters handoff <slug> [path] [--json] [--output FILE] [--force]` composes the existing native feature handoff with the adapter lifecycle mapping selected for the feature's current status. The packet includes feature id, status, readiness, source files, missing files, gaps, blockers, adapter config state, upstream phase, upstream artifacts, agent focus, local commands, notes, and recommended upstream steps. Recommended upstream steps are plan data only: OpenSpec uses argv arrays, Spec Kit and Superpowers use agent instructions, and every step is marked not executed, not safe to auto-run, no remote creation, no network, and no token requirement. Partial bundles return `0`; missing bundles return `1`; invalid slugs return `2`.

`specspine feature handoff <slug> [path] [--json] [--output FILE] [--force]` composes the existing local feature status, trace, tasks, readiness, and release readiness evidence into one minimal packet for agents. JSON output includes `feature_id`, `status`, `ready`, `sources`, `missing_files`, `gaps`, `blocking_checks`, `summary`, `acceptance_criteria`, `tasks`, `quality_checks`, `test_plan`, `release_readiness`, `recommended_commands`, and `next_actions`. Its recommended commands match the generated execution template's focused `handoff`, `tasks`, `task-issues`, `trace`, `tests`, `ready`, `pr`, and `validate . --fusion --features` workflow.

The handoff summary preserves the focused report counts: trace total/done/open, ready pass/fail/total, tasks total/done/open, gap count, and blocking check count. Next actions are deterministic and ordered: create or restore missing bundles, add missing peer files or sections, complete open tasks, resolve blocking checks, then review/merge/archive ready bundles. Missing bundles return `1` with a packet; invalid slugs return `2`; partial bundles return `0`. Output behavior matches other feature exporters: `--output` writes text with overwrite protection, and `--json --output` prints JSON while writing text to the file.

`specspine feature tests <slug> [path] [--json] [--output FILE] [--force]` composes a QA-focused acceptance-test packet from the local feature handoff, trace, readiness, status, source-file evidence, and optional `## Test Coverage` links in the quality peer file. It does not execute tests, generate test code, infer implementation files, call upstream CLIs, call GitHub, access the network, read tokens, or require dependencies beyond the Python standard library.

The tests report includes `feature_id`, `status`, `ready`, `source_files`, `missing_files`, `gaps`, `blocking_checks`, `acceptance_criteria`, `test_plan`, `test_coverage`, `test_cases`, `quality_checks`, `summary`, and `recommended_commands`. Test coverage links are parsed from checklist rows like `- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_name`; target existence is checked only against the local workspace path before any `::` selector. Test cases are deterministic: one acceptance criterion becomes one test case, so `TC001` maps to `AC001` and carries the AC text, source file, line, linked coverage, and an explicit behavior-to-test statement. Test case status is `covered`, `planned`, or `pending` based on linked coverage state. Text output uses GitHub Markdown checklist items for test cases and also includes Test Coverage, existing test plan lines, quality checks, gaps, blocking checks, and key local commands. Partial bundles return `0`; all-files-missing returns `1`; invalid slugs return `2`; output file semantics match the other local exporters.

`specspine status <path> --feature-summaries` is an opt-in workspace view for comparing native features. The default status payload intentionally stays compact for agent startup and does not include per-feature task or readiness detail. With the flag, `status` reuses `list_feature_bundles`, reads `Priority:` and `Owner:` from `specs/features/<slug>.md`, and uses the existing feature handoff report to add `feature_summaries` with lifecycle status, priority, owner, completeness, readiness, missing files, task summary counts, ready summary counts, gap count, blocking check count, next actions, and recommended local commands. Missing or invalid priorities are reported as `unknown`; missing or blank owners are reported as `unassigned`. Text status adds only a short Feature summaries section. Invalid feature filenames produce not-ready summary records instead of crashing workspace status.

Feature summary triage stays local to the already-built summaries. `--feature-status` filters by lifecycle status and can be repeated, including abnormal `invalid` and `unknown` buckets. `--feature-ready` filters by readiness aliases. `--feature-priority` filters by `high`, `medium`, `low`, or `unknown`, and `--feature-owner` performs repeated case-insensitive exact owner matches where `unassigned` includes missing owners. `--feature-sort` orders by `slug`, `status`, `ready`, `gaps`, `blocking`, `tasks-open`, or `priority`; priority sort uses `high -> medium -> low -> unknown`, with `--feature-sort-desc` reversing the selected order. These options are rejected with code `2` unless `--feature-summaries` is present, so callers do not accidentally think the compact default status was filtered.

`specspine gates [path] [--json]` is the repository-level quality policy packet. It reads only `quality/checklist.md` and exports definitions without executing tests, validation, shell commands, upstream CLIs, GitHub APIs, network requests, `gh`, or token reads. The parser is intentionally section-bounded:

- `GATE001` required checks come from checkbox items under `## Required Checks`.
- `DOD001` Definition Of Done items come from bullet items under `## Definition Of Done`.

The JSON report includes `root`, `source_file`, `source_missing`, `required_checks`, `definition_of_done`, `summary`, and `recommended_commands`. Missing sources return code `1` with empty lists; existing sources return code `0` even when gate checkboxes are open because this command exports definitions rather than evaluating completion.

`specspine adapters lifecycle [path] [--json]` is the adapter lifecycle policy packet. It exports static local mappings for OpenSpec, Spec Kit, and Superpowers without probing tools, running shell commands, reading tokens, calling GitHub APIs, or using network access. It reads `.specspine/fusion.yaml` only to determine adapter enablement and configured adapter contract paths, then checks whether those local config paths exist.

The JSON report includes `root`, `native_statuses`, `adapters`, `summary`, and `recommended_commands`. Each adapter record includes `display_name`, `enabled`, `config`, `config_exists`, `upstream_url`, and six mappings. Each mapping includes `id`, `status`, `specspine_meaning`, `upstream_phase`, `upstream_artifacts`, `agent_focus`, and `local_commands`. Disabled adapters and missing config files never make this command fail; they are reported as data while the command returns `0`.

`specspine feature task-issues <slug> [path] [--json] [--output FILE] [--force]` composes the existing local task and trace evidence into a GitHub Markdown issue draft package without creating remote issues. One execution checklist item becomes one issue draft with a stable title, task metadata, source line, acceptance criteria context, and key local commands.

The report includes `feature_id`, `status`, `source_file`, `source_missing`, `missing_files`, `issues`, `summary`, and `recommended_commands`. Each issue includes `title`, `body`, `feature_id`, `task_id`, `task_text`, `task_done`, `source_file`, and `line`. The command is extractive and deterministic: it does not call GitHub APIs, require `gh`, read tokens, use network access, invoke upstream CLIs, vendor code, or add dependencies. Partial bundles with missing execution files return zero when another peer file exists; all-files-missing returns non-zero; invalid slugs return `2`; output semantics match the other feature exporters.

`specspine feature issue <slug> [path]` is the local bridge from native feature bundles to GitHub issue workflows. It reads the spec, execution, and quality peer files and builds a structured issue draft with:

- title from the spec file's first-line H1, falling back to slug title case.
- body sections for Feature ID, Status, Why, Acceptance Criteria, Tasks, Test Plan, Source Files, and Missing Files.
- stable JSON output through `--json`.
- body file export through `--output`, with overwrite protection unless `--force` is passed.

The command is intentionally offline. It does not call GitHub APIs, does not require `gh`, and does not read tokens. Missing peer files are reported in the draft; if all three feature files are missing, the command fails clearly.

`specspine feature pr <slug> [path] [--json] [--output FILE] [--force]` is the local bridge from native feature bundles to GitHub Pull Request workflows and Spec Kit PR Bridge-style review artifacts. It composes the existing local status, handoff, trace, readiness, release readiness, and source-file evidence into a PR title plus body without creating a remote PR.

JSON output includes `title`, `body`, `feature_id`, `status`, `ready`, `source_files`, `missing_files`, `gaps`, `blocking_checks`, `summary`, and `recommended_commands`. Text output includes Summary, Feature, Why, Acceptance Criteria, Tasks, Test Plan, Release Readiness, Readiness / Blocking Checks, Source Files, Missing Files, and Key Commands. Reviewable evidence uses GitHub Markdown checklist syntax where the source evidence is a checklist. Partial bundles return `0` with missing files and blockers recorded; all-files-missing returns non-zero; invalid slugs return `2`. Output behavior matches the other local exporters.

The command is intentionally offline. It does not call GitHub APIs, does not require `gh`, does not read tokens, does not use network access, and does not vendor upstream project code.

`specspine feature sync-plan <slug> [path] [--json] [--output FILE] [--output-dir DIR] [--force]` is the local review bridge before any GitHub CLI execution. It composes existing feature issue, task issue, Pull Request, metadata, status, readiness, gap, and blocker evidence into a plan of argv arrays. The command never executes `gh`, calls GitHub APIs, reads tokens, uses network access, invokes subprocesses, invokes upstream CLIs, or adds dependencies.

The sync plan JSON includes `feature_id`, `status`, `ready`, `source_files`, `missing_files`, `gaps`, `blocking_checks`, `metadata`, `summary`, `commands`, `notes`, and `recommended_commands`. Commands include stable ids, `kind` values of `issue`, `task-issue`, or `pull-request`, body source references, draft body content, argv arrays, and safety flags. Every command is marked `creates_remote=true`, `requires_token=true`, `requires_network=true`, and `safe_to_auto_run=false`; text output adds shell-quoted command lines for human review only. GitHub priority is represented as a label for compatibility, project scope is only noted, PR dry-run mode is deliberately not used as a safety guarantee, and local `Owner:` metadata is not automatically mapped to assignees.

`--output-dir` materializes the plan into local review files: `manifest.json`, `feature-issue.md`, `task-issues/T001.md` style task bodies, `pull-request.md`, and `commands.sh`. The manifest preserves the sync-plan JSON shape and adds artifact path indexes plus `body_file` / `artifact_path` fields for each command. `commands.sh` contains comments and shell-quoted `gh ... --body-file <local artifact>` commands only; it is not chmodded or executed. Existing command-owned artifact files require `--force` to overwrite, and unknown files in the directory are preserved.

`specspine validate --features` checks that discovered native feature bundles have valid slugs, all three peer files, matching feature ids, allowed status markers, and consistent peer-file status.

`specspine agents init [path]` writes a short `AGENTS.md` file for Codex, Claude, Gemini, and similar coding agents. The file is a human-readable entry point, not a new source of truth. It points agents back to `specspine status . --json`, `specspine validate .`, native feature bundles, and the external-adapter boundary for OpenSpec, Spec Kit, and Superpowers. The command refuses to overwrite an existing `AGENTS.md` unless `--force` is passed.

## Adapter Direction

Adapters should be optional. SpecSpine should be usable as plain files first, then integrate with tools such as OpenSpec, Spec Kit, Superpowers, GitHub issues, and pull requests.

The expected adapter boundary:

```text
SpecSpine files <-> adapter <-> external tool
```

Adapters should not own the source of truth unless the user explicitly chooses that mode.

The adapter lifecycle map and GitHub sync plan are local contracts for future sync work. They align SpecSpine's native statuses with OpenSpec change artifacts, Spec Kit's spec -> plan -> tasks -> implement workflow, Superpowers' brainstorming, planning, TDD, subagent, review, and completion discipline, and GitHub issue/PR intent before any adapter writes remote or upstream state.

## Fusion Layer

`specspine fuse` writes:

- `.specspine/fusion.yaml` for machine-readable adapter mapping.
- `.specspine/fusion-map.md` for human-readable responsibility mapping.
- `.specspine/adapters/*.md` for per-upstream contracts.
- `quality/superpowers.md` for the project-local Superpowers quality policy.

The fusion layer records `vendored_upstream_code: false`. Upstream tools are invoked through public CLIs or installed agent plugins.

## Modules

- `specspine.workspace`: local file templates and workspace checks.
- `specspine.agents`: project-local `AGENTS.md` generation for AI coding agents.
- `specspine.features`: native feature slug/status validation, bundle templates, file creation, discovery, lifecycle status updates, task export, task issue draft export, trace export, readiness gate evaluation, handoff packet export, issue draft export, PR draft export, GitHub sync plan export, and sync-plan artifact materialization.
- `specspine.adapters`: upstream metadata, availability probes, lifecycle mappings, agent mappings, and initializer command construction.
- `specspine.fusion`: fusion file generation and workspace initialization.
- `specspine.status`: compact workspace, fusion, artifact, upstream, recommendation, optional validation summary, and optional feature summary rendering.
- `specspine.validation`: executable workspace, scaffold-placeholder warning, fusion, feature, optional adapter contract checks, and compact validation summaries.
- `specspine.cli`: command-line interface.
