# Adapter Handoff Artifacts

Feature ID: adapter-handoff-artifacts
Status: validated
Priority: high
Owner: SpecSpine maintainers

## Why

Adapter handoff currently produces one combined packet. Agents often need the OpenSpec, Spec Kit, and Superpowers context as separate reviewable files while keeping the same local, non-executing boundary.

## Users

- Main agents exporting adapter context before delegating review slices.
- Adapter-focused subagents that should only inspect one upstream workflow's context.
- Reviewers checking evidence, gaps, blockers, and safety flags before any upstream tool is run manually.

## Scope

- Add `specspine adapters handoff <slug> [path] --output-dir DIR [--json] [--force]`.
- Write `manifest.json`, `combined.md`, and focused Markdown files for OpenSpec, Spec Kit, and Superpowers.
- Include feature id, status, readiness, summary, source files, missing files, gaps, blockers, artifact paths, and safety flags in the manifest.
- Preserve `--json` stdout as the full handoff report while adding artifact location metadata when an output directory is used.
- Preserve existing `--output FILE` behavior and allow it to work with `--output-dir`.
- Refuse to overwrite command-managed artifact files unless `--force` is passed, while preserving unknown files in the directory.
- Keep artifact export local: no upstream tools, subprocesses, network, GitHub operations, token reads, or new dependencies.

## Non-Goals

- Running OpenSpec, Spec Kit, Superpowers, GitHub CLI, shell commands, or network calls.
- Creating remote artifacts or reading credentials.
- Replacing upstream adapter workflows with SpecSpine-owned generated content.
- Deleting or rewriting unknown files in the output directory.

## Acceptance Criteria

- [x] `--output-dir` writes `manifest.json`, `combined.md`, and one focused Markdown file for each supported adapter.
- [x] Focused adapter files contain adapter-specific OpenSpec, Spec Kit, and Superpowers handoff content.
- [x] Manifest JSON includes feature evidence, artifact paths, and explicit false safety flags for execution, network, token, remote creation, and auto-run.
- [x] Existing command-managed artifact files cause exit code `1` without `--force`, and stderr lists existing files.
- [x] `--force` overwrites command-managed artifact files and preserves unknown files.
- [x] `--json --output-dir` prints parseable full JSON handoff data and writes the artifact directory.
- [x] `--output FILE` remains compatible when used alone or together with `--output-dir`.
- [x] Missing bundle and invalid slug behavior remain unchanged.
- [x] Tests prove artifact writing does not use subprocesses, network services, adapter probes, upstream CLIs, or token environment reads.
- [x] Documentation and agent guidance describe artifact export and its safety boundary.
