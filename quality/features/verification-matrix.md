# Verification Matrix Quality

Feature ID: verification-matrix
Status: validated
Why: A verification matrix is useful only if it stays local, clearly maps each AC to evidence, and avoids claiming that coverage metadata proves tests ran.

## Required Checks

- [x] Unit tests cover verified rows when checked ACs have checked local coverage targets.
- [x] Unit tests cover unverified rows when coverage targets are missing.
- [x] Unit tests cover structured missing feature output and invalid slug behavior.
- [x] Unit tests guard against subprocess execution, network access, GitHub access, upstream CLI execution, environment reads, and token reads.
- [x] Documentation and agent guidance list the command and advisory-only safety contract.
- [x] Generated feature templates include verification matrix handoff and release-readiness guidance.
- [x] The dogfood bundle is validated across spec, execution, and quality peer files.

## Test Coverage

- [x] AC001 -> tests/test_verification.py::VerificationMatrixTests::test_cli_json_and_exit_codes
- [x] AC002 -> tests/test_verification.py::VerificationMatrixTests::test_builder_is_local_only_and_renderers_are_pure
- [x] AC003 -> tests/test_verification.py::VerificationMatrixTests::test_verified_row_when_acceptance_criterion_has_existing_checked_coverage
- [x] AC004 -> tests/test_verification.py::VerificationMatrixTests::test_verified_row_when_acceptance_criterion_has_existing_checked_coverage
- [x] AC005 -> tests/test_verification.py::VerificationMatrixTests::test_unverified_row_when_coverage_target_is_missing
- [x] AC006 -> tests/test_verification.py::VerificationMatrixTests::test_missing_feature_returns_structured_report
- [x] AC006 -> tests/test_verification.py::VerificationMatrixTests::test_invalid_feature_slug_is_rejected
- [x] AC006 -> tests/test_verification.py::VerificationMatrixTests::test_cli_json_and_exit_codes
- [x] AC007 -> tests/test_verification.py::VerificationMatrixTests::test_builder_is_local_only_and_renderers_are_pure
- [x] AC008 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_verification_matrix_documentation_and_dogfood_describe_workflow
- [x] AC008 -> tests/test_features.py::FeatureBundleTests::test_create_feature_bundle_in_plain_workspace
- [x] AC008 -> tests/test_agents.py::AgentsTests::test_agents_content_includes_required_commands_and_boundaries

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_verification`.
- Run `PYTHONPATH=src python3 -m unittest tests.test_features tests.test_agents tests.test_dogfood_artifacts`.
- Run `PYTHONPATH=src python3 -m specspine verify matrix verification-matrix . --json`.
- Run `PYTHONPATH=src python3 -m specspine verify matrix missing-feature . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready verification-matrix . --json --require-coverage`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.

## Review Notes

- The matrix reports local evidence records only; it deliberately avoids executing recommended commands.
- A `verified` row means the AC is checked and has at least one checked existing coverage link, not that tests were run.
- Missing feature bundles still return a JSON report so callers can surface blockers consistently.

## Release Readiness

- [x] `verification-matrix` has complete spec, execution, and quality peer files.
- [x] Lifecycle status is `validated` across all peer files.
- [x] Acceptance criteria, implementation tasks, required checks, test coverage links, and release readiness evidence are complete.
- [x] Focused verification matrix tests pass.
- [x] Project documentation and generated templates describe the verification workflow.
