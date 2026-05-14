# Upstream Integration Policy

SpecSpine fuses OpenSpec, Spec Kit, and Superpowers as external open source tools. It does not vendor or copy their source code.

## Integrated Projects

| Tool | Upstream | License | Integration Mode |
| --- | --- | --- | --- |
| OpenSpec | https://github.com/Fission-AI/OpenSpec | MIT | External `openspec` CLI |
| Spec Kit | https://github.com/github/spec-kit | MIT | External `specify` CLI |
| Superpowers | https://github.com/obra/superpowers | MIT | Agent plugin/extension |

## Boundary

SpecSpine may:

- Detect whether an upstream tool is installed.
- Print official install hints.
- Export static local lifecycle mappings for upstream adapter phases.
- Export feature-specific adapter handoff packets and optional local per-adapter artifact directories from local SpecSpine evidence and lifecycle mappings.
- Export local GitHub CLI sync plans and artifact directories for human review before remote issue or PR creation.
- Run upstream initializer commands when the user opts in with `--run-upstream`.
- Store adapter contracts that point to upstream artifacts and commands.
- Map upstream outputs into the SpecSpine backbone.

SpecSpine must not:

- Copy upstream source files into this repository.
- Reimplement private upstream internals.
- Treat generated upstream files as SpecSpine-owned files.
- Modify upstream-managed files unless a documented adapter command explicitly performs that action.

## Command Surfaces

OpenSpec:

```bash
openspec init . --tools <tool-id>
openspec update
openspec validate --all
```

Spec Kit:

```bash
specify init . --integration <integration-key>
specify integration list
```

Superpowers:

Superpowers is installed through the active AI coding agent's plugin or extension system. SpecSpine records the expected quality policy in `quality/superpowers.md` and expects the agent to load Superpowers from its installed plugin.

## Lifecycle Mapping

`specspine adapters lifecycle [path] [--json]` exports the local mapping between SpecSpine native feature statuses and upstream phases before any sync command touches upstream or remote state. It covers `proposed`, `planned`, `in-progress`, `implemented`, `validated`, and `archived` for OpenSpec, Spec Kit, and Superpowers.

The command is definition-only. It reads local fusion config for adapter enablement and config paths, checks whether local adapter config files exist, and returns `0` even when adapters are disabled. It does not execute `openspec`, `specify`, Superpowers, `gh`, shell commands, GitHub APIs, network calls, or token reads.

## Feature Adapter Handoff

`specspine adapters handoff <slug> [path] [--json] [--output FILE] [--output-dir DIR] [--force]` exports the local adapter handoff for one native feature. It combines native feature status, readiness, sources, gaps, and blockers with the selected OpenSpec, Spec Kit, and Superpowers lifecycle mapping.

The handoff is plan data only. OpenSpec recommendations are argv arrays for agent-friendly commands such as `openspec status --json`, `openspec instructions apply --change <slug> --json`, and `openspec validate --all --json`. Spec Kit recommendations follow the Spec -> Plan -> Tasks -> Implement artifact flow as agent actions. Superpowers recommendations name skill actions such as brainstorming, writing-plans, test-driven-development, subagent-driven-development, requesting-code-review, and verification-before-completion. SpecSpine does not execute these steps, probe adapter tools, read tokens, or call the network.

With `--output-dir`, SpecSpine writes reviewable local artifacts only: `manifest.json`, `combined.md`, `combined.json`, focused `adapters/openspec.md`, `adapters/speckit.md`, `adapters/superpowers.md`, and focused `adapters/openspec.json`, `adapters/speckit.json`, and `adapters/superpowers.json`. The manifest records the original Markdown artifact paths plus `artifacts.combined_json`, `artifacts.adapter_json`, `checksum_algorithm=sha256`, and `artifact_checksums` for every non-manifest managed content artifact. It also records safety flags with `executed=false`, `requires_network=false`, `requires_token=false`, `creates_remote=false`, and `safe_to_auto_run=false`, plus a note that artifact export does not execute upstream tools, subprocesses, network calls, GitHub operations, or token reads. Existing managed artifact files, including the JSON artifacts, require `--force`; unknown files are preserved.

## GitHub Sync Planning

`specspine feature sync-plan <slug> [path] [--json] [--output-dir DIR]` exports planned `gh issue create` and draft `gh pr create` argv arrays from local feature evidence. With `--output-dir`, it also writes `manifest.json`, Markdown body files, and a review-only `commands.sh` that points `--body-file` at those local files. It is a local review packet only: SpecSpine does not execute `gh`, does not use PR dry-run mode as an automatic safety claim, does not read tokens, does not call GitHub APIs, does not invoke subprocesses, and does not access the network.

## Agent Mapping

| SpecSpine Agent | OpenSpec Tool ID | Spec Kit Integration |
| --- | --- | --- |
| `codex` | `codex` | `codex` |
| `claude` | `claude` | `claude` |
| `copilot` | `github-copilot` | `copilot` |
| `cursor` | `cursor` | `cursor-agent` |
| `gemini` | `gemini` | `gemini` |
| `opencode` | `opencode` | `opencode` |
| `windsurf` | `windsurf` | `windsurf` |
