# Quality Checklist

## Required Checks

- [x] Workspace artifacts exist for intent, product, architecture, execution, and quality. [severity: high] [owner: maintainers]
- [x] Fusion artifacts exist for OpenSpec, Spec Kit, and Superpowers. [severity: medium] [owner: maintainers]
- [x] `.specspine/fusion.yaml` keeps `integration_mode: adapter`. [severity: critical] [owner: architecture]
- [x] `.specspine/fusion.yaml` keeps `vendored_upstream_code: false`. [severity: critical] [owner: architecture]
- [x] Default workflows do not require GitHub tokens or GitHub API calls. [severity: critical] [owner: security]
- [x] Run `PYTHONPATH=src python3 -m unittest discover -s tests` before completion. [severity: high] [owner: qa] [ci: unit-tests]
- [x] Run `PYTHONPATH=src python3 -m specspine feature tasks feature-task-export . --json` before completion. [severity: medium] [owner: maintainers] [ci: feature-task-export]
- [x] Run `PYTHONPATH=src python3 -m specspine status . --json` before completion. [severity: medium] [owner: maintainers] [ci: status-json]
- [x] Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features` before completion. [severity: high] [owner: qa] [ci: validation]
- [x] Run the repository token-prefix scan before completion; keep token prefixes out of project files. [severity: critical] [owner: security] [ci: token-prefix-scan]

## Definition Of Done

- Status reports both `workspace.complete=true` and `fusion.complete=true`.
- Validation passes with `--fusion --features`; native feature bundles use allowed statuses consistently across peer files.
- `feature tasks feature-task-export --json` returns ordered task records from this repository's dogfood execution file.
- Unit tests pass.
- Agent-facing docs describe the current project and do not leave placeholder template prompts.
- Upstream integrations remain external adapters unless a future spec explicitly changes the policy.
