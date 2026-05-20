from __future__ import annotations

import hashlib
import json
import shlex
from pathlib import Path
from typing import Iterable

from .adapter_lifecycle import build_adapter_lifecycle_report
from .adapter_models import (
    ADAPTER_HANDOFF_SAFETY_FLAGS,
    ADAPTER_LIFECYCLE_MAPPINGS,
    ADAPTER_SPECS,
    AdapterFeatureHandoffEntry,
    AdapterFeatureHandoffReport,
    AdapterHandoffArtifactExistsError,
    AdapterHandoffArtifacts,
    AdapterHandoffStep,
    AdapterLifecycleMapping,
)
from .features import (
    FeatureBundleNotFoundError,
    build_feature_handoff_report,
    feature_bundle_paths,
)

__all__ = [
    "adapter_feature_handoff_focused_payload",
    "build_adapter_feature_handoff_report",
    "render_adapter_feature_handoff_adapter_json",
    "render_adapter_feature_handoff_adapter_text",
    "render_adapter_feature_handoff_json",
    "render_adapter_feature_handoff_text",
    "write_adapter_feature_handoff_artifacts",
]


def _replace_slug(commands: Iterable[str], slug: str) -> tuple[str, ...]:
    return tuple(command.replace("<slug>", slug) for command in commands)


def _mapping_for_status(
    adapter_key: str,
    status: str,
) -> AdapterLifecycleMapping | None:
    for mapping in ADAPTER_LIFECYCLE_MAPPINGS[adapter_key]:
        if mapping.status == status:
            return mapping
    return None


def _openspec_steps(slug: str) -> tuple[AdapterHandoffStep, ...]:
    return (
        AdapterHandoffStep(
            id="openspec.status-json",
            kind="cli-command",
            description="Review OpenSpec change and spec status as JSON.",
            argv=("openspec", "status", "--json"),
        ),
        AdapterHandoffStep(
            id="openspec.instructions-apply",
            kind="cli-command",
            description="Apply OpenSpec agent instructions for the matching change id.",
            argv=(
                "openspec",
                "instructions",
                "apply",
                "--change",
                slug,
                "--json",
            ),
        ),
        AdapterHandoffStep(
            id="openspec.validate-all-json",
            kind="cli-command",
            description="Validate all OpenSpec artifacts and return JSON findings.",
            argv=("openspec", "validate", "--all", "--json"),
        ),
    )


def _speckit_steps(slug: str) -> tuple[AdapterHandoffStep, ...]:
    return (
        AdapterHandoffStep(
            id="speckit.spec",
            kind="agent-action",
            description="Prepare or review the Spec Kit spec artifact for this feature.",
            instruction=(
                f"Use Spec Kit's Spec phase for `{slug}` to capture scenarios, "
                "acceptance criteria, constraints, and user value from the local "
                "SpecSpine feature bundle."
            ),
        ),
        AdapterHandoffStep(
            id="speckit.plan",
            kind="agent-action",
            description="Prepare or review the Spec Kit plan artifact.",
            instruction=(
                f"Use Spec Kit's Plan phase for `{slug}` to turn the spec into "
                "architecture, research, contracts, and implementation shape."
            ),
        ),
        AdapterHandoffStep(
            id="speckit.tasks",
            kind="agent-action",
            description="Prepare or review the Spec Kit tasks artifact.",
            instruction=(
                f"Use Spec Kit's Tasks phase for `{slug}` to produce an ordered "
                "task list that traces back to the spec and plan artifacts."
            ),
        ),
        AdapterHandoffStep(
            id="speckit.implement",
            kind="agent-action",
            description="Hand the Spec Kit implement phase to an agent without running it from SpecSpine.",
            instruction=(
                f"Use Spec Kit's Implement phase for `{slug}` only after the "
                "Spec, Plan, and Tasks artifacts are reviewed as local context."
            ),
        ),
    )


