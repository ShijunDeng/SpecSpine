# Security Cues Packet Quality

Feature ID: security-cues-packet
Status: validated
Why: A security cue packet is useful only if it stays local, avoids leaking file contents or secrets, and makes clear that cues are review prompts rather than vulnerability proof.

## Required Checks

- [x] Unit tests cover security cue detection and confirm rendered output omits secret values.
- [x] Unit tests cover missing files without crashes.
- [x] Unit tests cover feature id inference from native peer paths.
- [x] Unit tests cover missing feature and invalid slug behavior.
- [x] Unit tests guard against subprocess execution, network access, GitHub access, upstream CLI execution, environment reads, and token reads.
- [x] Documentation and agent guidance list the command and advisory-only safety contract.
- [x] Generated feature templates include security cues handoff and release-readiness guidance.
- [x] The dogfood bundle is validated across spec, execution, and quality peer files.

## Test Coverage

- [x] AC001 -> tests/test_security.py::SecurityCueReportTests::test_cli_json_and_missing_feature_exit_codes
- [x] AC002 -> tests/test_security.py::SecurityCueReportTests::test_cli_json_and_missing_feature_exit_codes
- [x] AC003 -> tests/test_security.py::SecurityCueReportTests::test_missing_files_are_reported_without_crashing
- [x] AC004 -> tests/test_security.py::SecurityCueReportTests::test_detects_security_cues_without_emitting_file_content
- [x] AC005 -> tests/test_security.py::SecurityCueReportTests::test_feature_is_inferred_from_peer_paths
- [x] AC006 -> tests/test_security.py::SecurityCueReportTests::test_feature_is_inferred_from_peer_paths
- [x] AC007 -> tests/test_security.py::SecurityCueReportTests::test_missing_feature_is_reported_without_crashing
- [x] AC007 -> tests/test_security.py::SecurityCueReportTests::test_invalid_feature_slug_is_rejected
- [x] AC007 -> tests/test_security.py::SecurityCueReportTests::test_cli_invalid_slug_returns_two
- [x] AC008 -> tests/test_security.py::SecurityCueReportTests::test_builder_is_local_only_and_renderers_are_pure
- [x] AC009 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_security_cues_packet_documentation_and_dogfood_describe_workflow
- [x] AC009 -> tests/test_features.py::FeatureBundleTests::test_create_feature_bundle_in_plain_workspace
- [x] AC009 -> tests/test_agents.py::AgentsTests::test_agents_content_includes_required_commands_and_boundaries

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_security`.
- Run `PYTHONPATH=src python3 -m unittest tests.test_features tests.test_agents tests.test_dogfood_artifacts`.
- Run `PYTHONPATH=src python3 -m specspine security cues . --json`.
- Run `PYTHONPATH=src python3 -m specspine security cues . --feature security-cues-packet --changed src/specspine/security.py --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready security-cues-packet . --json --require-coverage`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.

## Review Notes

- The packet reports keyword cues only and deliberately avoids source line text.
- Recommended commands are records for humans or agents to inspect later; none are executed by the exporter.
- Missing feature bundles still return a JSON report so callers can surface blockers consistently.

## Release Readiness

- [x] `security-cues-packet` has complete spec, execution, and quality peer files.
- [x] Lifecycle status is `validated` across all peer files.
- [x] Acceptance criteria, implementation tasks, required checks, test coverage links, and release readiness evidence are complete.
- [x] Focused security cue tests pass.
- [x] Project documentation and generated templates describe the security cues workflow.
