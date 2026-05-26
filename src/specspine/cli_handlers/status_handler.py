"""Handler for the `status` CLI command."""

from __future__ import annotations

import sys
from pathlib import Path

from ..health import build_health_report, render_health_json, render_health_text
from ..status import (
    InvalidFeatureSummaryOption,
    parse_feature_summary_owner_filters,
    parse_feature_summary_metadata_filters,
    parse_feature_summary_priority_filters,
    parse_feature_summary_ready_filter,
    parse_feature_summary_sort_key,
    parse_feature_summary_status_filters,
    render_status_json,
    render_status_text,
)
from ..validation import (
    build_validation_report,
    build_validation_summary,
)
from ..policy import load_workspace_policy


def _get_cli_attr(name: str):
    """Access attribute through cli module namespace for test mock compatibility."""
    return getattr(sys.modules["specspine.cli"], name)


def handle_status(args) -> int:
    """Handle the status command. Extracted from cli._cmd_status."""
    if getattr(args, "health", False) or args.path == "health":
        health_path = "." if args.path == "health" else args.path
        try:
            report = build_health_report(Path(health_path))
        except OSError as error:
            print(f"Could not build health report: {error}", file=__import__("sys").stderr)
            return 1

        if args.json:
            print(render_health_json(report), end="")
        else:
            print(render_health_text(report), end="")
        return 0

    if args.validation_warnings and not args.validate:
        print("--validation-warnings requires --validate.", file=__import__("sys").stderr)
        return 2
    if args.readiness_policy and not args.readiness_summary:
        print("--readiness-policy requires --readiness-summary.", file=__import__("sys").stderr)
        return 2
    if args.readiness_require_coverage and not args.readiness_summary:
        print(
            "--readiness-require-coverage requires --readiness-summary.",
            file=__import__("sys").stderr,
        )
        return 2

    feature_summary_options_requested = bool(
        args.feature_status
        or args.feature_ready is not None
        or args.feature_priority
        or args.feature_owner
        or args.feature_milestone
        or args.feature_target_release
        or args.feature_project
        or args.feature_effort
        or args.feature_sort is not None
        or args.feature_sort_desc
        or args.feature_require_coverage
        or args.feature_policy
    )
    if feature_summary_options_requested and not args.feature_summaries:
        print(
            "--feature-status, --feature-ready, --feature-priority, "
            "--feature-owner, --feature-milestone, "
            "--feature-target-release, --feature-project, "
            "--feature-effort, --feature-sort, --feature-sort-desc, "
            "--feature-require-coverage, and --feature-policy "
            "require --feature-summaries.",
            file=__import__("sys").stderr,
        )
        return 2

    feature_summary_statuses: tuple[str, ...] = ()
    feature_summary_ready: bool | None = None
    feature_summary_priorities: tuple[str, ...] = ()
    feature_summary_owners: tuple[str, ...] = ()
    feature_summary_milestones: tuple[str, ...] = ()
    feature_summary_target_releases: tuple[str, ...] = ()
    feature_summary_projects: tuple[str, ...] = ()
    feature_summary_efforts: tuple[str, ...] = ()
    feature_summary_sort: str | None = None
    if args.feature_summaries:
        try:
            feature_summary_statuses = parse_feature_summary_status_filters(
                args.feature_status
            )
            feature_summary_ready = parse_feature_summary_ready_filter(
                args.feature_ready
            )
            feature_summary_priorities = parse_feature_summary_priority_filters(
                args.feature_priority
            )
            feature_summary_owners = parse_feature_summary_owner_filters(
                args.feature_owner
            )
            feature_summary_milestones = parse_feature_summary_metadata_filters(
                args.feature_milestone,
                default="unassigned",
            )
            feature_summary_target_releases = parse_feature_summary_metadata_filters(
                args.feature_target_release,
                default="unassigned",
            )
            feature_summary_projects = parse_feature_summary_metadata_filters(
                args.feature_project,
                default="unassigned",
            )
            feature_summary_efforts = parse_feature_summary_metadata_filters(
                args.feature_effort,
                default="unknown",
            )
            feature_summary_sort = parse_feature_summary_sort_key(args.feature_sort)
        except InvalidFeatureSummaryOption as error:
            print(str(error), file=__import__("sys").stderr)
            return 2

    status_kwargs = {
        "include_adapters": args.adapters,
        "include_feature_summaries": args.feature_summaries,
        "include_readiness_summary": args.readiness_summary,
        "feature_summary_statuses": feature_summary_statuses,
        "feature_summary_ready": feature_summary_ready,
        "feature_summary_priorities": feature_summary_priorities,
        "feature_summary_owners": feature_summary_owners,
        "feature_summary_milestones": feature_summary_milestones,
        "feature_summary_target_releases": feature_summary_target_releases,
        "feature_summary_projects": feature_summary_projects,
        "feature_summary_efforts": feature_summary_efforts,
        "feature_summary_sort": feature_summary_sort,
        "feature_summary_sort_desc": args.feature_sort_desc,
        "feature_summary_require_coverage": args.feature_require_coverage,
        "readiness_require_coverage": args.readiness_require_coverage,
        "readiness_use_policy": args.readiness_policy,
    }
    if args.feature_policy:
        status_kwargs["feature_summary_use_policy"] = True
    build_status = _get_cli_attr("build_status")
    status = build_status(Path(args.path), **status_kwargs)
    if args.validate:
        probe_adapters = _get_cli_attr("probe_adapters")
        report = build_validation_report(
            Path(args.path),
            include_fusion=True,
            include_features=True,
            include_adapters=args.adapters,
            adapter_probe=probe_adapters,
        )
        status["validation"] = build_validation_summary(
            report,
            included={
                "workspace": True,
                "fusion": True,
                "features": True,
                "adapters": bool(args.adapters),
            },
            include_warning_checks=args.validation_warnings,
        )
    if args.json:
        print(render_status_json(status), end="")
    else:
        print(render_status_text(status), end="")
    return 0
