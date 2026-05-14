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

The CLI is intentionally thin:

- `specspine init` creates the default workspace structure.
- `specspine feature new` creates a traceable native feature bundle.
- `specspine fuse` creates the OpenSpec + Spec Kit + Superpowers fusion layer.
- `specspine doctor` checks whether expected files exist.
- `specspine status` emits a compact status packet for humans, agents, and scripts.
- `specspine validate` turns workspace and fusion contracts into executable checks for CI and agents.
- `specspine adapters doctor` checks whether external tools are installed.
- `specspine adapters install-hints` prints upstream install guidance.

Future commands should remain thin orchestration layers over explicit files so the workspace stays understandable without a server.

`specspine status --json` is the preferred machine-readable context boundary. It reports:

- workspace and fusion completeness.
- core artifact existence.
- enabled upstream adapters.
- recommended next actions.
- optional external adapter availability when `--adapters` is passed.

`specspine validate --json` is the preferred machine-readable quality gate. It reports:

- the resolved workspace root.
- whether validation is ok.
- stable check records with `id`, `status`, `message`, and `severity`.
- summary counts for `pass`, `fail`, `warn`, and `skip`.

Validation is local-first and zero-dependency. The default mode validates base workspace files only. `--fusion` requires the fusion layer and enforces adapter-mode/no-vendored-code boundaries. `--adapters` probes external upstream adapters only when explicitly requested.

`specspine feature new <slug> [path]` is the first native feature lifecycle command. It creates three peer files:

- `specs/features/<slug>.md` for intent, users, scope, non-goals, and acceptance criteria.
- `execution/features/<slug>.md` for milestones, tasks, dependencies, and open questions.
- `quality/features/<slug>.md` for required checks, test plan, review notes, and release readiness.

Each file records the same `Feature ID: <slug>` and starts at `Status: proposed`. The command refuses to overwrite existing feature files unless `--force` is passed.

`specspine validate --features` checks that discovered native feature bundles have valid slugs, all three peer files, matching feature ids, and proposed status markers.

## Adapter Direction

Adapters should be optional. SpecSpine should be usable as plain files first, then integrate with tools such as OpenSpec, Spec Kit, Superpowers, GitHub issues, and pull requests.

The expected adapter boundary:

```text
SpecSpine files <-> adapter <-> external tool
```

Adapters should not own the source of truth unless the user explicitly chooses that mode.

## Fusion Layer

`specspine fuse` writes:

- `.specspine/fusion.yaml` for machine-readable adapter mapping.
- `.specspine/fusion-map.md` for human-readable responsibility mapping.
- `.specspine/adapters/*.md` for per-upstream contracts.
- `quality/superpowers.md` for the project-local Superpowers quality policy.

The fusion layer records `vendored_upstream_code: false`. Upstream tools are invoked through public CLIs or installed agent plugins.

## Modules

- `specspine.workspace`: local file templates and workspace checks.
- `specspine.features`: native feature slug validation, bundle templates, file creation, and discovery.
- `specspine.adapters`: upstream metadata, availability probes, agent mappings, and initializer command construction.
- `specspine.fusion`: fusion file generation and workspace initialization.
- `specspine.status`: compact workspace, fusion, artifact, upstream, and recommendation summaries.
- `specspine.validation`: executable workspace, fusion, and optional adapter contract checks.
- `specspine.cli`: command-line interface.
