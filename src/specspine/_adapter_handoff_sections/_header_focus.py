from __future__ import annotations

__all__ = [
    "render_header_lines",
    "render_adapter_focus_lines",
]


def render_header_lines(report, adapter_key: str) -> list[str]:
    adapter = report.adapters[adapter_key]
    return [
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
    ]


def render_adapter_focus_lines(report, adapter_key: str) -> list[str]:
    adapter = report.adapters[adapter_key]
    return [
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
    ]
