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

The CLI is intentionally small at this stage:

- `specspine init` creates the default workspace structure.
- `specspine doctor` checks whether expected files exist.

Future commands should remain thin orchestration layers over explicit files so the workspace stays understandable without a server.

## Adapter Direction

Adapters should be optional. SpecSpine should be usable as plain files first, then integrate with tools such as OpenSpec, Spec Kit, Superpower, GitHub issues, and pull requests.

The expected adapter boundary:

```text
SpecSpine files <-> adapter <-> external tool
```

Adapters should not own the source of truth unless the user explicitly chooses that mode.
