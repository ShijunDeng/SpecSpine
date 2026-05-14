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
