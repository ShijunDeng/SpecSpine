# SpecSpine

SpecSpine is a spec-driven AI development hub. It connects why to build, what to build, and how to finish with quality into one reliable engineering backbone.

中文定位：

> 规范驱动的 AI 开发中枢，把“为什么做、做什么、如何高质量完成”串成一条可靠主干。

## Why SpecSpine

AI-assisted development is strongest when the team can keep intent, scope, implementation, and quality in the same loop. SpecSpine is designed to make that loop explicit.

It borrows the strengths of spec-first tools and high-quality execution workflows:

- **Intent first**: clarify the problem, users, constraints, and success signals.
- **Spec as backbone**: turn intent into product scope, feature specs, and technical decisions.
- **Execution with discipline**: break specs into traceable plans, tasks, checks, and handoffs.
- **Quality by default**: keep acceptance criteria, tests, review notes, and release readiness visible.

## Current Status

This repository is an early project skeleton. It includes:

- A zero-dependency Python CLI.
- A workspace initializer: `specspine init`.
- A project-local agent instruction initializer: `specspine agents init`.
- A native feature bundle creator: `specspine feature new`.
- A native feature lifecycle status command: `specspine feature status`.
- A native feature task exporter: `specspine feature tasks`.
- A native feature traceability exporter: `specspine feature trace`.
- A native feature readiness gate: `specspine feature ready`.
- A native feature handoff packet exporter: `specspine feature handoff`.
- A native feature acceptance-test packet exporter: `specspine feature tests`.
- A local GitHub issue draft exporter: `specspine feature issue`.
- A local GitHub Pull Request draft exporter: `specspine feature pr`.
- A fusion initializer: `specspine fuse`.
- A compact workspace status packet with optional validation and filterable feature summaries: `specspine status --json --validate --feature-summaries`.
- An executable validation layer: `specspine validate --json`.
- Adapter metadata for OpenSpec, Spec Kit, and Superpowers.
- Default templates for intent, product, architecture, feature workflow bundles, quality, and execution.
- A lightweight test suite and GitHub Actions CI.

## Install Locally

Use a virtual environment for a reproducible development install:

```bash
python3 -m venv .venv && . .venv/bin/activate && python -m pip install -e . && specspine --help
```

If you are already inside a disposable Python environment, install directly:

```bash
python3 -m pip install -e .
```

Then run:

```bash
specspine --help
```

You can also run the CLI without installation:

```bash
python3 -m specspine --help
```

## Quick Start

Create a SpecSpine workspace in an existing product repository:

```bash
specspine init .
```

Create project-local instructions for AI coding agents:

```bash
specspine agents init .
```

Create a traceable feature bundle:

```bash
specspine feature new add-dark-mode . --title "Add dark mode" --why "Reduce eye strain"
```

New feature bundles start with focused spec -> execution -> quality guidance: goals and non-goals, acceptance criteria that can become tests, edge cases, constraints, dependencies, open questions, agent handoff commands, required checks, explicit test coverage links, test plan, PR draft, readiness, and validation gates.

Export the compact implementation/review handoff packet:

```bash
specspine feature handoff add-dark-mode .
specspine feature handoff add-dark-mode . --json
```

Export implementation tasks from the feature execution file:

```bash
specspine feature tasks add-dark-mode .
specspine feature tasks add-dark-mode . --json
```

Export a full traceability handoff from the feature bundle:

```bash
specspine feature trace add-dark-mode .
specspine feature trace add-dark-mode . --json
```

Export the acceptance-test packet for QA or testing agents:

```bash
specspine feature tests add-dark-mode .
specspine feature tests add-dark-mode . --json
```

Check whether the feature is ready for review or release:

```bash
specspine feature ready add-dark-mode .
specspine feature ready add-dark-mode . --json
```

Draft a local GitHub issue from the feature bundle:

```bash
specspine feature issue add-dark-mode .
specspine feature issue add-dark-mode . --json
```

Draft a local GitHub Pull Request from the feature bundle:

```bash
specspine feature pr add-dark-mode .
specspine feature pr add-dark-mode . --json
```

Advance the feature lifecycle when the bundle moves forward:

