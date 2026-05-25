from __future__ import annotations

__all__ = [
    "RELEASE_READINESS_CHECKS",
    "RELEASE_READINESS_TEMPLATE",
]

RELEASE_READINESS_CHECKS: tuple[str, ...] = (
    "RR001: Acceptance criteria, tasks, required checks, and test plan evidence are complete.",
    "RR002: Docs, release notes, or `specspine feature pr {slug} . --json` output are ready for reviewers.",
    "RR003: `specspine tests impact . --feature {slug} --json` has been reviewed for focused local test commands.",
    "RR004: `specspine consistency scan . --feature {slug} --json` has been reviewed for local spec-code-test-doc drift.",
    "RR005: `specspine hygiene scan . --json` has been reviewed for generated artifacts and denylisted repository residue.",
    "RR006: `specspine retrospective report . --json` has been reviewed for local feature improvement signals.",
    "RR007: `specspine coverage plan . --feature {slug} --json` has been reviewed if missing AC coverage remains.",
    "RR008: `specspine verify matrix {slug} . --json` has been reviewed for AC-level verification evidence.",
    "RR009: `specspine change risk . --feature {slug} --json` has been reviewed for changed-path risk evidence.",
    "RR010: `specspine security cues . --feature {slug} --json` has been reviewed for security-sensitive cues.",
    "RR011: `specspine provenance manifest . --feature {slug} --json` has been reviewed for local evidence hashes.",
    "RR012: `specspine review packet . --feature {slug} --json` has been reviewed for local pre-merge evidence.",
    "RR013: `specspine feature sync-plan {slug} . --json` or `--output-dir .specspine/sync-plan/{slug}` has been reviewed before any remote GitHub sync.",
    "RR014: `specspine feature archive {slug} . --json` has been reviewed before marking status archived.",
    "RR015: `specspine feature ready {slug} . --json` and `specspine validate . --fusion --features` have been run.",
    "RR016: No known blockers remain, or blockers are documented in review notes.",
)

RELEASE_READINESS_TEMPLATE = "\n".join(
    f"- [ ] {check}" for check in RELEASE_READINESS_CHECKS
)
