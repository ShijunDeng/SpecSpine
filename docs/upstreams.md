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
