# Feature Template Refresh Quality

Feature ID: feature-template-refresh
Status: validated
Why: The refreshed templates should guide new work into the current local workflow while staying deterministic, zero-dependency, and not ready by default.

## Required Checks

- [x] Unit tests cover refreshed spec, execution, and quality template sections.
- [x] Unit tests cover generated Agent Handoff commands.
- [x] Unit tests show a new generated bundle structurally validates while `feature ready` remains blocked.
- [x] Unit tests show `feature trace` and `feature tests` extract placeholder checklist and test-plan evidence.
- [x] Existing overwrite and `--force` behavior remains covered.
- [x] Documentation and agent guidance describe the focused handoff, tests, PR, ready, and validation workflow.
- [x] This dogfood bundle passes its own readiness gate.

## Test Coverage

- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_create_feature_bundle_in_plain_workspace
- [x] AC002 -> tests/test_features.py::FeatureBundleTests::test_create_feature_bundle_in_plain_workspace
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_create_feature_bundle_in_plain_workspace
- [x] AC004 -> tests/test_features.py::FeatureBundleTests::test_new_feature_bundle_validates_but_is_not_ready
- [x] AC005 -> tests/test_features.py::FeatureBundleTests::test_new_feature_bundle_trace_and_tests_extract_placeholders
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_create_feature_bundle_does_not_overwrite_existing_files
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_create_feature_bundle_force_overwrites_existing_files
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_feature_new_cli_does_not_overwrite_without_force
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_feature_new_cli_force_overwrites
- [x] AC007 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_agents_file_preserves_project_rules
- [x] AC007 -> tests/test_agents.py::AgentsTests::test_agents_content_includes_required_commands_and_boundaries
- [x] AC007 -> tests/test_features.py::FeatureBundleTests::test_create_feature_bundle_in_plain_workspace
- [x] AC008 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_feature_template_refresh_dogfood_bundle_passes_default_and_coverage_gates

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-template-refresh . --json`.
- Run the configured repository token-pattern scan.

## Review Notes

- Template content remains plain Markdown generated through the existing deterministic path.
- New checklist items are intentionally unchecked so a freshly generated bundle cannot pass `feature ready`.
- The execution template and handoff recommendations now point agents at the same local workflow commands.
- No new dependencies, flags, upstream calls, GitHub calls, or token reads are introduced.

## Release Readiness

- [x] Acceptance criteria and execution tasks are complete.
- [x] Unit tests, validation, feature readiness, and token-pattern scan commands pass.
- [x] README, docs, specs, execution plan, task list, quality review, root `AGENTS.md`, and generated agent template are updated.
- [x] Local PR draft workflow remains offline and token-free.
- [x] No known blockers remain.
