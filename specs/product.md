# Product Spec

## Scope

SpecSpine is a local CLI and file convention for spec-driven AI development. The product surface includes:

- Workspace initialization for intent, product, architecture, execution, and quality artifacts.
- Agent instruction generation through `specspine agents init`.
- Native feature bundles spanning `specs/features/`, `execution/features/`, and `quality/features/`.
- Native feature lifecycle status query/update across feature peer files.
- Local GitHub issue draft generation from feature bundles without API calls.
- Fusion initialization for OpenSpec, Spec Kit, and Superpowers as external adapters.
- Status, optional status validation summaries, validation, doctor, and adapter inspection commands suitable for CI and coding agents.

## Non-Goals

- Hosting a server, database, or background daemon.
- Vendoring OpenSpec, Spec Kit, Superpowers, or any upstream source tree.
- Owning upstream lifecycle files after an external tool generates them.
- Reading GitHub tokens, writing GitHub tokens, or creating remote GitHub issues by default.
- Replacing OpenSpec proposals, Spec Kit plans, or Superpowers skills with private reimplementations.

## User Workflows

- Initialize a base workspace with `specspine init .` and create agent guidance with `specspine agents init .`.
- Initialize the full fusion layer with `specspine fuse . --agent codex`, which writes adapter contracts but does not invoke upstream tools.
- Run `specspine status . --json` before work to understand missing artifacts, enabled upstreams, and next recommendations; add `--validate` when a single packet should also show quality-gate summary and failed check ids.
- Create new requirements with `specspine feature new <slug> . --title "..." --why "..."`, then keep the spec, execution, and quality peer files aligned by `Feature ID`.
- Move feature bundles through `proposed`, `planned`, `in-progress`, `implemented`, `validated`, and `archived` with `specspine feature status <slug> . --set STATUS`.
- Generate an offline issue draft with `specspine feature issue <slug> . --json` or `--output`.
- Verify readiness with `specspine validate . --fusion --features` and the unit test suite.

## Acceptance Criteria

- Base and fusion workspaces can be initialized without external dependencies.
- A complete fused workspace reports `workspace.complete=true` and `fusion.complete=true` in status JSON.
- `status --json --validate` reports `validation.ok`, summary counts, included check groups, and failed checks without changing the report command's zero exit behavior.
- Enabled upstream metadata reports OpenSpec, Spec Kit, and Superpowers as enabled when their adapter files are present.
- Validation passes for complete workspace, fusion artifacts, and native feature bundles with consistent allowed lifecycle status.
- Fusion config preserves `integration_mode: adapter` and `vendored_upstream_code: false`.
