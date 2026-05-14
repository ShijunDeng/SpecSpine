# Feature Summary Filters Quality

Feature ID: feature-summary-filters
Status: validated
Why: Filtering and sorting are agent-facing triage behavior, so they must remain deterministic, local, and compatible with compact startup status.

## Required Checks

- [x] Unit tests verify default feature summaries remain compatible and default `status --json` stays compact.
- [x] Unit tests verify `--feature-status` single and repeated filters.
- [x] Unit tests verify `--feature-ready` ready and not-ready aliases.
- [x] Unit tests verify every supported `--feature-sort` key and descending order.
- [x] Unit tests verify no-match JSON returns an empty list and text output shows `none`.
- [x] Unit tests verify summary filter and sort options without `--feature-summaries` return code `2`.
- [x] Unit tests verify unsupported status, readiness, and sort values return code `2`.
- [x] Dogfood validation verifies this bundle has consistent `validated` lifecycle status.
- [x] Dogfood readiness verifies this bundle passes the local feature gate.

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine status . --json --validate --feature-summaries --feature-status validated --feature-ready yes --feature-sort slug`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-summary-filters . --json`.
- Run the repository token-prefix scan requested for this feature.

## Review Notes

- The status command still composes local feature summary evidence and does not call GitHub, upstream tools, network services, or token-backed APIs.
- Default status output remains compact because feature summaries and their filters are opt-in.
- Invalid option handling returns code `2` before status construction so unsupported values are not silently ignored.

## Release Readiness

- [x] Default status compatibility is preserved.
- [x] Feature summary filters and sorting are deterministic and local.
- [x] Documentation and agent guidance describe the new triage flags.
- [x] Validation and dogfood readiness pass.
