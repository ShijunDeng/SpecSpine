from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .adapters import (
    ADAPTER_SPECS,
    AGENT_PROFILES,
    AdapterHandoffArtifactExistsError,
    AdapterStatus,
    build_adapter_feature_handoff_report,
    build_adapter_lifecycle_report,
    build_upstream_init_commands,
    probe_adapters,
    render_adapter_feature_handoff_json,
    render_adapter_feature_handoff_text,
    render_adapter_lifecycle_json,
    render_adapter_lifecycle_text,
    run_upstream_initializers,
    write_adapter_feature_handoff_artifacts,
)
from .agents import AgentsFileExistsError, init_agents_file
from .analysis import (
    build_analysis_report,
    render_analysis_json,
    render_analysis_text,
)
from .archive import (
    FeatureArchiveArtifactExistsError,
    InvalidArchiveId,
    build_feature_archive_report,
    feature_archive_report_with_package,
    render_feature_archive_json,
    render_feature_archive_text,
    write_feature_archive_package,
)
from .coverage import (
    build_coverage_debt_report,
    render_coverage_debt_json,
    render_coverage_debt_text,
)
from .features import (
    FeatureBundleExistsError,
    FeatureBundleNotFoundError,
    FeatureSyncPlanArtifactExistsError,
    FeatureStatusTransitionError,
    InvalidFeatureStatus,
    InvalidFeatureSlug,
    build_feature_handoff_report,
    build_feature_ready_report,
    build_feature_task_issues_report,
    build_feature_sync_plan,
    build_feature_tests_report,
    build_feature_trace_report,
    build_feature_tasks_report,
    build_issue_draft,
    build_proposal_files,
    build_pull_request_draft,
    create_feature_bundle,
    create_proposal_bundle,
    get_feature_status,
    read_feature_metadata,
    render_feature_handoff_json,
    render_feature_handoff_text,
    render_feature_ready_json,
    render_feature_ready_text,
    render_feature_sync_plan_json,
    render_feature_sync_plan_text,
    render_feature_task_issues_json,
    render_feature_task_issues_text,
    render_feature_tests_json,
    render_feature_tests_text,
    render_feature_trace_json,
    render_feature_trace_text,
    render_feature_tasks_json,
    render_feature_tasks_text,
    render_issue_json,
    render_issue_text,
    render_pull_request_json,
    render_pull_request_text,
    set_feature_status,
    write_feature_sync_plan_artifacts,
)
from .fusion import FUSION_REQUIRED_FILES, init_fusion_workspace
from .gates import (
    build_quality_gate_report,
    render_quality_gate_json,
    render_quality_gate_text,
)
from .loop import (
    build_loop_packet,
    render_loop_packet_json,
    render_loop_packet_text,
)
from .policy import load_workspace_policy, render_policy_json, render_policy_text
from .status import (
    InvalidFeatureSummaryOption,
    build_status,
    parse_feature_summary_owner_filters,
    parse_feature_summary_metadata_filters,
    parse_feature_summary_priority_filters,
    parse_feature_summary_ready_filter,
    parse_feature_summary_sort_key,
    parse_feature_summary_status_filters,
    render_status_json,
    render_status_text,
)
from .validation import (
    build_validation_report,
    build_validation_summary,
    render_validation_json,
    render_validation_text,
    validation_exit_code,
)
from .workspace import BASE_WORKSPACE_FILES, check_workspace, init_workspace


def _print_created(paths: list[Path], root: Path) -> None:
    for path in paths:
        print(f"  created {path.relative_to(root)}")


def _generate_slug_from_intent(intent: str) -> str:
    from .proposer import generate_slug_from_intent

    return generate_slug_from_intent(intent)