def _superpowers_steps(_slug: str) -> tuple[AdapterHandoffStep, ...]:
    return (
        AdapterHandoffStep(
            id="superpowers.brainstorming",
            kind="agent-action",
            description="Use brainstorming to clarify intent and unresolved questions.",
            instruction="Apply the brainstorming skill before locking requirements or scope.",
        ),
        AdapterHandoffStep(
            id="superpowers.writing-plans",
            kind="agent-action",
            description="Use writing-plans to produce an executable implementation plan.",
            instruction="Apply the writing-plans skill and keep risks, tasks, and validation explicit.",
        ),
        AdapterHandoffStep(
            id="superpowers.test-driven-development",
            kind="agent-action",
            description="Use test-driven-development for behavior changes.",
            instruction="Apply test-driven-development so tests lead implementation where practical.",
        ),
        AdapterHandoffStep(
            id="superpowers.subagent-driven-development",
            kind="agent-action",
            description="Use subagent-driven-development for parallel review or implementation slices.",
            instruction="Apply subagent-driven-development when focused subagent handoffs reduce risk.",
        ),
        AdapterHandoffStep(
            id="superpowers.requesting-code-review",
            kind="agent-action",
            description="Use requesting-code-review before completion.",
            instruction="Apply requesting-code-review and capture findings in local review evidence.",
        ),
        AdapterHandoffStep(
            id="superpowers.verification-before-completion",
            kind="agent-action",
            description="Use verification-before-completion before marking the feature done.",
            instruction="Apply verification-before-completion and record the checks that passed.",
        ),
    )


def _recommended_steps(adapter_key: str, slug: str) -> tuple[AdapterHandoffStep, ...]:
    if adapter_key == "openspec":
        return _openspec_steps(slug)
    if adapter_key == "speckit":
        return _speckit_steps(slug)
    if adapter_key == "superpowers":
        return _superpowers_steps(slug)
    return ()


def _adapter_handoff_recommended_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature handoff {slug} . --json",
        "specspine adapters lifecycle . --json",
        f"specspine feature ready {slug} . --json",
        "specspine validate . --fusion --features",
    )


def build_adapter_feature_handoff_report(
    root: Path,
    slug: str,
) -> AdapterFeatureHandoffReport:
    feature_report = build_feature_handoff_report(root, slug)
    resolved_root = root.expanduser().resolve()
    if not feature_report.has_native_files:
        missing_paths = tuple(feature_bundle_paths(resolved_root, slug).values())
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=missing_paths,
        )

    lifecycle_report = build_adapter_lifecycle_report(resolved_root)
    source_files = tuple(
        str(source["path"])
        for source in feature_report.sources.values()
        if source["exists"]
    )

    adapters: dict[str, AdapterFeatureHandoffEntry] = {}
    for key in ADAPTER_SPECS:
        lifecycle_adapter = lifecycle_report.adapters[key]
        mapping = _mapping_for_status(key, feature_report.status)
        if mapping is None:
            upstream_phase = "No mapping selected"
            upstream_artifacts: tuple[str, ...] = ()
            agent_focus = (
                "Resolve the native feature status before handing work to this adapter."
            )
            local_commands: tuple[str, ...] = ()
            notes = (
                f"Native status `{feature_report.status}` has no adapter lifecycle mapping.",
                "SpecSpine did not execute upstream tools or inspect adapter runtime availability.",
            )
        else:
            upstream_phase = mapping.upstream_phase
            upstream_artifacts = mapping.upstream_artifacts
            agent_focus = mapping.agent_focus
            local_commands = _replace_slug(mapping.local_commands, slug)
            notes = (
                f"Selected mapping `{mapping.id}` for native status `{feature_report.status}`.",
                "Recommended upstream steps are handoff data only; SpecSpine did not execute them.",
            )

        adapters[key] = AdapterFeatureHandoffEntry(
            key=key,
            display_name=lifecycle_adapter.display_name,
            enabled=lifecycle_adapter.enabled,
            config=lifecycle_adapter.config,
            config_exists=lifecycle_adapter.config_exists,
            upstream_url=lifecycle_adapter.upstream_url,
            integration_surface=ADAPTER_SPECS[key].role,
            native_status=feature_report.status,
            upstream_phase=upstream_phase,
            upstream_artifacts=upstream_artifacts,
            agent_focus=agent_focus,
            local_commands=local_commands,
            recommended_upstream_steps=_recommended_steps(key, slug),
            notes=notes,
        )

    return AdapterFeatureHandoffReport(
        root=resolved_root,
        feature_id=feature_report.feature_id,
        status=feature_report.status,
        ready=feature_report.ready,
        sources=feature_report.sources,
        source_files=source_files,
        missing_files=feature_report.missing_files,
        gaps=feature_report.gaps,
        blocking_checks=feature_report.blocking_checks,
        feature_summary=feature_report.summary,
        adapters=adapters,
        recommended_commands=_adapter_handoff_recommended_commands(slug),
    )


