# Tasks

## Completed

- [x] Implement zero-dependency CLI entry point.
- [x] Implement `specspine init` base workspace generation.
- [x] Implement `specspine agents init` project-local agent instructions.
- [x] Implement `specspine feature new` native feature bundles.
- [x] Implement `specspine feature issue` offline GitHub issue drafts.
- [x] Implement `specspine feature status` native lifecycle state query/update.
- [x] Implement opt-in `specspine feature status --enforce-transition` lifecycle transition policy.
- [x] Implement `specspine feature tasks` execution checklist export.
- [x] Implement `specspine feature trace` traceability handoff export.
- [x] Implement `specspine feature ready` per-feature readiness gate.
- [x] Implement `specspine feature handoff` compact agent handoff packet export.
- [x] Implement `specspine feature pr` offline Pull Request draft export.
- [x] Implement `specspine fuse` adapter-mode fusion generation.
- [x] Implement `specspine status . --json`.
- [x] Implement `specspine status . --json --validate` validation summaries.
- [x] Implement `specspine status . --json --feature-summaries` optional native feature summaries.
- [x] Implement `specspine validate . --fusion --features`.
- [x] Document upstream adapter policy without vendoring upstream code.
- [x] Initialize this repository as a complete SpecSpine fusion workspace.
- [x] Dogfood the feature lifecycle with `feature-status-lifecycle`.
- [x] Dogfood status validation summaries with `status-validation-summary`.
- [x] Dogfood task export with `feature-task-export`.
- [x] Dogfood traceability export with `feature-traceability-export`.
- [x] Dogfood readiness gate with `feature-readiness-gate`.
- [x] Dogfood handoff packet export with `feature-handoff-packet`.
- [x] Dogfood workspace feature summaries with `status-feature-summaries`.
- [x] Dogfood enforced transition policy with `feature-transition-policy`.
- [x] Dogfood offline Pull Request draft export with `feature-pr-draft`.

## Next

- [ ] Observe whether implementation, acceptance, and review agents use `feature handoff --json` as their default feature packet.
- [ ] Observe whether implementation agents still need focused `feature tasks --json` after reading the handoff packet.
- [ ] Observe whether reviewers prefer `feature trace --json` as the default traceability packet.
- [ ] Observe whether reviewers and CI jobs prefer `feature ready --json` for per-feature release gates.
- [ ] Observe whether reviewers use `feature pr --json` as the local bridge from feature evidence into Pull Request review.
- [ ] Monitor whether agents prefer `status --json --validate` as the default startup packet.
- [ ] Observe whether agents use `status --json --validate --feature-summaries` only when comparing multiple features.
- [ ] Revisit generated templates after dogfooding this workspace for one or more development cycles.
- [ ] Add tests when template or validation behavior changes.
- [ ] Keep README/docs aligned with any command surface changes.
- [ ] Continue to avoid GitHub token reads/writes and API calls in default workflows.
