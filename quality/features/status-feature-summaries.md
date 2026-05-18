# Status Feature Summaries Quality

Feature ID: status-feature-summaries
Status: validated
Why: The summary view must be compact, deterministic, local-only, and safe to use as an optional agent startup expansion.

## Required Checks

- [x] Unit tests verify default JSON status omits `feature_summaries`.
- [x] Unit tests verify JSON summaries include expected fields and counts.
- [x] Unit tests verify `--feature-summaries --validate --json` keeps validation output.
- [x] Unit tests verify default text output is unchanged and flagged text includes `Feature summaries`.
- [x] Unit tests verify partial bundles include missing files, gaps, blocking counts, and next actions.
- [x] Unit tests verify invalid feature slugs do not crash status.
- [x] Agent template tests verify the new optional startup guidance.
- [x] Dogfood readiness tests verify this bundle is validated and ready.

## Test Coverage

- [x] AC001 -> tests/test_status.py::StatusTests::test_status_json_cli_can_include_feature_summaries
- [x] AC001 -> tests/test_status.py::StatusTests::test_status_json_cli_validate_preserves_feature_summaries
- [x] AC001 -> tests/test_status.py::StatusTests::test_status_validate_with_adapters_preserves_feature_summaries
- [x] AC002 -> tests/test_status.py::StatusTests::test_status_json_cli_output_is_parseable
- [x] AC003 -> tests/test_status.py::StatusTests::test_status_json_cli_can_include_feature_summaries
- [x] AC004 -> tests/test_status.py::StatusTests::test_status_text_feature_summaries_are_opt_in
- [x] AC005 -> tests/test_status.py::StatusTests::test_status_feature_summary_reports_partial_bundle_actions
- [x] AC006 -> tests/test_status.py::StatusTests::test_status_feature_summary_handles_invalid_slug_files
- [x] AC007 -> tests/test_agents.py::AgentsTests::test_agents_content_includes_required_commands_and_boundaries
- [x] AC007 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_status_feature_summaries_dogfood_bundle_passes_default_and_coverage_gates

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine status . --json --validate --feature-summaries`.
- Run `PYTHONPATH=src python3 -m specspine feature ready status-feature-summaries . --json`.
- Run the repository token-prefix scan requested for this feature.

## Review Notes

- The status command composes existing local feature handoff evidence and does not invoke GitHub, upstream tools, network services, or token reads.
- The default status payload remains compact to avoid expanding every agent startup context.
- Invalid filename handling follows feature discovery behavior by recording the discovered slug and returning not-ready summary information instead of failing the entire workspace status command.

## Release Readiness

- [x] Default status compatibility is preserved.
- [x] Optional summaries are deterministic and bounded.
- [x] Documentation and agent guidance describe when to request summaries.
- [x] Validation and dogfood readiness pass.
