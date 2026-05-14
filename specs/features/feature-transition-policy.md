# Feature Transition Policy

Feature ID: feature-transition-policy
Status: validated

## Why

Native feature status updates are intentionally file-native and manually editable, but agents need an optional guardrail when lifecycle order matters. The transition policy lets teams ask for ordered state changes and archive readiness without breaking existing status workflows.

## Users

- Implementation agents moving native feature bundles through planned, implementation, review, and validation states.
- Reviewers who want archive attempts to prove that the feature readiness gate already passes.
- Maintainers preserving manual status override behavior for repair and dogfood workflows.

## Scope

- Add `--enforce-transition` to `specspine feature status <slug> [path] --set STATUS`.
- Preserve default `--set` behavior when the flag is absent.
- Enforce the allowed lifecycle graph only when the flag is present.
- Reject enforced updates before writing when the current peer status is missing, mixed, inconsistent, unsupported, or archived terminal.
- Require the existing `feature ready` gate to pass before an enforced archive write.
- Return stable JSON success and failure payloads with transition context.

## Non-Goals

- Making transition enforcement the default behavior.
- Replacing the readiness gate with lifecycle rules.
- Inferring readiness from status alone.
- Adding dependencies, remote service calls, token reads, or upstream CLI calls.

## Acceptance Criteria

- [x] `specspine feature status <slug> [path] --set STATUS --enforce-transition [--json]` is accepted by the CLI.
- [x] Default status updates still allow arbitrary supported status changes when `--enforce-transition` is absent.
- [x] Enforced updates allow only the documented transition graph and treat `archived` as terminal.
- [x] Enforced updates fail before writing when peer statuses are missing, mixed, inconsistent, or unsupported.
- [x] Enforced archive updates run the feature readiness gate first and report blockers when the gate is not ready.
- [x] JSON success payloads include transition context, and JSON failures include a stable error payload without token or environment leakage.
- [x] Documentation and agent instructions describe the policy as opt-in.
