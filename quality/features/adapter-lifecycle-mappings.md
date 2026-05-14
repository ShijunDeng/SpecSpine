# Adapter Lifecycle Mappings Quality

Feature ID: adapter-lifecycle-mappings
Status: validated
Why: Lifecycle mappings will guide future adapter and remote sync decisions, so the command must be stable, local, and explicitly non-executing.

## Required Checks

- [x] Unit tests verify JSON shape includes three adapters, six statuses, and 18 mappings.
- [x] Unit tests verify fused workspaces report enabled state and config existence correctly.
- [x] Unit tests verify plain workspaces keep mappings while reporting disabled adapters and missing configs.
- [x] Unit tests verify missing adapter config files do not make lifecycle export fail.
- [x] Unit tests verify text output includes adapter names, mapping ids, statuses, and upstream phases.
- [x] Unit tests verify the command does not call subprocesses, network services, `gh`, upstream CLIs, or read token files.
- [x] Documentation describes output shape, return code behavior, and offline boundaries.
- [x] Dogfood validation verifies this bundle has consistent `validated` lifecycle status.
- [x] Dogfood readiness verifies this bundle passes the local feature gate.
- [x] Token-prefix scanning verifies no GitHub token was added.

## Test Coverage

- [x] AC001 -> tests/test_adapter_lifecycle.py::AdapterLifecycleTests::test_lifecycle_json_shape_for_fused_workspace
- [x] AC002 -> tests/test_adapter_lifecycle.py::AdapterLifecycleTests::test_lifecycle_json_shape_for_fused_workspace
- [x] AC003 -> tests/test_adapter_lifecycle.py::AdapterLifecycleTests::test_lifecycle_json_shape_for_fused_workspace
- [x] AC004 -> tests/test_adapter_lifecycle.py::AdapterLifecycleTests::test_lifecycle_json_shape_for_fused_workspace
- [x] AC005 -> tests/test_adapter_lifecycle.py::AdapterLifecycleTests::test_lifecycle_json_for_plain_workspace_keeps_mappings_without_enabled_configs
- [x] AC005 -> tests/test_adapter_lifecycle.py::AdapterLifecycleTests::test_lifecycle_json_reports_missing_config_without_failing
- [x] AC006 -> tests/test_adapter_lifecycle.py::AdapterLifecycleTests::test_lifecycle_text_includes_adapter_names_ids_statuses_and_phases
- [x] AC008 -> tests/test_adapter_lifecycle.py::AdapterLifecycleTests::test_lifecycle_reads_only_fusion_config_and_skips_external_tools

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features --json`.
- Run `PYTHONPATH=src python3 -m specspine adapters lifecycle . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready adapter-lifecycle-mappings . --json`.
- Run `git diff --check`.
- Run the repository GitHub token-prefix scan and confirm it produces no matches.

## Review Notes

- The command exports definitions only; disabled adapters and missing config files are report data, not failures.
- The command reads local fusion config for adapter enablement and config paths, then uses path existence checks for config state.
- No GitHub API, `gh`, network, token, subprocess, upstream CLI, dependency, or command-execution path is introduced.

## Release Readiness

- [x] `specspine adapters lifecycle . --json` works for this repository.
- [x] Plain-workspace and missing-config behavior remain successful and explicit.
- [x] Unit tests and repository validation pass.
- [x] Documentation and agent guidance include the lifecycle mapping workflow.
- [x] The dogfood bundle is ready and validated.
