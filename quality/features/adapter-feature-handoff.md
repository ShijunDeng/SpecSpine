# Adapter Feature Handoff Quality

Feature ID: adapter-feature-handoff
Status: validated
Why: The command is useful only if it produces deterministic local handoff data and proves it did not execute or probe upstream tooling.

## Required Checks

- [x] Unit tests verify fused workspace JSON shape, adapter fields, summary counts, and recommended local commands.
- [x] Unit tests verify Markdown output includes feature status, readiness, gaps, blockers, adapter phases, steps, notes, and local commands.
- [x] Unit tests verify `--output`, `--force`, and `--json --output` behavior.
- [x] Unit tests verify every native status selects the matching adapter lifecycle mapping.
- [x] Unit tests verify recommended upstream steps include required safety and execution fields.
- [x] Unit tests verify OpenSpec, Spec Kit, and Superpowers key recommended steps.
- [x] Unit tests verify partial bundles return success with missing files, gaps, and blockers.
- [x] Unit tests verify missing bundle and invalid slug exit codes.
- [x] Unit tests verify subprocesses, network calls, adapter probes, tool probes, and token environment reads are not used.
- [x] Documentation and agent guidance describe the command and offline boundary.
- [x] Dogfood validation verifies this bundle has consistent `validated` lifecycle status.
- [x] Dogfood readiness verifies this bundle passes the local feature gate.

## Test Coverage

- [x] AC001 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_handoff_json_shape_for_fused_workspace
- [x] AC002 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_handoff_text_output_contains_feature_adapter_steps_and_local_commands
- [x] AC003 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_output_file_semantics_keep_json_stdout_and_markdown_file
- [x] AC004 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_current_status_selects_each_adapter_mapping
- [x] AC005 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_recommended_upstream_steps_are_safe_unexecuted_and_adapter_specific
- [x] AC006 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_partial_bundle_returns_zero_and_records_missing_gaps_blockers
- [x] AC007 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_missing_bundle_and_invalid_slug_exit_codes
- [x] AC008 -> tests/test_adapter_handoff.py::AdapterFeatureHandoffTests::test_handoff_does_not_call_subprocess_network_probe_or_read_tokens

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_adapter_handoff`.
- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine adapters handoff adapter-feature-handoff . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready adapter-feature-handoff . --json`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features --json`.
- Run `git diff --check`.

## Review Notes

- The command composes existing local reports; it does not call `probe_adapters` or runtime tool detection.
- OpenSpec recommendations are argv data only and are always marked `executed=false`.
- Spec Kit and Superpowers recommendations are agent instructions only and do not imply SpecSpine ran upstream workflows.
- The output remains suitable for partial bundles so agents can see missing evidence before adapter work starts.

## Release Readiness

- [x] `specspine adapters handoff adapter-feature-handoff . --json` exports the expected local packet.
- [x] Partial bundle and missing bundle behavior are explicit and tested.
- [x] Focused adapter handoff tests and full repository tests pass.
- [x] Documentation and AGENTS guidance include the command.
- [x] The dogfood bundle is ready and validated.
