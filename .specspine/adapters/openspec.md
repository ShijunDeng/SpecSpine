# OpenSpec Adapter

Upstream: https://github.com/Fission-AI/OpenSpec
License: MIT
Integration mode: external CLI, no vendored source code.

## Role

OpenSpec owns lightweight change proposals, spec deltas, design notes, task lists, validation, and archive flow.

## Install

```bash
npm install -g @fission-ai/openspec@latest
```

## Initialize Through SpecSpine

```bash
specspine fuse . --agent codex --run-upstream
```

Equivalent OpenSpec command:

```bash
openspec init . --tools codex
```

## Expected Artifacts

- `openspec/specs/`
- `openspec/changes/`
- `openspec/config.yaml`

SpecSpine references these artifacts but does not replace OpenSpec's own lifecycle.
