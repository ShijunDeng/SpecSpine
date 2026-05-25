from __future__ import annotations

from ..workspace import normalize_template


def build_agent_handoff(resolved_slug: str) -> str:
    return normalize_template(f"""
## Agent Handoff

- Run `specspine feature handoff {resolved_slug} . --json` before implementation or review handoff.
- Run `specspine adapters handoff {resolved_slug} . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks {resolved_slug} . --json` for the focused implementation checklist.
- Run `specspine feature task-issues {resolved_slug} . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace {resolved_slug} . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests {resolved_slug} . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature {resolved_slug} --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature {resolved_slug} --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine coverage plan . --feature {resolved_slug} --json` when missing AC coverage needs read-only remediation steps.
- Run `specspine verify matrix {resolved_slug} . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature {resolved_slug} --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature {resolved_slug} --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature {resolved_slug} --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature {resolved_slug} --json` to compose local pre-merge review evidence.
- Run `specspine feature ready {resolved_slug} . --json` after implementation evidence is complete.
- Run `specspine feature pr {resolved_slug} . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan {resolved_slug} . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan {resolved_slug} . --output-dir .specspine/sync-plan/{resolved_slug}` to materialize local sync review artifacts.
- Run `specspine feature archive {resolved_slug} . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
""")


__all__ = [
    "build_agent_handoff",
]
