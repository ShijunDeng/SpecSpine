# Feature Handoff Packet Quality

Feature ID: feature-handoff-packet
Status: validated
Why: A handoff packet is useful only if it is compact, deterministic, local, token-free, and strict about missing evidence.

## Required Checks

- [x] Unit tests cover handoff JSON and text output for ready bundles.
- [x] Unit tests cover partial bundles with missing files, trace gaps, open tasks, blocking checks, and deterministic next actions.
- [x] Unit tests cover missing bundles returning a packet and exit code `1`.
- [x] Unit tests cover invalid slugs returning exit code `2`.
- [x] Unit tests cover `--output`, overwrite refusal, `--force`, and `--json --output`.
- [x] Unit tests cover agent template guidance and dogfood artifact readiness.
- [x] The implementation does not call GitHub APIs, read tokens, call upstream CLIs, access network services, or add third-party dependencies.

## Test Coverage

- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_feature_handoff_cli_text_and_json_outputs_ready_bundle
- [x] AC002 -> tests/test_features.py::FeatureBundleTests::test_feature_handoff_cli_text_and_json_outputs_ready_bundle
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_feature_handoff_cli_text_and_json_outputs_ready_bundle
- [x] AC004 -> tests/test_features.py::FeatureBundleTests::test_feature_handoff_cli_reports_partial_bundle_actions
- [x] AC005 -> tests/test_features.py::FeatureBundleTests::test_feature_handoff_cli_text_and_json_outputs_ready_bundle
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_feature_handoff_cli_output_file_overwrite_force_and_json_output
- [x] AC007 -> tests/test_features.py::FeatureBundleTests::test_feature_handoff_cli_missing_bundle_returns_packet_and_nonzero
- [x] AC007 -> tests/test_features.py::FeatureBundleTests::test_feature_handoff_cli_invalid_slug_returns_two
- [x] AC008 -> tests/test_agents.py::AgentsTests::test_agents_content_includes_required_commands_and_boundaries
- [x] AC008 -> tests/test_features.py::FeatureBundleTests::test_dogfood_feature_handoff_packet_is_validated_and_ready
- [x] AC008 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_feature_handoff_documentation_describes_workflow

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine feature handoff feature-handoff-packet . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-handoff-packet . --json`.
- Run the requested repository token-prefix scan and confirm no credential token prefixes are present.

## Review Notes

- The handoff command composes existing local report evidence; it does not invent feature content or infer semantic coverage.
- Missing bundles still produce a small packet so the next agent receives concrete create-or-restore guidance.
- Partial bundles remain non-fatal because the packet is intended to help agents repair missing peer files and sections.

## Release Readiness

- [x] `feature-handoff-packet` has complete spec, execution, and quality peer files.
- [x] Lifecycle status is `validated` across all peer files.
- [x] Acceptance criteria, tasks, required checks, test plan, and release readiness evidence are complete.
- [x] Local verification commands for this round pass.