```bash
specspine feature status add-dark-mode . --set planned
specspine feature status add-dark-mode . --set planned --enforce-transition
specspine feature status add-dark-mode . --json
```

Create the full OpenSpec + Spec Kit + Superpowers fusion layer:

```bash
specspine fuse . --agent codex
```

This writes SpecSpine's own backbone and adapter contracts without running external tools. To also invoke the upstream tools through their official command surfaces:

```bash
specspine fuse . --agent codex --run-upstream
```

Summarize the workspace for humans or downstream agents:

```bash
specspine status .
specspine status . --json
specspine status . --json --validate
specspine status . --json --validate --feature-summaries --feature-status validated --feature-ready yes --feature-sort slug
```

Validate workspace and fusion contracts for CI or agents:

```bash
specspine validate .
specspine validate . --fusion --json
```

Or create one in a new directory:

```bash
specspine init ./my-product
```

The fusion command creates:

```text
.specspine/
  spine.yaml
  fusion.yaml
  fusion-map.md
  adapters/
specs/
  intent.md
  product.md
  architecture.md
  features/
execution/
  plan.md
  tasks.md
quality/
  checklist.md
  review.md
  superpowers.md
```

A native feature bundle adds matching files under `specs/features/`, `execution/features/`, and `quality/features/`. Each file carries the same `Feature ID: <slug>` and starts at `Status: proposed`. Supported lifecycle statuses are `proposed`, `planned`, `in-progress`, `implemented`, `validated`, and `archived`.

## Upstream Integration

SpecSpine integrates upstream tools as open source software dependencies and plugins. It does not copy their source code into this repository.

