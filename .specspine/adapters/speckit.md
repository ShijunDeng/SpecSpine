# Spec Kit Adapter

Upstream: https://github.com/github/spec-kit
License: MIT
Integration mode: external Specify CLI, no vendored source code.

## Role

Spec Kit owns the structured specify, plan, tasks, and implement workflow for AI coding agents.

## Install

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@vX.Y.Z
```

## Initialize Through SpecSpine

```bash
specspine fuse . --agent codex --run-upstream
```

Equivalent Spec Kit command:

```bash
specify init . --integration codex
```

## Expected Artifacts

- `.specify/`
- `specs/`
- agent-specific command or skill files

SpecSpine keeps a higher-level backbone and lets Spec Kit manage its own generated agent integration files.
