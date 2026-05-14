# Architecture

## System Shape

SpecSpine is a small Python package under `src/specspine` with a command-line entry point. The architecture is file-first:

- `workspace` owns base workspace templates and required artifact checks.
- `agents` writes project-local `AGENTS.md` instructions.
- `features` creates and reads native feature bundles and offline issue drafts.
- `adapters` describes external upstream tools and probes local availability.
- `fusion` writes the OpenSpec + Spec Kit + Superpowers adapter layer.
- `status` builds machine-readable workspace summaries and recommendations.
- `validation` turns workspace, fusion, adapter, and feature contracts into checks.
- `cli` maps command-line arguments to those modules.

## Data And Interfaces

- `.specspine/spine.yaml` maps the backbone files for a workspace.
- `.specspine/fusion.yaml` records enabled upstreams, the selected agent profile, and the adapter/no-vendor boundary.
- `.specspine/fusion-map.md` and `.specspine/adapters/*.md` document the human-facing integration contract.
- `specs/`, `execution/`, and `quality/` carry the repository-owned source of truth.
- Native feature bundles use peer files with matching `Feature ID: <slug>` and `Status: proposed` markers.
- The main machine interfaces are `specspine status . --json` and `specspine validate . --fusion --features`.

## Decisions

- Keep the CLI zero-dependency so it runs in constrained agent environments and source checkouts.
- Treat upstream tools as adapters. SpecSpine can print install hints and optionally run public initializer commands, but it does not copy or own upstream code.
- Keep GitHub issue support offline by drafting structured text/JSON instead of requiring `gh`, tokens, or API access.
- Make validation executable and local so agents can detect missing files and broken contracts before and after edits.

## Risks

- Template drift can make generated artifacts too generic. Dogfood this repository and update templates when repeated manual corrections appear.
- Upstream command surfaces may change. Keep adapter docs explicit and probe availability separately from core validation.
- Feature bundles can diverge across spec, execution, and quality files. Validate matching IDs and keep task lists traceable.
- Agent instructions can become stale. Prefer short rules that point back to status, validation, and repository specs.