def _print_adapter_statuses(statuses: list[AdapterStatus] | None = None) -> None:
    if statuses is None:
        statuses = probe_adapters()

    print("External adapters:")
    for status in statuses:
        marker = "ok" if status.available else "missing"
        version = f" ({status.version})" if status.version else ""
        print(f"  [{marker}] {status.display_name}{version}")
        print(f"      {status.detail}")
        if not status.available:
            print(f"      install: {status.install_hint}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="specspine",
        description="SpecSpine: the backbone for spec-driven AI execution.",
    )
    parser.add_argument("--version", action="version", version=f"specspine {__version__}")

    subcommands = parser.add_subparsers(dest="command", required=True)

    init_parser = subcommands.add_parser("init", help="initialize a SpecSpine workspace")
    init_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    init_parser.add_argument("--force", action="store_true", help="overwrite existing SpecSpine files")

    agents_parser = subcommands.add_parser("agents", help="manage AI coding agent instructions")
    agents_subcommands = agents_parser.add_subparsers(dest="agents_command", required=True)
    agents_init_parser = agents_subcommands.add_parser(
        "init",
        help="create project-local AGENTS.md instructions",
    )
    agents_init_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    agents_init_parser.add_argument("--force", action="store_true", help="overwrite AGENTS.md")

    fuse_parser = subcommands.add_parser(
        "fuse",
        help="initialize the OpenSpec + Spec Kit + Superpowers fusion layer",
    )
    fuse_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    fuse_parser.add_argument(
        "--agent",
        choices=sorted(AGENT_PROFILES),
        default="codex",
        help="AI coding agent profile used by upstream adapters",
    )
    fuse_parser.add_argument("--force", action="store_true", help="overwrite SpecSpine fusion files")
    fuse_parser.add_argument(
        "--run-upstream",
        action="store_true",
        help="run upstream initializer commands after writing SpecSpine files",
    )
    fuse_parser.add_argument("--skip-openspec", action="store_true", help="do not enable the OpenSpec adapter")
    fuse_parser.add_argument("--skip-speckit", action="store_true", help="do not enable the Spec Kit adapter")
    fuse_parser.add_argument("--skip-superpowers", action="store_true", help="do not enable the Superpowers adapter")

    feature_parser = subcommands.add_parser("feature", help="manage native SpecSpine features")
    feature_subcommands = feature_parser.add_subparsers(dest="feature_command", required=True)

    feature_new_parser = feature_subcommands.add_parser(
        "new",
        help="create a traceable feature bundle",
    )
    feature_new_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    feature_new_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    feature_new_parser.add_argument("--title", help="human-readable feature title")
    feature_new_parser.add_argument("--why", help="short reason this feature matters")
    feature_new_parser.add_argument("--force", action="store_true", help="overwrite existing feature files")

    feature_issue_parser = feature_subcommands.add_parser(
        "issue",
        help="draft a local GitHub issue from a native feature bundle",
    )
    feature_issue_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    feature_issue_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    feature_issue_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    feature_issue_parser.add_argument(
        "--output",
        help="write the issue body to a file instead of printing the text draft",
    )
    feature_issue_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing output file",
    )

    feature_pr_parser = feature_subcommands.add_parser(
        "pr",
        help="draft a local GitHub Pull Request from a native feature bundle",
    )
    feature_pr_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    feature_pr_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    feature_pr_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    feature_pr_parser.add_argument(
        "--output",
        help="write the PR body to a file instead of printing the text draft",
    )
    feature_pr_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing output file",
    )

    feature_tasks_parser = feature_subcommands.add_parser(
        "tasks",
        help="export executable checklist tasks from a native feature bundle",
    )
    feature_tasks_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    feature_tasks_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    feature_tasks_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    feature_tasks_parser.add_argument(
        "--output",
        help="write the text task list to a file instead of printing it",
    )
    feature_tasks_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing output file",
    )

    feature_task_issues_parser = feature_subcommands.add_parser(
        "task-issues",
        help="draft local GitHub issues from native feature execution tasks",
    )
    feature_task_issues_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    feature_task_issues_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    feature_task_issues_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    feature_task_issues_parser.add_argument(
        "--output",
        help="write the text issue draft package to a file instead of printing it",
    )
    feature_task_issues_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing output file",
    )

    feature_sync_plan_parser = feature_subcommands.add_parser(
        "sync-plan",
        help="plan local GitHub CLI sync commands without executing them",
    )
    feature_sync_plan_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    feature_sync_plan_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    feature_sync_plan_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    feature_sync_plan_parser.add_argument(
        "--output",
        help="write the text sync plan to a file instead of printing it",
    )
    feature_sync_plan_parser.add_argument(
        "--output-dir",
        help="write reviewable sync plan artifacts to a directory",
    )
    feature_sync_plan_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing output files written by this command",
    )

    feature_archive_parser = feature_subcommands.add_parser(
        "archive",
        help="package local archive evidence for a native feature bundle",
    )
    feature_archive_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    feature_archive_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    feature_archive_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    feature_archive_parser.add_argument(
        "--output-dir",
        help="write a compact archive package to a directory",
    )
    feature_archive_parser.add_argument(
        "--archive-id",
        help="stable archive id to include in the report and package",
    )
    feature_archive_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing archive package files written by this command",
    )

    feature_trace_parser = feature_subcommands.add_parser(
        "trace",
        help="export a traceability handoff from a native feature bundle",
    )
    feature_trace_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    feature_trace_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    feature_trace_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    feature_trace_parser.add_argument(
        "--output",
        help="write the text trace handoff to a file instead of printing it",
    )
    feature_trace_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing output file",
    )

    feature_handoff_parser = feature_subcommands.add_parser(
        "handoff",
        help="export a compact agent handoff packet from a native feature bundle",
    )
    feature_handoff_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    feature_handoff_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    feature_handoff_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    feature_handoff_parser.add_argument(
        "--output",
        help="write the text handoff packet to a file instead of printing it",
    )
    feature_handoff_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing output file",
    )

    feature_tests_parser = feature_subcommands.add_parser(
        "tests",
        help="export an acceptance-test packet from a native feature bundle",
    )
    feature_tests_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    feature_tests_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    feature_tests_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    feature_tests_parser.add_argument(
        "--output",
        help="write the text acceptance-test packet to a file instead of printing it",
    )
    feature_tests_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing output file",
    )

    feature_ready_parser = feature_subcommands.add_parser(
        "ready",
        help="check whether a native feature bundle passes the local readiness gate",
    )
    feature_ready_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    feature_ready_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    feature_ready_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    feature_ready_parser.add_argument(
        "--require-coverage",
        action="store_true",
        help="require completed local Test Coverage links for every acceptance criterion",
    )
    feature_ready_parser.add_argument(
        "--policy",
        action="store_true",
        help="apply workspace readiness policy when deciding whether coverage is required",
    )

    feature_status_parser = feature_subcommands.add_parser(
        "status",
        help="read or advance a native feature lifecycle status",
    )
    feature_status_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    feature_status_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    feature_status_parser.add_argument("--set", dest="set_status", help="set the feature lifecycle status")
    feature_status_parser.add_argument(
        "--enforce-transition",
        action="store_true",
        help="enforce ordered lifecycle transitions and archive readiness",
    )
    feature_status_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )

    doctor_parser = subcommands.add_parser("doctor", help="check SpecSpine workspace files")
    doctor_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    doctor_parser.add_argument(
        "--fusion",
        action="store_true",
        help="also require SpecSpine fusion files",
    )
    doctor_parser.add_argument(
        "--adapters",
        action="store_true",
        help="also check external adapter availability",
    )

    gates_parser = subcommands.add_parser("gates", help="export repository quality gate definitions")
    gates_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    gates_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )

    policy_parser = subcommands.add_parser("policy", help="export workspace readiness policy")
    policy_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    policy_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )

    coverage_parser = subcommands.add_parser("coverage", help="inspect local coverage evidence")
    coverage_subcommands = coverage_parser.add_subparsers(
        dest="coverage_command",
        required=True,
    )
    coverage_debt_parser = coverage_subcommands.add_parser(
        "debt",
        help="report native feature acceptance-criteria coverage debt",
    )
    coverage_debt_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    coverage_debt_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    coverage_debt_parser.add_argument(
        "--policy",
        action="store_true",
        help="only require coverage for features selected by workspace readiness policy",
    )

    analyze_parser = subcommands.add_parser(
        "analyze",
        help="analyze native feature consistency and coverage without changing files",
    )
    analyze_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    analyze_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    analyze_parser.add_argument(
        "--feature",
        metavar="SLUG",
        help="analyze one native feature slug",
    )
    analyze_parser.add_argument(
        "--fail-on-issues",
        action="store_true",
        help="return nonzero when analysis finds issues",
    )

    loop_parser = subcommands.add_parser("loop", help="export local agent loop packets")
    loop_subcommands = loop_parser.add_subparsers(dest="loop_command", required=True)
    loop_packet_parser = loop_subcommands.add_parser(
        "packet",
        help="export a deterministic local agent loop packet",
    )
    loop_packet_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    loop_packet_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    loop_packet_parser.add_argument(
        "--output",
        help="write the text packet to a file instead of printing it",
    )
    loop_packet_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing output file",
    )
    loop_packet_parser.add_argument(
        "--deadline",
        help="deadline value to include in the packet",
    )

    status_parser = subcommands.add_parser("status", help="summarize SpecSpine workspace status")
    status_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    status_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    status_parser.add_argument(
        "--adapters",
        action="store_true",
        help="also check external adapter availability",
    )
    status_parser.add_argument(
        "--validate",
        action="store_true",
        help="include a validation summary in the status output",
    )
    status_parser.add_argument(
        "--validation-warnings",
        action="store_true",
        help="include validation warning check details; requires --validate",
    )
    status_parser.add_argument(
        "--feature-summaries",
        "--features",
        dest="feature_summaries",
        action="store_true",
        help="include compact per-feature progress summaries and next actions",
    )
    status_parser.add_argument(
        "--readiness-summary",
        action="store_true",
        help="include a workspace rollup of native feature readiness gates",
    )
    status_parser.add_argument(
        "--readiness-require-coverage",
        action="store_true",
        help="require completed local Test Coverage links when computing readiness summary",
    )
    status_parser.add_argument(
        "--readiness-policy",
        action="store_true",
        help="apply workspace readiness policy when computing readiness summary",
    )
    status_parser.add_argument(
        "--feature-require-coverage",
        action="store_true",
        help="require completed local Test Coverage links when computing feature summary readiness",
    )
    status_parser.add_argument(
        "--feature-policy",
        action="store_true",
        help="apply workspace readiness policy when computing feature summary readiness",
    )
    status_parser.add_argument(
        "--feature-status",
        action="append",
        default=[],
        metavar="STATUS",
        help="filter feature summaries by lifecycle status; repeat to include more than one",
    )
    status_parser.add_argument(
        "--feature-ready",
        metavar="READY",
        help="filter feature summaries by readiness: yes, no, true, false, ready, or not-ready",
    )
    status_parser.add_argument(
        "--feature-priority",
        action="append",
        default=[],
        metavar="VALUE",
        help="filter feature summaries by priority: high, medium, low, or unknown",
    )
    status_parser.add_argument(
        "--feature-owner",
        action="append",
        default=[],
        metavar="VALUE",
        help="filter feature summaries by owner; repeat to include more than one",
    )
    status_parser.add_argument(
        "--feature-milestone",
        action="append",
        default=[],
        metavar="VALUE",
        help="filter feature summaries by milestone; repeat to include more than one",
    )
    status_parser.add_argument(
        "--feature-target-release",
        action="append",
        default=[],
        metavar="VALUE",
        help="filter feature summaries by target release; repeat to include more than one",
    )
    status_parser.add_argument(
        "--feature-project",
        action="append",
        default=[],
        metavar="VALUE",
        help="filter feature summaries by project; repeat to include more than one",
    )
    status_parser.add_argument(
        "--feature-effort",
        action="append",
        default=[],
        metavar="VALUE",
        help="filter feature summaries by effort; repeat to include more than one",
    )
    status_parser.add_argument(
        "--feature-sort",
        metavar="KEY",
        help="sort feature summaries by slug, status, ready, gaps, blocking, tasks-open, priority, milestone, target-release, project, or effort",
    )
    status_parser.add_argument(
        "--feature-sort-desc",
        action="store_true",
        help="reverse the selected feature summary sort order",
    )

    validate_parser = subcommands.add_parser("validate", help="validate SpecSpine workspace contracts")
    validate_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    validate_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for CI and agents",
    )
    validate_parser.add_argument(
        "--fusion",
        action="store_true",
        help="also require and validate SpecSpine fusion files",
    )
    validate_parser.add_argument(
        "--features",
        action="store_true",
        help="also validate native feature bundle consistency",
    )
    validate_parser.add_argument(
        "--adapters",
        action="store_true",
        help="also check enabled external adapter availability",
    )

    adapters_parser = subcommands.add_parser("adapters", help="inspect external adapter integration")
    adapters_subcommands = adapters_parser.add_subparsers(dest="adapters_command", required=True)

    adapters_subcommands.add_parser("doctor", help="check OpenSpec, Spec Kit, and Superpowers availability")
    adapters_subcommands.add_parser("install-hints", help="print upstream install commands and links")
    adapters_lifecycle_parser = adapters_subcommands.add_parser(
        "lifecycle",
        help="export local adapter lifecycle mappings",
    )
    adapters_lifecycle_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    adapters_lifecycle_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    adapters_handoff_parser = adapters_subcommands.add_parser(
        "handoff",
        help="export adapter execution handoff data for one native feature",
    )
    adapters_handoff_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    adapters_handoff_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    adapters_handoff_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    adapters_handoff_parser.add_argument(
        "--output",
        help="write the Markdown handoff packet to a file instead of printing it",
    )
    adapters_handoff_parser.add_argument(
        "--output-dir",
        help="write reviewable adapter handoff artifacts to a directory",
    )
    adapters_handoff_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing output file",
    )

    propose_parser = subcommands.add_parser(
        "propose",
        help="generate a structured spec bundle from natural language intent",
    )
    propose_parser.add_argument("intent", help="natural language description of the feature")
    propose_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    propose_parser.add_argument("--slug", help="feature slug (auto-generated from intent if omitted)")
    propose_parser.add_argument("--dry-run", action="store_true", help="print generated content without writing files")
    propose_parser.add_argument("--json", action="store_true", help="print stable JSON for agents and scripts")
    propose_parser.add_argument("--force", action="store_true", help="overwrite existing feature files")
    propose_parser.add_argument("--priority", default="medium", help="feature priority")
    propose_parser.add_argument("--owner", default="unassigned", help="feature owner")
    propose_parser.add_argument("--milestone", default="unassigned", help="feature milestone")
    propose_parser.add_argument("--target-release", default="unassigned", help="feature target release")
    propose_parser.add_argument("--project", default="unassigned", help="feature project")
    propose_parser.add_argument("--effort", default="unknown", help="estimated effort")

    mcp_parser = subcommands.add_parser("mcp", help="MCP server interface")
    mcp_sub = mcp_parser.add_subparsers(dest="mcp_command", required=True)
    mcp_sub.add_parser("server", help="Start MCP stdio server")
    mcp_config = mcp_sub.add_parser("config", help="Generate MCP client config")
    mcp_config.add_argument(
        "--format",
        choices=["claude-desktop", "vscode", "cursor"],
        default="claude-desktop",
    )
    mcp_config.add_argument("--root", default=".", help="workspace root path")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        root = Path(args.path).expanduser().resolve()
        written = init_workspace(root, force=args.force)
        if written:
            print(f"Initialized SpecSpine workspace at {root}")
            _print_created(written, root)
        else:
            print(f"SpecSpine workspace already exists at {root}")
        return 0

    if args.command == "agents":
        if args.agents_command == "init":
            root = Path(args.path).expanduser().resolve()
            try:
                written = init_agents_file(root, force=args.force)
            except AgentsFileExistsError as error:
                print(str(error), file=sys.stderr)
                return 1

            print(f"Initialized SpecSpine agent instructions at {root}")
            print(f"  created {written.relative_to(root)}")
            return 0

    if args.command == "fuse":
        root = Path(args.path).expanduser().resolve()
        include_openspec = not args.skip_openspec
        include_speckit = not args.skip_speckit
        include_superpowers = not args.skip_superpowers

        written = init_fusion_workspace(
            root,
            agent=args.agent,
            force=args.force,
            include_openspec=include_openspec,
            include_speckit=include_speckit,
            include_superpowers=include_superpowers,
        )

        if written:
            print(f"Initialized SpecSpine fusion layer at {root}")
            _print_created(written, root)
        else:
            print(f"SpecSpine fusion layer already exists at {root}")

        commands = build_upstream_init_commands(
            agent=args.agent,
            include_openspec=include_openspec,
            include_speckit=include_speckit,
            include_superpowers=include_superpowers,
            force=args.force,
        )

        if not args.run_upstream:
            print("Upstream tools were not run. Use --run-upstream to invoke:")
            for command in commands:
                print(f"  {command.key}: {command.display() or command.description}")
            return 0

        results = run_upstream_initializers(root, commands)
        failed = False
        print("Upstream initializer results:")
        for result in results:
            marker = "ok" if result.returncode == 0 else "failed"
            print(f"  [{marker}] {result.key}: {result.command}")
            if result.stdout.strip():
                print(f"      {result.stdout.strip()}")
            if result.stderr.strip():
                print(f"      {result.stderr.strip()}")
            failed = failed or result.returncode != 0
        return 1 if failed else 0

    if args.command == "feature":
        if args.feature_command == "new":
            root = Path(args.path).expanduser().resolve()
            try:
                written = create_feature_bundle(
                    root,
                    args.slug,
                    title=args.title,
                    why=args.why,
                    force=args.force,
                )
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleExistsError as error:
                print(str(error), file=sys.stderr)
                for path in error.existing_paths:
                    print(f"  existing {path.relative_to(root)}", file=sys.stderr)
                return 1

            print(f"Created SpecSpine feature bundle '{args.slug}' at {root}")
            _print_created(written, root)
            return 0

        if args.feature_command == "issue":
            root = Path(args.path).expanduser().resolve()
            try:
                draft = build_issue_draft(root, args.slug)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not read feature bundle: {error}", file=sys.stderr)
                return 1

            if args.output:
                output_path = Path(args.output).expanduser().resolve()
                if output_path.exists() and not args.force:
                    print(
                        f"Output file already exists: {output_path}. "
                        "Use --force to overwrite it.",
                        file=sys.stderr,
                    )
                    return 1

                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(draft.body, encoding="utf-8")
                except OSError as error:
                    print(f"Could not write issue draft: {error}", file=sys.stderr)
                    return 1

            if args.json:
                print(render_issue_json(draft), end="")
            elif args.output:
                print(f"Wrote GitHub issue draft body to {output_path}")
            else:
                print(render_issue_text(draft), end="")
            return 0

        if args.feature_command == "pr":
            root = Path(args.path).expanduser().resolve()
            try:
                draft = build_pull_request_draft(root, args.slug)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not read feature PR draft: {error}", file=sys.stderr)
                return 1

            if args.output:
                output_path = Path(args.output).expanduser().resolve()
                if output_path.exists() and not args.force:
                    print(
                        f"Output file already exists: {output_path}. "
                        "Use --force to overwrite it.",
                        file=sys.stderr,
                    )
                    return 1

                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(draft.body, encoding="utf-8")
                except OSError as error:
                    print(f"Could not write PR draft: {error}", file=sys.stderr)
                    return 1

            if args.json:
                print(render_pull_request_json(draft), end="")
            elif args.output:
                print(f"Wrote GitHub Pull Request draft body to {output_path}")
            else:
                print(render_pull_request_text(draft), end="")
            return 0

        if args.feature_command == "tasks":
            root = Path(args.path).expanduser().resolve()
            try:
                report = build_feature_tasks_report(root, args.slug)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not read feature tasks: {error}", file=sys.stderr)
                return 1

            text_body = render_feature_tasks_text(report)
            if args.output:
                output_path = Path(args.output).expanduser().resolve()
                if output_path.exists() and not args.force:
                    print(
                        f"Output file already exists: {output_path}. "
                        "Use --force to overwrite it.",
                        file=sys.stderr,
                    )
                    return 1

                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(text_body, encoding="utf-8")
                except OSError as error:
                    print(f"Could not write feature tasks: {error}", file=sys.stderr)
                    return 1

            if args.json:
                print(render_feature_tasks_json(report), end="")
            elif args.output:
                print(f"Wrote feature task list to {output_path}")
            else:
                print(text_body, end="")
            return 0

        if args.feature_command == "task-issues":
            root = Path(args.path).expanduser().resolve()
            try:
                report = build_feature_task_issues_report(root, args.slug)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not read feature task issue drafts: {error}", file=sys.stderr)
                return 1

            text_body = render_feature_task_issues_text(report)
            if args.output:
                output_path = Path(args.output).expanduser().resolve()
                if output_path.exists() and not args.force:
                    print(
                        f"Output file already exists: {output_path}. "
                        "Use --force to overwrite it.",
                        file=sys.stderr,
                    )
                    return 1

                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(text_body, encoding="utf-8")
                except OSError as error:
                    print(f"Could not write feature task issue drafts: {error}", file=sys.stderr)
                    return 1

            if args.json:
                print(render_feature_task_issues_json(report), end="")
            elif args.output:
                print(f"Wrote feature task issue draft package to {output_path}")
            else:
                print(text_body, end="")
            return 0

        if args.feature_command == "sync-plan":
            root = Path(args.path).expanduser().resolve()
            try:
                plan = build_feature_sync_plan(root, args.slug)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not read feature sync plan: {error}", file=sys.stderr)
                return 1

            text_body = render_feature_sync_plan_text(plan)
            output_path = None
            if args.output:
                output_path = Path(args.output).expanduser().resolve()
                if output_path.exists() and not args.force:
                    print(
                        f"Output file already exists: {output_path}. "
                        "Use --force to overwrite it.",
                        file=sys.stderr,
                    )
                    return 1

            artifact_output = None
            if args.output_dir:
                output_dir = Path(args.output_dir).expanduser().resolve()
                try:
                    artifact_output = write_feature_sync_plan_artifacts(
                        plan,
                        output_dir,
                        force=args.force,
                    )
                except FeatureSyncPlanArtifactExistsError as error:
                    print(str(error), file=sys.stderr)
                    for path in error.existing_paths:
                        print(f"  existing {path}", file=sys.stderr)
                    return 1
                except OSError as error:
                    print(f"Could not write feature sync plan artifacts: {error}", file=sys.stderr)
                    return 1

            if output_path is not None:
                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(text_body, encoding="utf-8")
                except OSError as error:
                    print(f"Could not write feature sync plan: {error}", file=sys.stderr)
                    return 1

            if args.json:
                print(render_feature_sync_plan_json(plan), end="")
            elif args.output:
                print(f"Wrote feature sync plan to {output_path}")
            elif artifact_output is not None:
                print(f"Wrote feature sync plan artifacts to {artifact_output.output_dir}")
            else:
                print(text_body, end="")
            return 0

        if args.feature_command == "archive":
            root = Path(args.path).expanduser().resolve()
            try:
                report = build_feature_archive_report(
                    root,
                    args.slug,
                    archive_id=args.archive_id,
                )
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except InvalidArchiveId as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not read feature archive evidence: {error}", file=sys.stderr)
                return 1

            if args.output_dir:
                output_dir = Path(args.output_dir).expanduser().resolve()
                try:
                    package = write_feature_archive_package(
                        report,
                        output_dir,
                        force=args.force,
                    )
                    report = feature_archive_report_with_package(report, package)
                except FeatureArchiveArtifactExistsError as error:
                    print(str(error), file=sys.stderr)
                    for path in error.existing_paths:
                        print(f"  existing {path}", file=sys.stderr)
                    return 1
                except OSError as error:
                    print(f"Could not write feature archive package: {error}", file=sys.stderr)
                    return 1

            if args.json:
                print(render_feature_archive_json(report), end="")
            else:
                print(render_feature_archive_text(report), end="")
            return 0

        if args.feature_command == "trace":
            root = Path(args.path).expanduser().resolve()
            try:
                report = build_feature_trace_report(root, args.slug)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not read feature trace: {error}", file=sys.stderr)
                return 1

            text_body = render_feature_trace_text(report)
            if args.output:
                output_path = Path(args.output).expanduser().resolve()
                if output_path.exists() and not args.force:
                    print(
                        f"Output file already exists: {output_path}. "
                        "Use --force to overwrite it.",
                        file=sys.stderr,
                    )
                    return 1

                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(text_body, encoding="utf-8")
                except OSError as error:
                    print(f"Could not write feature trace: {error}", file=sys.stderr)
                    return 1

            if args.json:
                print(render_feature_trace_json(report), end="")
            elif args.output:
                print(f"Wrote feature trace handoff to {output_path}")
            else:
                print(text_body, end="")
            return 0

        if args.feature_command == "handoff":
            root = Path(args.path).expanduser().resolve()
            try:
                report = build_feature_handoff_report(root, args.slug)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except OSError as error:
                print(f"Could not read feature handoff: {error}", file=sys.stderr)
                return 1

            text_body = render_feature_handoff_text(report)
            if args.output:
                output_path = Path(args.output).expanduser().resolve()
                if output_path.exists() and not args.force:
                    print(
                        f"Output file already exists: {output_path}. "
                        "Use --force to overwrite it.",
                        file=sys.stderr,
                    )
                    return 1

                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(text_body, encoding="utf-8")
                except OSError as error:
                    print(f"Could not write feature handoff: {error}", file=sys.stderr)
                    return 1

            if args.json:
                print(render_feature_handoff_json(report), end="")
            elif args.output:
                print(f"Wrote feature handoff packet to {output_path}")
            else:
                print(text_body, end="")
            return 0 if report.has_native_files else 1

        if args.feature_command == "tests":
            root = Path(args.path).expanduser().resolve()
            try:
                report = build_feature_tests_report(root, args.slug)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except OSError as error:
                print(f"Could not read feature test packet: {error}", file=sys.stderr)
                return 1

            text_body = render_feature_tests_text(report)
            if args.output:
                output_path = Path(args.output).expanduser().resolve()
                if output_path.exists() and not args.force:
                    print(
                        f"Output file already exists: {output_path}. "
                        "Use --force to overwrite it.",
                        file=sys.stderr,
                    )
                    return 1

                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(text_body, encoding="utf-8")
                except OSError as error:
                    print(f"Could not write feature test packet: {error}", file=sys.stderr)
                    return 1

            if args.json:
                print(render_feature_tests_json(report), end="")
            elif args.output:
                print(f"Wrote feature test packet to {output_path}")
            else:
                print(text_body, end="")
            return 0 if report.has_native_files else 1

        if args.feature_command == "ready":
            root = Path(args.path).expanduser().resolve()
            try:
                policy_required = False
                policy_source = None
                if args.policy:
                    policy = load_workspace_policy(root)
                    metadata = read_feature_metadata(root, args.slug)
                    status = get_feature_status(root, args.slug).status or "unknown"
                    policy_required = policy.require_coverage.requires_coverage(
                        feature_id=args.slug,
                        metadata=metadata,
                        status=status,
                    )
                    policy_source = str(policy.source_file)
                report = build_feature_ready_report(
                    root,
                    args.slug,
                    require_coverage=args.require_coverage or policy_required,
                    policy_applied=args.policy,
                    coverage_required_by_policy=policy_required,
                    policy_source=policy_source,
                )
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except OSError as error:
                print(f"Could not read feature readiness: {error}", file=sys.stderr)
                return 1

            if args.json:
                print(render_feature_ready_json(report), end="")
            else:
                print(render_feature_ready_text(report), end="")
            return 0 if report.ready else 1

        if args.feature_command == "status":
            root = Path(args.path).expanduser().resolve()
            try:
                if args.set_status:
                    report = set_feature_status(
                        root,
                        args.slug,
                        args.set_status,
                        enforce_transition=args.enforce_transition,
                    )
                    include_updated = True
                else:
                    report = get_feature_status(root, args.slug)
                    include_updated = False
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except InvalidFeatureStatus as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureStatusTransitionError as error:
                if args.json:
                    print(render_status_json(error.as_dict()), end="")
                else:
                    print(str(error), file=sys.stderr)
                    for check in error.blocking_checks:
                        print(
                            f"  blocking {check['id']}: {check['message']}",
                            file=sys.stderr,
                        )
                    for gap in error.gaps:
                        print(
                            f"  gap {gap['id']}: {gap['message']}",
                            file=sys.stderr,
                        )
                    for path in error.missing_files:
                        print(f"  missing {path}", file=sys.stderr)
                return 1
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not update feature status: {error}", file=sys.stderr)
                return 1

            payload = report.as_dict(include_updated=include_updated)
            has_files = any(bool(file["exists"]) for file in report.files.values())
            if args.json:
                print(render_status_json(payload), end="")
            else:
                if include_updated:
                    transition = report.transition or {}
                    from_status = transition.get("from") or "unknown"
                    marker = " with enforced transition" if transition.get("enforced") else ""
                    print(
                        f"Feature {report.feature_id} status updated: "
                        f"{from_status} -> {report.status}{marker}"
                    )
                elif report.consistent:
                    print(f"Feature {report.feature_id} status: {report.status}")
                else:
                    print(
                        f"Feature {report.feature_id} status: "
                        f"{report.status or 'unknown'} (mixed/inconsistent)"
                    )
                for kind, file in report.files.items():
                    marker = "ok" if file["exists"] else "missing"
                    status = file["status"] or "unknown"
                    print(f"  [{marker}] {kind}: {file['path']} ({status})")
            return 0 if has_files else 1

    if args.command == "doctor":
        required_files = dict(BASE_WORKSPACE_FILES)
        if args.fusion:
            required_files.update(FUSION_REQUIRED_FILES)

        _present, missing = check_workspace(Path(args.path), required_files=required_files)
        if missing:
            print("SpecSpine workspace is incomplete.")
            root = Path(args.path).expanduser().resolve()
            for path in missing:
                print(f"  missing {path.relative_to(root)}")
            if args.adapters:
                _print_adapter_statuses()
            return 1

        print(f"SpecSpine workspace is ready at {Path(args.path).expanduser().resolve()}")
        if args.adapters:
            statuses = probe_adapters()
            _print_adapter_statuses(statuses)
            return 0 if all(status.available for status in statuses) else 1
        return 0

    if args.command == "gates":
        report = build_quality_gate_report(Path(args.path))
        if args.json:
            print(render_quality_gate_json(report), end="")
        else:
            print(render_quality_gate_text(report), end="")
        return 1 if report.source_missing else 0

    if args.command == "policy":
        try:
            policy = load_workspace_policy(Path(args.path))
        except OSError as error:
            print(f"Could not read workspace policy: {error}", file=sys.stderr)
            return 1
        if args.json:
            print(render_policy_json(policy), end="")
        else:
            print(render_policy_text(policy), end="")
        return 0

    if args.command == "coverage":
        if args.coverage_command == "debt":
            try:
                report = build_coverage_debt_report(
                    Path(args.path),
                    use_policy=args.policy,
                )
            except OSError as error:
                print(f"Could not read coverage debt: {error}", file=sys.stderr)
                return 1

            if args.json:
                print(render_coverage_debt_json(report), end="")
            else:
                print(render_coverage_debt_text(report), end="")
            return 0

    if args.command == "analyze":
        try:
            report = build_analysis_report(
                Path(args.path),
                feature_filter=args.feature,
            )
        except InvalidFeatureSlug as error:
            print(str(error), file=sys.stderr)
            return 2
        except OSError as error:
            print(f"Could not analyze feature bundles: {error}", file=sys.stderr)
            return 1

        if args.json:
            print(render_analysis_json(report), end="")
        else:
            print(render_analysis_text(report), end="")
        if args.fail_on_issues and report.issues:
            return 1
        return 0

    if args.command == "loop":
        if args.loop_command == "packet":
            try:
                packet = build_loop_packet(
                    Path(args.path),
                    deadline=args.deadline,
                )
            except OSError as error:
                print(f"Could not build loop packet: {error}", file=sys.stderr)
                return 1

            text_body = render_loop_packet_text(packet)
            output_path = None
            if args.output:
                output_path = Path(args.output).expanduser().resolve()
                if output_path.exists() and not args.force:
                    print(
                        f"Output file already exists: {output_path}. "
                        "Use --force to overwrite it.",
                        file=sys.stderr,
                    )
                    return 1

                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(text_body, encoding="utf-8")
                except OSError as error:
                    print(f"Could not write loop packet: {error}", file=sys.stderr)
                    return 1

            if args.json:
                print(render_loop_packet_json(packet), end="")
            elif output_path is not None:
                print(f"Wrote loop packet to {output_path}")
            else:
                print(text_body, end="")
            return 0

    if args.command == "status":
        if args.validation_warnings and not args.validate:
            print("--validation-warnings requires --validate.", file=sys.stderr)
            return 2
        if args.readiness_policy and not args.readiness_summary:
            print("--readiness-policy requires --readiness-summary.", file=sys.stderr)
            return 2
        if args.readiness_require_coverage and not args.readiness_summary:
            print("--readiness-require-coverage requires --readiness-summary.", file=sys.stderr)
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
                file=sys.stderr,
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
                print(str(error), file=sys.stderr)
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
        status = build_status(Path(args.path), **status_kwargs)
        if args.validate:
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

    if args.command == "validate":
        report = build_validation_report(
            Path(args.path),
            include_fusion=args.fusion,
            include_features=args.features,
            include_adapters=args.adapters,
        )
        if args.json:
            print(render_validation_json(report), end="")
        else:
            print(render_validation_text(report), end="")
        return validation_exit_code(report)

    if args.command == "adapters":
        if args.adapters_command == "doctor":
            statuses = probe_adapters()
            _print_adapter_statuses(statuses)
            return 0 if all(status.available for status in statuses) else 1

        if args.adapters_command == "install-hints":
            for spec in ADAPTER_SPECS.values():
                print(f"{spec.display_name}:")
                print(f"  upstream: {spec.upstream_url}")
                print(f"  install: {spec.install_hint}")
            return 0

        if args.adapters_command == "lifecycle":
            report = build_adapter_lifecycle_report(Path(args.path))
            if args.json:
                print(render_adapter_lifecycle_json(report), end="")
            else:
                print(render_adapter_lifecycle_text(report), end="")
            return 0

        if args.adapters_command == "handoff":
            root = Path(args.path).expanduser().resolve()
            try:
                report = build_adapter_feature_handoff_report(root, args.slug)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not read adapter feature handoff: {error}", file=sys.stderr)
                return 1

            text_body = render_adapter_feature_handoff_text(report)
            output_path = None
            if args.output:
                output_path = Path(args.output).expanduser().resolve()
                if output_path.exists() and not args.force:
                    print(
                        f"Output file already exists: {output_path}. "
                        "Use --force to overwrite it.",
                        file=sys.stderr,
                    )
                    return 1

            artifact_output = None
            if args.output_dir:
                output_dir = Path(args.output_dir).expanduser().resolve()
                try:
                    artifact_output = write_adapter_feature_handoff_artifacts(
                        report,
                        output_dir,
                        force=args.force,
                    )
                except AdapterHandoffArtifactExistsError as error:
                    print(str(error), file=sys.stderr)
                    for path in error.existing_paths:
                        print(f"  existing {path}", file=sys.stderr)
                    return 1
                except OSError as error:
                    print(f"Could not write adapter handoff artifacts: {error}", file=sys.stderr)
                    return 1

            if output_path is not None:
                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(text_body, encoding="utf-8")
                except OSError as error:
                    print(f"Could not write adapter feature handoff: {error}", file=sys.stderr)
                    return 1

            if args.json:
                if artifact_output is None:
                    print(render_adapter_feature_handoff_json(report), end="")
                else:
                    payload = report.as_dict()
                    payload["artifacts"] = artifact_output.manifest["artifacts"]
                    payload["artifact_dir"] = str(artifact_output.output_dir)
                    payload["checksum_algorithm"] = artifact_output.manifest[
                        "checksum_algorithm"
                    ]
                    payload["artifact_checksums"] = artifact_output.manifest[
                        "artifact_checksums"
                    ]
                    print(json.dumps(payload, indent=2, sort_keys=True) + "\n", end="")
            elif output_path is not None:
                print(f"Wrote adapter feature handoff packet to {output_path}")
            elif artifact_output is not None:
                print(f"Wrote adapter handoff artifacts to {artifact_output.output_dir}")
            else:
                print(text_body, end="")
            return 0

    if args.command == "propose":
        root = Path(args.path).expanduser().resolve()
        intent = args.intent

        try:
            from .proposer import normalize_intent

            intent, warnings = normalize_intent(intent)
            if args.slug:
                slug = args.slug
            else:
                slug = _generate_slug_from_intent(intent)

            from .features import validate_feature_slug as _validate_slug
            slug = _validate_slug(slug)
        except ValueError as error:
            print(str(error), file=sys.stderr)
            return 2
        except InvalidFeatureSlug as error:
            print(str(error), file=sys.stderr)
            return 2

        if args.dry_run:
            try:
                files = build_proposal_files(
                    slug,
                    intent,
                    priority=args.priority,
                    owner=args.owner,
                    milestone=args.milestone,
                    target_release=args.target_release,
                    project=args.project,
                    effort=args.effort,
                )
            except (InvalidFeatureSlug, ValueError) as error:
                print(str(error), file=sys.stderr)
                return 2

            targets = {
                relative_path: root / relative_path
                for relative_path in files
            }
            existing_paths = [
                str(path.relative_to(root))
                for path in targets.values()
                if path.exists()
            ]
            if existing_paths and not args.force:
                print(
                    f"Feature bundle '{slug}' already has existing files. "
                    "Use --force to overwrite them.",
                    file=sys.stderr,
                )
                for path in existing_paths:
                    print(f"  existing {path}", file=sys.stderr)
                return 1

            metadata = {
                "effort": args.effort,
                "milestone": args.milestone,
                "owner": args.owner,
                "priority": args.priority,
                "project": args.project,
                "target_release": args.target_release,
            }
            if args.json:
                payload = {
                    "dry_run": bool(args.dry_run),
                    "existing_paths": existing_paths,
                    "intent": intent,
                    "metadata": metadata,
                    "files": dict(files),
                    "slug": slug,
                    "warnings": warnings,
                    "written_paths": [],
                }
                print(json.dumps(payload, indent=2, sort_keys=True) + "\n", end="")
            else:
                for warning in warnings:
                    print(f"Warning: {warning}")
                print(f"# Proposed feature: {slug}")
                print(f"# Intent: {intent}")
                if existing_paths:
                    print("# Existing files: " + ", ".join(existing_paths))
                print()
                for relative_path, content in files.items():
                    print(f"## {relative_path}")
                    print()
                    print(content)
                    print()
            return 0

        pre_existing_paths: list[str] = []
        try:
            planned_files = build_proposal_files(
                slug,
                intent,
                priority=args.priority,
                owner=args.owner,
                milestone=args.milestone,
                target_release=args.target_release,
                project=args.project,
                effort=args.effort,
            )
            pre_existing_paths = [
                relative_path
                for relative_path in planned_files
                if (root / relative_path).exists()
            ]
            written = create_proposal_bundle(
                root,
                slug,
                intent,
                priority=args.priority,
                owner=args.owner,
                milestone=args.milestone,
                target_release=args.target_release,
                project=args.project,
                effort=args.effort,
                force=args.force,
            )
        except InvalidFeatureSlug as error:
            print(str(error), file=sys.stderr)
            return 2
        except ValueError as error:
            print(str(error), file=sys.stderr)
            return 2
        except FeatureBundleExistsError as error:
            print(str(error), file=sys.stderr)
            for path in error.existing_paths:
                print(f"  existing {path.relative_to(root)}", file=sys.stderr)
            return 1

        if args.json:
            files = build_proposal_files(
                slug,
                intent,
                priority=args.priority,
                owner=args.owner,
                milestone=args.milestone,
                target_release=args.target_release,
                project=args.project,
                effort=args.effort,
            )
            payload = {
                "dry_run": False,
                "existing_paths": pre_existing_paths,
                "intent": intent,
                "metadata": {
                    "effort": args.effort,
                    "milestone": args.milestone,
                    "owner": args.owner,
                    "priority": args.priority,
                    "project": args.project,
                    "target_release": args.target_release,
                },
                "files": dict(files),
                "slug": slug,
                "warnings": warnings,
                "written_paths": [str(path.relative_to(root)) for path in written],
            }
            print(json.dumps(payload, indent=2, sort_keys=True) + "\n", end="")
            return 0

        for warning in warnings:
            print(f"Warning: {warning}")
        print(f"Created SpecSpine proposal bundle '{slug}' at {root}")
        _print_created(written, root)
        return 0

    if args.command == "mcp":
        if args.mcp_command == "server":
            from .mcp import run_server

            run_server()
            return 0

        if args.mcp_command == "config":
            from .mcp import generate_client_config

            config = generate_client_config(fmt=args.format, root=args.root)
            print(json.dumps(config, indent=2, sort_keys=True))
            return 0

    parser.print_help()
    return 1
