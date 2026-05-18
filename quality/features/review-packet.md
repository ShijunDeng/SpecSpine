# Review Packet Quality

Feature ID: review-packet
Status: validated
Why: A review packet is useful only if it is deterministic, local-only, clear about advisory commands, and grounded in existing SpecSpine evidence.

## Required Checks

- [x] Unit tests cover workspace JSON shape and text output.
- [x] Unit tests cover feature JSON shape, changed-file forwarding, and recommended commands.
- [x] Unit tests cover invalid slug and missing feature exit behavior.
- [x] Unit tests guard against subprocess execution, network access, GitHub access, upstream CLI execution, and token reads.
- [x] Documentation and agent guidance list the command and safety contract.
- [x] Generated feature templates include review packet handoff and release-readiness guidance.
- [x] The dogfood bundle is validated across spec, execution, and quality peer files.

## Test Coverage

- [x] AC001 -> tests/test_review.py::ReviewPacketTests::test_text_output
- [x] AC001 -> tests/test_review.py::ReviewPacketTests::test_workspace_json_shape
- [x] AC002 -> tests/test_review.py::ReviewPacketTests::test_workspace_json_shape
- [x] AC003 -> tests/test_review.py::ReviewPacketTests::test_feature_json_shape_and_changed_files
- [x] AC004 -> tests/test_review.py::ReviewPacketTests::test_feature_json_shape_and_changed_files
- [x] AC005 -> tests/test_review.py::ReviewPacketTests::test_invalid_feature_slug_returns_two
- [x] AC005 -> tests/test_review.py::ReviewPacketTests::test_missing_feature_returns_one_with_report
- [x] AC006 -> tests/test_review.py::ReviewPacketTests::test_report_is_local_only
- [x] AC007 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_review_packet_documentation_and_dogfood_describe_workflow
- [x] AC007 -> tests/test_features.py::FeatureBundleTests::test_create_feature_bundle_in_plain_workspace
- [x] AC007 -> tests/test_agents.py::AgentsTests::test_agents_content_includes_required_commands_and_boundaries

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_review`.
- Run `PYTHONPATH=src python3 -m unittest tests.test_features tests.test_agents tests.test_dogfood_artifacts`.
- Run `PYTHONPATH=src python3 -m specspine review packet . --json`.
- Run `PYTHONPATH=src python3 -m specspine review packet . --feature review-packet --changed src/specspine/review.py --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready review-packet . --json --require-coverage`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.

## Review Notes

- The packet composes existing local reports instead of reimplementing their parsing rules.
- Recommended commands are records for humans or agents to inspect later; none are executed by the exporter.
- Missing feature bundles still return a JSON report so callers can surface review blockers consistently.

## Release Readiness

- [x] `review-packet` has complete spec, execution, and quality peer files.
- [x] Lifecycle status is `validated` across all peer files.
- [x] Acceptance criteria, implementation tasks, required checks, test coverage links, and release readiness evidence are complete.
- [x] Focused review packet tests pass.
- [x] Project documentation and generated templates describe the pre-merge review packet workflow.
