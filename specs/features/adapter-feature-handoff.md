# Adapter Feature Handoff

Feature ID: adapter-feature-handoff
Status: validated
Priority: high
Owner: SpecSpine maintainers

## Why

Static adapter lifecycle mappings explain how SpecSpine statuses relate to OpenSpec, Spec Kit, and Superpowers, but implementation agents need a feature-specific packet that joins those mappings with the native feature evidence already present in the workspace. A local adapter handoff lets agents plan upstream work without executing upstream tools, probing installations, reading tokens, or calling network services.

## Users

- Main agents preparing a native feature for OpenSpec, Spec Kit, or Superpowers handoff.
- Subagents that need focused upstream phase, artifact, and step context for one feature.
- Reviewers confirming adapter work stays local, extractive, and non-executing before any external tool is run manually.

## Scope

- Add `specspine adapters handoff <slug> [path] [--json] [--output FILE] [--force]`.
- Compose native feature id, status, readiness, source files, missing files, trace gaps, blocking checks, and summary.
- Select the OpenSpec, Spec Kit, and Superpowers lifecycle mapping for the feature's current native status.
- Include adapter metadata, config state, upstream phase, upstream artifacts, agent focus, local commands, recommended upstream steps, and notes.
- Mark every recommended upstream step as data only with remote, network, token, auto-run, and executed safety fields.
- Keep OpenSpec steps as argv arrays for agent-friendly CLI commands without executing them.
- Keep Spec Kit and Superpowers steps as agent actions without implying SpecSpine ran those workflows.
- Write Markdown through `--output` while preserving JSON stdout when `--json --output` is used.
- Return `0` for partial bundles, `1` for missing bundles, and `2` for invalid slugs.
- Preserve the no vendored upstream code, no subprocess, no probe, no token, and no network boundary.

## Non-Goals

- Running OpenSpec, Spec Kit, Superpowers, `gh`, shell commands, subprocesses, or network calls.
- Detecting whether upstream tools or plugins are installed.
- Creating remote artifacts, reading authentication tokens, or syncing with GitHub.
- Copying upstream code or replacing upstream-owned workflows.

## Acceptance Criteria

- [x] JSON output includes feature evidence, adapter entries, summary counts, and recommended local commands for a fused workspace.
- [x] Markdown output is readable by humans and agents and lists feature state, gaps, blockers, adapter phases, steps, notes, and local commands.
- [x] `--json --output` prints JSON to stdout and writes Markdown to the requested file with existing overwrite semantics.
- [x] The current native status selects the matching lifecycle mapping for OpenSpec, Spec Kit, and Superpowers.
- [x] Recommended upstream steps include safe, unexecuted OpenSpec CLI argv, Spec Kit phase actions, and Superpowers skill actions.
- [x] Partial bundles return `0` while reporting missing files, gaps, blockers, and selected adapter mappings.
- [x] Missing bundles return `1`; invalid slugs return `2`.
- [x] Tests prove the command does not call subprocesses, network services, adapter probes, upstream CLIs, or read token environment variables.
- [x] Documentation and agent guidance include the adapter feature handoff workflow.
- [x] Dogfood readiness, project validation, focused tests, full tests, and diff checks are complete.
