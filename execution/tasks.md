# Tasks

## Completed

- [x] Implement zero-dependency CLI entry point.
- [x] Implement `specspine init` base workspace generation.
- [x] Implement `specspine agents init` project-local agent instructions.
- [x] Implement `specspine feature new` native feature bundles.
- [x] Implement `specspine feature issue` offline GitHub issue drafts.
- [x] Implement `specspine feature status` native lifecycle state query/update.
- [x] Implement `specspine fuse` adapter-mode fusion generation.
- [x] Implement `specspine status . --json`.
- [x] Implement `specspine status . --json --validate` validation summaries.
- [x] Implement `specspine validate . --fusion --features`.
- [x] Document upstream adapter policy without vendoring upstream code.
- [x] Initialize this repository as a complete SpecSpine fusion workspace.
- [x] Dogfood the feature lifecycle with `feature-status-lifecycle`.
- [x] Dogfood status validation summaries with `status-validation-summary`.

## Next

- [ ] Monitor whether agents prefer `status --json --validate` as the default startup packet.
- [ ] Revisit generated templates after dogfooding this workspace for one or more development cycles.
- [ ] Add tests when template or validation behavior changes.
- [ ] Keep README/docs aligned with any command surface changes.
- [ ] Continue to avoid GitHub token reads/writes and API calls in default workflows.
