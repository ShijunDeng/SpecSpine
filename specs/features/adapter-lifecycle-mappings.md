# Adapter Lifecycle Mappings

Feature ID: adapter-lifecycle-mappings
Status: validated
Priority: high
Owner: SpecSpine maintainers

## Why

SpecSpine already records OpenSpec, Spec Kit, and Superpowers as external adapters, but agents need a stable local map from native lifecycle states to upstream phases before any remote sync or upstream command automation is safe. A local export gives reviewers and agents a shared definition of what `proposed`, `planned`, `in-progress`, `implemented`, `validated`, and `archived` mean for each adapter without invoking upstream tools.

## Users

- Main agents deciding which upstream artifact should guide a feature at each lifecycle stage.
- Acceptance and review agents checking that SpecSpine status transitions align with upstream workflows.
- Maintainers planning future adapter sync, GitHub issue sync, or pull request sync while keeping the current command offline.

## Scope

- Add `specspine adapters lifecycle [path] [--json]`.
- Export mappings for OpenSpec, Spec Kit, and Superpowers.
- Cover all native lifecycle statuses: `proposed`, `planned`, `in-progress`, `implemented`, `validated`, and `archived`.
- Include stable mapping fields: `id`, `status`, `specspine_meaning`, `upstream_phase`, `upstream_artifacts`, `agent_focus`, and `local_commands`.
- Report adapter `enabled`, `config`, and `config_exists` from local fusion config and adapter files.
- Emit stable JSON with `root`, `native_statuses`, `adapters`, `summary`, and `recommended_commands`.
- Emit concise text output with adapter names, config state, and status-to-phase mapping ids.
- Return `0` even when adapters are disabled or adapter config files are missing.
- Keep the command local, static, zero-dependency, network-free, GitHub-free, token-free, and non-executing.

## Non-Goals

- Running OpenSpec, Spec Kit, Superpowers, `gh`, GitHub APIs, shell commands, or network calls.
- Creating, modifying, or syncing upstream-managed artifacts.
- Replacing upstream lifecycles with private reimplementations.
- Changing native feature lifecycle transition rules.

## Acceptance Criteria

- [x] `specspine adapters lifecycle --json` reports exactly three adapters: `openspec`, `speckit`, and `superpowers`.
- [x] JSON output includes the six native lifecycle statuses and 18 total mappings.
- [x] Each mapping has a stable adapter/status id and includes status meaning, upstream phase, upstream artifacts, agent focus, and local commands.
- [x] Fused workspaces report adapter `enabled` and `config_exists` from local fusion files.
- [x] Plain or missing-config workspaces still return `0`, keep mappings, and report disabled or missing config state.
- [x] Text output includes adapter names, mapping ids, native statuses, and upstream phases.
- [x] Recommended commands include local status validation, adapter doctor, and project validation.
- [x] The command does not call subprocesses, network services, GitHub, `gh`, upstream CLIs, or read token files.
- [x] Documentation and agent guidance describe the lifecycle export and offline boundary.
- [x] Dogfood readiness, project validation, unit tests, diff checks, and token-prefix scanning are complete.
