# Feature Test Packet Quality

Feature ID: feature-test-packet
Status: validated
Why: The acceptance-test packet is valuable only if it is deterministic, local, non-generative, token-free, and honest about missing evidence.

## Required Checks

- [x] Unit tests cover `feature tests` JSON and text output for ready bundles.
- [x] Unit tests cover deterministic `TC001 -> AC001` mapping from acceptance criteria.
- [x] Unit tests cover partial bundles with missing files, trace gaps, empty test plan or quality sections, and blocking readiness checks.
- [x] Unit tests cover missing bundles returning a packet and non-zero exit code.
- [x] Unit tests cover invalid slugs returning exit code `2`.
- [x] Unit tests cover `--output`, overwrite refusal, `--force`, and `--json --output`.
- [x] Unit tests cover operation without GitHub tokens, `gh`, network access, upstream CLIs, or new dependencies.
- [x] Documentation, agent guidance, and dogfood artifacts describe the acceptance-test packet.

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-test-packet . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature tests feature-test-packet . --json`.
- Run the requested repository credential-prefix scan and confirm no token prefixes are present.

## Review Notes

- The command composes existing local reports and peer files; it does not invent feature behavior beyond the deterministic AC-to-TC wrapper.
- Test cases intentionally remain pending checklist items because the packet is context for testing, not proof that tests were run.
- Partial bundles stay exportable so QA agents can see missing quality evidence before asking another agent to repair the bundle.

## Release Readiness

- [x] `feature-test-packet` has complete spec, execution, and quality peer files.
- [x] Lifecycle status is `validated` across all peer files.
- [x] Acceptance criteria, tasks, required checks, test plan, and release readiness evidence are complete.
- [x] Local verification commands for this round pass.
