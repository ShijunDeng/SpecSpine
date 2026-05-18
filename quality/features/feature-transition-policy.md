# Feature Transition Policy Quality

Feature ID: feature-transition-policy
Status: validated
Why: Transition enforcement must block unsafe writes only when explicitly requested, and archive attempts must surface readiness blockers without changing files.

## Required Checks

- [x] Unit tests prove default arbitrary status updates still work without `--enforce-transition`.
- [x] Unit tests prove allowed enforced transitions write peer files and report transition JSON.
- [x] Unit tests prove disallowed enforced transitions and archived-terminal transitions return `1` without writing files.
- [x] Unit tests prove mixed or inconsistent current peer status fails before writing.
- [x] Unit tests prove enforced archive requires readiness, reports blockers, and succeeds for a ready bundle.
- [x] Unit tests prove invalid slugs or target statuses still return `2`.
- [x] Agent template and dogfood artifact tests cover the recommended lifecycle commands.
- [x] Documentation states that enforcement is opt-in and default manual updates remain compatible.

## Test Coverage

- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_feature_status_cli_enforced_allowed_transition_writes_files
- [x] AC002 -> tests/test_features.py::FeatureBundleTests::test_feature_status_cli_set_updates_existing_peer_files
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_feature_status_cli_enforced_allowed_transition_writes_files
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_feature_status_cli_enforced_all_non_archive_allowed_transitions_write
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_feature_status_cli_enforced_archived_terminal_does_not_write
- [x] AC004 -> tests/test_features.py::FeatureBundleTests::test_feature_status_cli_enforced_mixed_status_fails_before_write
- [x] AC004 -> tests/test_features.py::FeatureBundleTests::test_feature_status_cli_enforced_missing_status_fails_before_write
- [x] AC005 -> tests/test_features.py::FeatureBundleTests::test_feature_status_cli_enforced_archive_requires_ready_gate
- [x] AC005 -> tests/test_features.py::FeatureBundleTests::test_feature_status_cli_enforced_archive_ready_bundle_succeeds
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_feature_status_cli_enforced_allowed_transition_writes_files
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_feature_status_cli_enforced_disallowed_transition_does_not_write
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_feature_status_cli_enforced_failure_does_not_leak_environment_tokens
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_feature_status_cli_rejects_invalid_status_and_slug
- [x] AC007 -> tests/test_agents.py::AgentsTests::test_agents_content_includes_required_commands_and_boundaries
- [x] AC007 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_feature_transition_policy_dogfood_bundle_passes_default_and_coverage_gates

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-transition-policy . --json`.
- Run the requested repository token-prefix scan and confirm no credential token prefixes are present.

## Review Notes

- The transition graph is intentionally conservative and explicit.
- Readiness and transition validity remain separate: archive edges can exist, but the readiness gate blocks incomplete bundles.
- JSON failures include transition context and readiness blockers but no environment values.

## Release Readiness

- [x] The feature bundle has complete spec, execution, and quality peer files.
- [x] Lifecycle status is `validated` across all peer files.
- [x] Acceptance criteria, tasks, required checks, test plan, and release readiness evidence are complete.
- [x] Local verification commands are defined for the implementation round.