def render_adapter_feature_handoff_json(report: AdapterFeatureHandoffReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def _adapter_handoff_blocking_checks(
    report: AdapterFeatureHandoffReport,
) -> list[dict[str, object]]:
    return [
        check.as_dict() if hasattr(check, "as_dict") else dict(check)
        for check in report.blocking_checks
    ]


def adapter_feature_handoff_focused_payload(
    report: AdapterFeatureHandoffReport,
    adapter_key: str,
) -> dict[str, object]:
    return {
        "adapter": report.adapters[adapter_key].as_dict(),
        "blocking_checks": _adapter_handoff_blocking_checks(report),
        "feature_id": report.feature_id,
        "gaps": [dict(gap) for gap in report.gaps],
        "missing_files": list(report.missing_files),
        "ready": report.ready,
        "recommended_commands": list(report.recommended_commands),
        "safety_flags": dict(ADAPTER_HANDOFF_SAFETY_FLAGS),
        "source_files": list(report.source_files),
        "status": report.status,
        "summary": report.summary,
    }


def render_adapter_feature_handoff_adapter_json(
    report: AdapterFeatureHandoffReport,
    adapter_key: str,
) -> str:
    return (
        json.dumps(
            adapter_feature_handoff_focused_payload(report, adapter_key),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def _render_step_line(step: AdapterHandoffStep) -> str:
    if step.argv:
        command = " ".join(shlex.quote(part) for part in step.argv)
        detail = f"`{command}`"
    else:
        detail = step.instruction
    return (
        f"- {step.id} ({step.kind}): {step.description} "
        f"executed=no safe_to_auto_run=no creates_remote=no "
        f"requires_network=no requires_token=no"
        + (f" - {detail}" if detail else "")
    )


def render_adapter_feature_handoff_text(
    report: AdapterFeatureHandoffReport,
) -> str:
    summary = report.summary
    adapters_summary = summary["adapters"]
    steps_summary = summary["steps"]
    lines = [
        f"# Adapter Feature Handoff: {report.feature_id}",
        "",
        "## Feature",
        "",
        f"- Status: {report.status}",
        f"- Ready: {'yes' if report.ready else 'no'}",
        f"- Source files: {len(report.source_files)}",
        f"- Missing files: {len(report.missing_files)}",
        f"- Gaps: {summary['gaps']['total']}",
        f"- Blocking checks: {summary['blocking_checks']['total']}",
        (
            "- Summary: "
            f"adapters={adapters_summary['total']} "
            f"enabled={adapters_summary['enabled']} "
            f"config_exists={adapters_summary['config_exists']} "
            f"steps={steps_summary['total']}"
        ),
        "",
        "## Sources",
        "",
    ]
    for kind, source in report.sources.items():
        marker = "ok" if source["exists"] else "missing"
        lines.append(f"- [{marker}] {kind}: {source['path']}")

    lines.extend(["", "## Gaps", ""])
    if report.gaps:
        lines.extend(
            f"- {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in report.gaps
        )
    else:
        lines.append("- None.")

    lines.extend(["", "## Blocking Checks", ""])
    if report.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in report.blocking_checks
        )
    else:
        lines.append("- None.")

    lines.extend(["", "## Adapters", ""])
    for key in ADAPTER_SPECS:
        adapter = report.adapters[key]
        lines.extend(
            [
                f"### {adapter.display_name} ({adapter.key})",
                "",
                f"- Enabled: {'yes' if adapter.enabled else 'no'}",
                f"- Config: {adapter.config} (exists: {'yes' if adapter.config_exists else 'no'})",
                f"- Upstream: {adapter.upstream_url}",
                f"- Integration surface: {adapter.integration_surface}",
                f"- Native status: {adapter.native_status}",
                f"- Upstream phase: {adapter.upstream_phase}",
                f"- Agent focus: {adapter.agent_focus}",
                "- Upstream artifacts:",
            ]
        )
        if adapter.upstream_artifacts:
            lines.extend(f"  - {artifact}" for artifact in adapter.upstream_artifacts)
        else:
            lines.append("  - None.")
        lines.append("- Local commands:")
        if adapter.local_commands:
            lines.extend(f"  - `{command}`" for command in adapter.local_commands)
        else:
            lines.append("  - None.")
        lines.append("- Recommended upstream steps:")
        if adapter.recommended_upstream_steps:
            lines.extend(
                f"  {_render_step_line(step)}"
                for step in adapter.recommended_upstream_steps
            )
        else:
            lines.append("  - None.")
        lines.append("- Notes:")
        lines.extend(f"  - {note}" for note in adapter.notes)
        lines.append("")

    lines.extend(["## Recommended Local Commands", ""])
    lines.extend(f"- `{command}`" for command in report.recommended_commands)

    return "\n".join(lines).rstrip() + "\n"


def render_adapter_feature_handoff_adapter_text(
    report: AdapterFeatureHandoffReport,
    adapter_key: str,
) -> str:
    adapter = report.adapters[adapter_key]
    lines = [
        f"# {adapter.display_name} Adapter Handoff: {report.feature_id}",
        "",
        "## Feature",
        "",
        f"- Status: {report.status}",
        f"- Ready: {'yes' if report.ready else 'no'}",
        f"- Missing files: {len(report.missing_files)}",
        f"- Gaps: {len(report.gaps)}",
        f"- Blocking checks: {len(report.blocking_checks)}",
        "",
        "## Adapter Focus",
        "",
        f"- Adapter: {adapter.display_name} ({adapter.key})",
        f"- Enabled: {'yes' if adapter.enabled else 'no'}",
        f"- Config: {adapter.config} (exists: {'yes' if adapter.config_exists else 'no'})",
        f"- Upstream: {adapter.upstream_url}",
        f"- Integration surface: {adapter.integration_surface}",
        f"- Native status: {adapter.native_status}",
        f"- Upstream phase: {adapter.upstream_phase}",
        f"- Agent focus: {adapter.agent_focus}",
        "",
        "## Upstream Artifacts",
        "",
    ]
    if adapter.upstream_artifacts:
        lines.extend(f"- {artifact}" for artifact in adapter.upstream_artifacts)
    else:
        lines.append("- None.")

    lines.extend(["", "## Local Commands", ""])
    if adapter.local_commands:
        lines.extend(f"- `{command}`" for command in adapter.local_commands)
    else:
        lines.append("- None.")

    lines.extend(["", "## Recommended Upstream Steps", ""])
    if adapter.recommended_upstream_steps:
        lines.extend(_render_step_line(step) for step in adapter.recommended_upstream_steps)
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "## Safety",
            "",
            "- executed=false",
            "- requires_network=false",
            "- requires_token=false",
            "- creates_remote=false",
            "- safe_to_auto_run=false",
            (
                "- Artifact export does not execute upstream tools, subprocesses, "
                "network calls, GitHub operations, or token reads."
            ),
            "",
            "## Notes",
            "",
        ]
    )
    lines.extend(f"- {note}" for note in adapter.notes)
    return "\n".join(lines).rstrip() + "\n"


