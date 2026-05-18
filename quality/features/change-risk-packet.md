# Change Risk Packet Quality

Feature ID: change-risk-packet
Status: validated
Why: A change risk packet is useful only if it is deterministic, local-only, conservative about risk, and explicit that recommended commands are advisory.

## Required Checks

- [x] Unit tests cover changed-path classification and summary counts.
- [x] Unit tests cover feature id inference from native peer paths.
- [x] Unit tests cover workspace packets with no changed files.
- [x] Unit tests cover missing feature and invalid slug behavior.
- [x] Unit tests guard against subprocess execution, network access, GitHub access, upstream CLI execution, and token reads.
- [x] Documentation and agent guidance list the command and safety contract.
- [x] Generated feature templates include change risk handoff and release-readiness guidance.
- [x] The dogfood bundle is validated across spec, execution, and quality peer files.

## Test Coverage

- [x] AC001 -> tests/test_change.py::ChangeRiskReportTests::test_cli_json_and_missing_feature_exit_codes
- [x] AC002 -> tests/test_change.py::ChangeRiskReportTests::test_cli_json_and_missing_feature_exit_codes
- [x] AC003 -> tests/test_change.py::ChangeRiskReportTests::test_changed_files_are_classified_and_summarized
- [x] AC004 -> tests/test_change.py::ChangeRiskReportTests::test_feature_is_inferred_from_peer_paths
- [x] AC005 -> tests/test_change.py::ChangeRiskReportTests::test_feature_is_inferred_from_peer_paths
- [x] AC006 -> tests/test_change.py::ChangeRiskReportTests::test_missing_feature_is_reported_without_crashing
- [x] AC006 -> tests/test_change.py::ChangeRiskReportTests::test_invalid_feature_slug_is_rejected
- [x] AC006 -> tests/test_change.py::ChangeRiskReportTests::test_cli_invalid_slug_returns_two
- [x] AC007 -> tests/test_change.py::ChangeRiskReportTests::test_builder_is_local_only_and_renderers_are_pure
- [x] AC008 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_change_risk_packet_documentation_and_dogfood_describe_workflow
- [x] AC008 -> tests/test_features.py::FeatureBundleTests::test_create_feature_bundle_in_plain_workspace
- [x] AC008 -> tests/test_agents.py::AgentsTests::test_agents_content_includes_required_commands_and_boundaries

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_change`.
- Run `PYTHONPATH=src python3 -m unittest tests.test_features tests.test_agents tests.test_dogfood_artifacts`.
- Run `PYTHONPATH=src python3 -m specspine change risk . --json`.
- Run `PYTHONPATH=src python3 -m specspine change risk . --feature change-risk-packet --changed src/specspine/change.py --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready change-risk-packet . --json --require-coverage`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.

## Review Notes

- The packet uses caller-supplied changed paths instead of running git, keeping the core command subprocess-free.
- Risk levels are advisory labels for review triage, not merge decisions.
- Missing feature bundles still return a JSON report so callers can surface blockers consistently.

## Release Readiness

- [x] `change-risk-packet` has complete spec, execution, and quality peer files.
- [x] Lifecycle status is `validated` across all peer files.
- [x] Acceptance criteria, implementation tasks, required checks, test coverage links, and release readiness evidence are complete.
- [x] Focused change risk tests pass.
- [x] Project documentation and generated templates describe the changed-path risk workflow.
