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