def _adapter_handoff_artifact_manifest(
    report: AdapterFeatureHandoffReport,
    artifact_checksums: dict[str, str],
) -> dict[str, object]:
    adapter_artifacts = {
        key: f"adapters/{key}.md"
        for key in ADAPTER_SPECS
    }
    adapter_json_artifacts = {
        key: f"adapters/{key}.json"
        for key in ADAPTER_SPECS
    }
    return {
        "artifact_version": 1,
        "artifact_root": ".",
        "artifact_checksums": artifact_checksums,
        "artifacts": {
            "manifest": "manifest.json",
            "combined": "combined.md",
            "combined_json": "combined.json",
            "adapters": adapter_artifacts,
            "adapter_json": adapter_json_artifacts,
        },
        "blocking_checks": _adapter_handoff_blocking_checks(report),
        "checksum_algorithm": "sha256",
        "feature_id": report.feature_id,
        "gaps": [dict(gap) for gap in report.gaps],
        "missing_files": list(report.missing_files),
        "ready": report.ready,
        "safety_flags": dict(ADAPTER_HANDOFF_SAFETY_FLAGS),
        "safety_notes": [
            (
                "Artifact export does not execute upstream tools, subprocesses, "
                "network calls, GitHub operations, or token reads."
            ),
            "Recommended upstream steps are review data only.",
        ],
        "source_files": list(report.source_files),
        "status": report.status,
        "summary": report.summary,
    }


