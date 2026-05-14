# Feature Task Export

Feature ID: feature-task-export
Status: validated

## Why

Native feature bundles already carry execution tasks, but agents cannot reliably consume Markdown checklist items from `execution/features/<slug>.md` as a stable task packet. A local task export command makes the implementation handoff explicit without generating new work or depending on upstream services.

## Users

- AI coding agents that need a compact ordered checklist before editing code.
- Maintainers who want feature specs, plans, and quality records connected to executable implementation tasks.
- Local scripts that need stable task JSON without reading GitHub issues or upstream tool state.

## Scope

- Add `specspine feature tasks <slug> [path] [--json] [--output FILE] [--force]`.
- Parse Markdown checkbox items from the execution feature file's `## Tasks` section.
- Preserve task order, done state, source file, line number, and stable generated ids.
- Emit concise text suitable for agent execution and stable JSON suitable for scripts.
- Support partial bundles where spec or quality files exist but execution is missing.
- Keep the command local-only with no GitHub API, token, `gh`, or upstream tool dependency.

## Non-Goals

- Generating tasks from prose or acceptance criteria.
- Synchronizing task state to GitHub, OpenSpec, Spec Kit, or Superpowers.
- Extending workspace status with task summaries in this iteration.
- Adding runtime dependencies.

## Acceptance Criteria

- [x] Checklist tasks are parsed in order from `## Tasks` with ids, text, done state, source file, and line number.
- [x] Text output gives an agent the feature id, status, summary, source, and task list.
- [x] JSON output includes `feature_id`, `status`, `source_file`, `tasks`, and `summary`.
- [x] Empty or missing execution tasks are reported clearly without inventing tasks.
- [x] All missing feature files return a non-zero exit code.
- [x] `--output`, `--force`, and `--json --output` behavior is covered.
- [x] The workflow remains token-free and does not call GitHub or upstream tools.