| Tool | Role | Integration Surface |
| --- | --- | --- |
| [OpenSpec](https://github.com/Fission-AI/OpenSpec) | Lightweight change proposals, spec deltas, design, tasks, validation, archive flow | External `openspec` CLI |
| [Spec Kit](https://github.com/github/spec-kit) | Intent-first spec, implementation plan, tasks, and agent command files | External `specify` CLI |
| [Superpowers](https://github.com/obra/superpowers) | Brainstorming, planning discipline, TDD, subagent execution, review, verification | Installed agent plugin/extension |

Install hints:

```bash
# OpenSpec
npm install -g @fission-ai/openspec@latest

# Spec Kit
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@vX.Y.Z
```

Superpowers is installed through your AI coding agent's plugin/extension system.

Check local adapter availability:

```bash
specspine adapters doctor
```

## Core Workflow

1. **Intent**
   - Why are we doing this?
   - Who is it for?
   - What outcome proves it worked?

2. **Spec**
   - What exactly should be built?
   - What is out of scope?
   - What constraints shape the solution?

3. **Plan**
   - How will the work be decomposed?
   - What decisions need to be made?
   - What risks need active handling?

4. **Execute**
   - What tasks are being worked?
   - What artifacts prove progress?
   - What changed from the original plan?

5. **Quality**
   - What tests and reviews are required?
   - What acceptance criteria must pass?
   - What is needed before release?

## CLI

```bash
specspine init [path]
```

Initializes the SpecSpine workspace structure.

```bash
specspine agents init [path] [--force]
```

Creates `AGENTS.md` in the target workspace with concise instructions for Codex, Claude, Gemini, and similar coding agents. The file tells agents to read `specspine status . --json --validate` first, add `--feature-summaries` and optional local feature filters only when comparing multiple native features, validate before and after edits, use native feature bundles for new requirements, keep OpenSpec/Spec Kit/Superpowers as external adapters, avoid GitHub tokens/API calls by default, and only use `--run-upstream` when explicitly requested. Existing files are not overwritten unless `--force` is passed.

```bash
specspine doctor [path]
```

Checks whether a directory contains the expected SpecSpine files.

```bash
specspine feature new <slug> [path] [--title TITLE] [--why WHY] [--force]
```

Creates a native feature bundle:

- `specs/features/<slug>.md`
- `execution/features/<slug>.md`
- `quality/features/<slug>.md`

The slug may contain lowercase letters, numbers, and hyphens, and must start and end with a letter or number. Existing feature files are not overwritten unless `--force` is passed.

```bash
specspine feature status <slug> [path] [--set STATUS] [--enforce-transition] [--json]
```

Reads or updates the lifecycle status for a native feature bundle. Without `--set`, the command reports the current peer-file status and clearly marks mixed or inconsistent files. With `--set`, the default behavior remains manual and compatible: it updates existing peer files to any supported status and returns non-zero if no feature files exist. Invalid slugs and invalid statuses return code `2`.

`--enforce-transition` is opt-in. When passed with `--set`, SpecSpine rejects missing, mixed, inconsistent, or invalid current peer status before writing; allows only `proposed -> planned|archived`, `planned -> in-progress|archived`, `in-progress -> implemented|planned|archived`, `implemented -> validated|in-progress|archived`, `validated -> archived|implemented`; and treats `archived` as terminal. Enforced archive updates also require `specspine feature ready <slug> [path]` to pass before files are written, so incomplete bundles remain unarchived even when the lifecycle edge itself exists.

`--json` emits stable JSON with `feature_id`, `status`, `consistent`, `files`, and `missing_files`; status updates also include `updated_files` and a `transition` object with `from`, `to`, `enforced`, and `allowed`. Enforced failures return code `1` without writing files and emit an error payload with `feature_id`, `error`, `transition`, and, when relevant, `blocking_checks`, `gaps`, or `missing_files`.

```bash
specspine feature tasks <slug> [path] [--json] [--output FILE] [--force]
```

Exports Markdown checklist items from `execution/features/<slug>.md` under `## Tasks`. Supported item forms are `- [ ] task`, `- [x] task`, `* [ ] task`, and `* [x] task`. Text output is a short agent handoff with feature id, status, source, summary, and ordered task list. `--json` emits stable JSON with `feature_id`, `status`, `source_file`, `source_missing`, `tasks`, `summary`, and `missing_files`; each task includes `id`, `text`, `done`, `source_file`, and `line`.

If the execution file exists but has no checklist items, the command returns an empty task list and says no tasks were found. If spec or quality files exist but the execution file is missing, the command still returns `0` with empty tasks, `source_missing=true`, and the missing execution file recorded. If no native feature files exist for the slug, it returns non-zero. `--output` writes the text handoff to a file and refuses to overwrite unless `--force` is passed. With `--json --output`, stdout is JSON and the file contains text.

```bash
specspine feature trace <slug> [path] [--json] [--output FILE] [--force]
```

Exports a native feature traceability handoff that connects acceptance criteria, execution tasks, required quality checks, and test plan evidence. It reads checklist items from `specs/features/<slug>.md` under `## Acceptance Criteria`, reuses the task checklist parser for `execution/features/<slug>.md` under `## Tasks`, and reads checklist items plus non-empty test plan lines from `quality/features/<slug>.md` under `## Required Checks` and `## Test Plan`.

JSON output includes `feature_id`, `status`, `sources`, `missing_files`, `acceptance_criteria`, `tasks`, `quality_checks`, `test_plan`, `summary`, and `gaps`. Text output is a short agent handoff with source summary, counts, gaps, and ordered trace content. Partial bundles return `0` while reporting missing files and gaps. If no native feature files exist for the slug, the command returns non-zero. `--output` writes the text handoff and refuses to overwrite unless `--force` is passed. With `--json --output`, stdout remains JSON and the file contains text.

```bash
specspine feature ready <slug> [path] [--json]
```

Runs a deterministic local readiness gate for a native feature bundle. The gate requires all three peer files, consistent peer-file status, lifecycle status `implemented` or `validated`, empty trace gaps, completed acceptance criteria, completed execution tasks, completed required checks, non-empty test plan content, and a completed `## Release Readiness` checklist in `quality/features/<slug>.md`.

JSON output includes `feature_id`, `ready`, `status`, `checks`, `blocking_checks`, `summary`, `missing_files`, and `gaps`. Text output is a compact reviewer/agent gate with status, readiness, summary counts, and blocking checks. Ready bundles return `0`; not-ready bundles and missing bundles return `1`; invalid slugs return `2`.

```bash
specspine feature handoff <slug> [path] [--json] [--output FILE] [--force]
```

Exports a compact feature-level handoff packet for implementation, acceptance, and review agents. It composes existing local evidence from feature status, trace, ready, tasks, and release readiness reports. It does not call GitHub APIs, read tokens, invoke upstream CLIs, use network access, or add third-party dependencies.

JSON output includes `feature_id`, `status`, `ready`, `sources`, `missing_files`, `gaps`, `blocking_checks`, `summary`, `acceptance_criteria`, `tasks`, `quality_checks`, `test_plan`, `release_readiness`, `recommended_commands`, and `next_actions`. Summary includes trace total/done/open, ready pass/fail/total, task total/done/open, gap count, and blocking check count. Text output is brief and includes feature/status/ready, counts, sources, next actions, open tasks, blocking checks, and key commands. The generated `feature new` execution template mirrors these focused commands for `handoff`, `tasks`, `trace`, `tests`, `ready`, `pr`, and `validate . --fusion --features`.

Missing bundles return `1` with create-or-restore guidance. Invalid slugs return `2`. Partial bundles return `0` and include missing files, trace gaps, and next actions. `--output` writes the text handoff and refuses to overwrite unless `--force` is passed. With `--json --output`, stdout remains JSON and the file contains text.

```bash
specspine feature tests <slug> [path] [--json] [--output FILE] [--force]
```

Exports a local acceptance-test packet for QA agents, test agents, and humans. It composes existing local evidence from feature handoff, trace, readiness, status, source files, and optional `## Test Coverage` links in `quality/features/<slug>.md`; it does not run tests, generate test code, infer implementation files, call network services, invoke GitHub or upstream CLIs, read tokens, or add dependencies.

Add coverage links with GitHub Markdown checklists such as `- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_name` or `- [ ] AC002 -> tests/test_features.py`. Each link records `COV###`, AC id, target, target path, local target existence, checkbox state, source file, and line. Links are local metadata only.

JSON output includes `feature_id`, `status`, `ready`, `source_files`, `missing_files`, `gaps`, `blocking_checks`, `acceptance_criteria`, `test_plan`, `test_coverage`, `test_cases`, `quality_checks`, `summary`, and `recommended_commands`. Each `test_cases` record maps deterministically from one acceptance criterion: `TC001` maps `AC001`, includes the AC text, source file, line, associated coverage links, and a behavior-to-test statement. Test case status is `covered` when any linked coverage item is checked, `planned` when only unchecked coverage exists, and `pending` when no coverage is linked.

Text output includes feature/status/ready, sources, summary, GitHub Markdown checklist test cases with linked targets, a Test Coverage section, existing test plan, quality checks, gaps, blocking checks, and key commands. Partial bundles return `0` with missing files and gaps recorded. Missing bundles return `1`; invalid slugs return `2`. `--output` writes the text packet and refuses to overwrite unless `--force` is passed. With `--json --output`, stdout remains JSON and the file contains text.

```bash
specspine feature issue <slug> [path] [--json] [--output FILE] [--force]
```

Creates a local GitHub issue draft from a native feature bundle without calling the GitHub API, reading tokens, or requiring `gh`. Text output includes the issue title and body. `--json` emits stable JSON with `title`, `body`, `feature_id`, `source_files`, `missing_files`, and `status`. `--output` writes the issue body to a file and refuses to overwrite an existing file unless `--force` is passed.

```bash
specspine feature pr <slug> [path] [--json] [--output FILE] [--force]
```

Creates a local GitHub Pull Request draft from a native feature bundle without creating a remote PR, calling the GitHub API, reading tokens, requiring `gh`, using network access, or vendoring upstream code. The draft composes existing local evidence from feature status, handoff, trace, readiness, release readiness, and source files.

JSON output includes `title`, `body`, `feature_id`, `status`, `ready`, `source_files`, `missing_files`, `gaps`, `blocking_checks`, `summary`, and `recommended_commands`. Text output includes the title and a GitHub Markdown body with Summary, Feature, Why, Acceptance Criteria, Tasks, Test Plan, Release Readiness, Readiness / Blocking Checks, Source Files, Missing Files, and Key Commands. Acceptance criteria, tasks, release readiness, gaps, and readiness checks use checklist syntax suitable for PR review.

Partial bundles return `0` while marking missing files, gaps, and blocking checks in the draft. If no native feature files exist for the slug, the command returns non-zero. Invalid slugs return `2`. `--output` writes the PR body to a file and refuses to overwrite an existing file unless `--force` is passed. With `--json --output`, stdout remains JSON and the file contains the text body.

```bash
specspine status [path] [--json] [--adapters] [--validate] [--feature-summaries] [--feature-status STATUS] [--feature-ready READY] [--feature-sort KEY] [--feature-sort-desc]
```

Summarizes workspace completeness, fusion completeness, core artifact status, native feature files, feature lifecycle status, enabled upstreams, and recommended next actions. `--json` emits a stable compact context packet for agents and scripts. `--adapters` also checks external OpenSpec, Spec Kit, and Superpowers availability.

`--validate` appends a compact `validation` summary to the status payload with `ok`, `summary`, `failed_checks`, and `included`. It checks workspace, fusion, and native feature bundles by default. External adapter availability checks are included only when `--adapters` is also passed. Text output adds a short Validation section with result, summary counts, and failed check ids only. `status` remains a report command and returns `0` even when the validation summary reports failures.

`--feature-summaries` appends an optional `feature_summaries` list to JSON status and a short Feature summaries section to text status. Each entry is derived from local native feature bundle discovery and the existing feature handoff report, with `feature_id`, `slug`, `status`, `complete`, `ready`, `missing_files`, `tasks_summary`, `ready_summary`, gap count, blocking check count, deterministic `next_actions`, and `recommended_commands`. The flag is not enabled by default because startup status should stay small; use it when an agent or maintainer needs to choose or compare multiple native features before opening a focused `feature handoff` packet.

Feature summary filters and sorting are local and deterministic. `--feature-status STATUS` can be repeated and accepts `proposed`, `planned`, `in-progress`, `implemented`, `validated`, `archived`, `invalid`, and `unknown`. `--feature-ready READY` accepts `yes`, `no`, `true`, `false`, `ready`, and `not-ready`. `--feature-sort KEY` accepts `slug`, `status`, `ready`, `gaps`, `blocking`, and `tasks-open`; `--feature-sort-desc` reverses the selected order. These options are valid only with `--feature-summaries`; unsupported values or missing `--feature-summaries` return code `2`.

```bash
specspine validate [path] [--fusion] [--features] [--adapters] [--json]
```

Runs executable local checks over SpecSpine contracts. By default it validates required workspace files. `--fusion` also requires fusion files, verifies `integration_mode: adapter`, verifies `vendored_upstream_code: false`, and checks enabled upstream adapter docs. `--features` checks native feature bundle consistency across spec, execution, and quality files, including allowed lifecycle status and peer-file status consistency. `--adapters` probes only enabled external upstream adapters. `--json` emits stable JSON with `root`, `ok`, `checks`, and `summary`; any `fail` check returns a non-zero exit code.

```bash
specspine fuse [path] --agent codex
```

Creates the fusion layer and records how OpenSpec, Spec Kit, and Superpowers map into the SpecSpine workflow.

```bash
specspine fuse [path] --agent codex --run-upstream
```

Runs upstream initializers through their public CLIs or plugin checks.

```bash
specspine doctor [path] --fusion --adapters
```

Checks SpecSpine files and external adapter availability.

```bash
specspine adapters install-hints
```

Prints upstream install instructions and project links.

## Design Principles

- **Specs are living artifacts**, not one-time documents.
- **AI agents need context boundaries**, not just prompts.
- **Execution should be traceable back to intent**.
- **Quality should be represented before implementation starts**.
- **The tool should fit existing repos**, not force a monorepo or platform migration.
- **Upstream projects stay upstream**: integrations use public CLIs, packages, and plugins rather than vendored code.

## Roadmap

- Adapter lifecycle mappings.
- Task decomposition from specs and richer task summaries.
- Quality gate definitions.
- Richer adapter sync for OpenSpec, Spec Kit, Superpowers, and other workflow engines.
- Remote GitHub issue and pull request synchronization beyond offline drafts.

## Development

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

Run the CLI from source:

```bash
PYTHONPATH=src python3 -m specspine doctor .
```

## License

License is TBD.