def _sha256_hex(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def write_adapter_feature_handoff_artifacts(
    report: AdapterFeatureHandoffReport,
    output_dir: Path,
    *,
    force: bool = False,
) -> AdapterHandoffArtifacts:
    resolved_output_dir = output_dir.expanduser().resolve()
    if resolved_output_dir.exists() and not resolved_output_dir.is_dir():
        raise NotADirectoryError(f"Output path is not a directory: {resolved_output_dir}")

    manifest_path = resolved_output_dir / "manifest.json"
    combined_path = resolved_output_dir / "combined.md"
    combined_json_path = resolved_output_dir / "combined.json"
    adapter_paths = tuple(
        resolved_output_dir / "adapters" / f"{key}.md"
        for key in ADAPTER_SPECS
    )
    adapter_json_paths = tuple(
        resolved_output_dir / "adapters" / f"{key}.json"
        for key in ADAPTER_SPECS
    )
    write_targets = (
        manifest_path,
        combined_path,
        combined_json_path,
        *adapter_paths,
        *adapter_json_paths,
    )

    parent_conflicts = tuple(
        path.parent
        for path in write_targets
        if path.parent.exists() and not path.parent.is_dir()
    )
    if parent_conflicts:
        first_conflict = parent_conflicts[0]
        raise NotADirectoryError(f"Output artifact parent is not a directory: {first_conflict}")

    existing_paths = tuple(path for path in write_targets if path.exists())
    if existing_paths and not force:
        raise AdapterHandoffArtifactExistsError(
            output_dir=resolved_output_dir,
            existing_paths=existing_paths,
        )

    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    (resolved_output_dir / "adapters").mkdir(parents=True, exist_ok=True)

    content_by_relative_path: dict[str, str] = {
        "combined.md": render_adapter_feature_handoff_text(report),
        "combined.json": render_adapter_feature_handoff_json(report),
    }
    for key in ADAPTER_SPECS:
        content_by_relative_path[f"adapters/{key}.md"] = (
            render_adapter_feature_handoff_adapter_text(report, key)
        )
        content_by_relative_path[f"adapters/{key}.json"] = (
            render_adapter_feature_handoff_adapter_json(report, key)
        )

    artifact_checksums = {
        relative_path: _sha256_hex(content.encode("utf-8"))
        for relative_path, content in content_by_relative_path.items()
    }
    manifest = _adapter_handoff_artifact_manifest(report, artifact_checksums)

    for relative_path, content in content_by_relative_path.items():
        (resolved_output_dir / relative_path).write_text(content, encoding="utf-8")
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return AdapterHandoffArtifacts(
        output_dir=resolved_output_dir,
        manifest_path=manifest_path,
        combined_path=combined_path,
        combined_json_path=combined_json_path,
        adapter_paths=adapter_paths,
        adapter_json_paths=adapter_json_paths,
        written_paths=write_targets,
        manifest=manifest,
    )
