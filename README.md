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
- A local GitHub issue draft exporter: `specspine feature issue`.
- A fusion initializer: `specspine fuse`.
- A compact workspace status packet with optional validation summaries: `specspine status --json --validate`.
- An executable validation layer: `specspine validate --json`.
- Adapter metadata for OpenSpec, Spec Kit, and Superpowers.
- Default spec templates for intent, product, architecture, features, quality, and execution.
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

Draft a local GitHub issue from the feature bundle:

```bash
specspine feature issue add-dark-mode .
specspine feature issue add-dark-mode . --json
```

Advance the feature lifecycle when the bundle moves forward:

```bash
specspine feature status add-dark-mode . --set planned
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

Creates `AGENTS.md` in the target workspace with concise instructions for Codex, Claude, Gemini, and similar coding agents. The file tells agents to read `specspine status . --json`, validate before and after edits, use native feature bundles for new requirements, keep OpenSpec/Spec Kit/Superpowers as external adapters, avoid GitHub tokens/API calls by default, and only use `--run-upstream` when explicitly requested. Existing files are not overwritten unless `--force` is passed.

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
specspine feature status <slug> [path] [--set STATUS] [--json]
```

Reads or updates the lifecycle status for a native feature bundle. Without `--set`, the command reports the current peer-file status and clearly marks mixed or inconsistent files. With `--set`, it updates existing peer files to an allowed status and returns non-zero if no feature files exist. Invalid slugs and invalid statuses return code `2`. `--json` emits stable JSON with `feature_id`, `status`, `consistent`, `files`, and `missing_files`; status updates also include `updated_files`.

```bash
specspine feature issue <slug> [path] [--json] [--output FILE] [--force]
```

Creates a local GitHub issue draft from a native feature bundle without calling the GitHub API, reading tokens, or requiring `gh`. Text output includes the issue title and body. `--json` emits stable JSON with `title`, `body`, `feature_id`, `source_files`, `missing_files`, and `status`. `--output` writes the issue body to a file and refuses to overwrite an existing file unless `--force` is passed.

```bash
specspine status [path] [--json] [--adapters] [--validate]
```

Summarizes workspace completeness, fusion completeness, core artifact status, native feature files, feature lifecycle status, enabled upstreams, and recommended next actions. `--json` emits a stable compact context packet for agents and scripts. `--adapters` also checks external OpenSpec, Spec Kit, and Superpowers availability.

`--validate` appends a compact `validation` summary to the status payload with `ok`, `summary`, `failed_checks`, and `included`. It checks workspace, fusion, and native feature bundles by default. External adapter availability checks are included only when `--adapters` is also passed. Text output adds a short Validation section with result, summary counts, and failed check ids only. `status` remains a report command and returns `0` even when the validation summary reports failures.

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

- Feature lifecycle transition policy and adapter mappings.
- Task decomposition from specs.
- Quality gate definitions.
- Agent handoff packets.
- Richer adapter sync for OpenSpec, Spec Kit, Superpowers, and other workflow engines.
- GitHub issue and pull request synchronization.

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
