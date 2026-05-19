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
from .blueprint import (
    build_spec_code_blueprint,
    render_blueprint_json,
    render_blueprint_text,
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
from .change import (
    build_change_risk_report,
    render_change_risk_json,
    render_change_risk_text,
)
from .cicd import (
    SAFETY_NOTES,
    SUPPORTED_FORMATS,
    generate_pipeline,
    render_pipeline_json,
    render_pipeline_text,
    render_pipeline_yaml,
)
from .consistency import (
    build_consistency_report,
    render_consistency_json,
    render_consistency_text,
)
from .coverage import (
    build_coverage_debt_report,
    build_coverage_plan_report,
    render_coverage_debt_json,
    render_coverage_debt_text,
    render_coverage_plan_json,
    render_coverage_plan_text,
)
from .dependency import (
    build_dependency_graph,
    render_dependency_json,
    render_dependency_text,
)
from .executor import (
    build_execution_plan,
    build_grading_rubric,
    render_grade_json,
    render_grade_text,
    render_loop_json,
    render_loop_text,
    render_plan_json,
    render_plan_text,
    run_execution_loop,
)
from .evolution import (
    GitDiffError,
    InvalidGitBaseError,
    build_evolution_timeline,
    calculate_risk_level,
    classify_changes,
    generate_remediation_plan,
    get_git_diff,
    render_diff_json,
    render_diff_text,
    render_evolution_json,
    render_evolution_text,
    resolve_impact,
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
    build_feature_tasks_report,
    build_feature_tests_report,
    build_feature_trace_report,
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
    render_feature_tasks_json,
    render_feature_tasks_text,
    render_feature_tests_json,
    render_feature_tests_text,
    render_feature_trace_json,
    render_feature_trace_text,
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
from .harness import (
    build_harness_feedback,
    build_harness_quality,
    render_harness_feedback_json,
    render_harness_feedback_text,
    render_harness_quality_json,
    render_harness_quality_text,
)
from .hygiene import (
    build_hygiene_scan_report,
    hygiene_report_has_strict_findings,
    render_hygiene_scan_json,
    render_hygiene_scan_text,
)
from .impact import (
    build_test_impact_report,
    render_test_impact_json,
    render_test_impact_text,
)
from .loop import (
    build_loop_packet,
    render_loop_packet_json,
    render_loop_packet_text,
)
from .orchestration import (
    build_orchestration_plan,
    render_orchestration_json,
    render_orchestration_text,
)
from .policy import load_workspace_policy, render_policy_json, render_policy_text
from .provenance import (
    build_provenance_manifest,
    render_provenance_manifest_json,
    render_provenance_manifest_text,
)
from .retrospective import (
    build_retrospective_analytics_report,
    build_retrospective_report,
    render_retrospective_analytics_json,
    render_retrospective_json,
    render_retrospective_text,
    retrospective_report_exit_code,
)
from .release import (
    build_release_notes_report,
    render_release_notes_json,
    render_release_notes_json_lines,
    render_release_notes_text,
)
from .review import (
    build_review_packet,
    render_review_packet_json,
    render_review_packet_text,
)
from .scaffold import (
    build_ac_test_scaffold,
    render_scaffold_json,
    render_scaffold_text,
)
from .security import (
    build_security_cue_report,
    render_security_cue_json,
    render_security_cue_text,
)
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
from .verification import (
    build_verification_matrix,
    render_verification_matrix_json,
    render_verification_matrix_text,
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

    feature_dependency_parser = feature_subcommands.add_parser(
        "dependency",
        help="analyze feature dependencies and compute critical path",
    )
    feature_dependency_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    feature_dependency_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    feature_dependency_parser.add_argument(
        "--feature",
        metavar="SLUG",
        help="focus on one native feature slug",
    )
    feature_dependency_parser.add_argument(
        "--features",
        metavar="SLUG1,SLUG2",
        help="comma-separated list of feature slugs to include",
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
    coverage_plan_parser = coverage_subcommands.add_parser(
        "plan",
        help="plan local remediation for acceptance-criteria coverage gaps",
    )
    coverage_plan_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    coverage_plan_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    coverage_plan_parser.add_argument(
        "--policy",
        action="store_true",
        help="only plan coverage for features selected by workspace readiness policy",
    )
    coverage_plan_parser.add_argument(
        "--feature",
        help="focus the plan on one native feature slug",
    )
    coverage_plan_parser.add_argument(
        "--limit",
        type=int,
        help="limit returned plan items without changing summary counts",
    )

    tests_parser = subcommands.add_parser("tests", help="inspect local test impact")
    tests_subcommands = tests_parser.add_subparsers(dest="tests_command", required=True)
    tests_impact_parser = tests_subcommands.add_parser(
        "impact",
        help="export a local static source-to-test impact packet",
    )
    tests_impact_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    tests_impact_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    tests_impact_parser.add_argument(
        "--changed",
        action="append",
        default=[],
        metavar="PATH",
        help="changed source or test path; repeat to include more than one",
    )
    tests_impact_parser.add_argument(
        "--feature",
        metavar="SLUG",
        help="include local feature test coverage evidence",
    )

    verify_parser = subcommands.add_parser(
        "verify",
        help="export local verification evidence",
    )
    verify_subcommands = verify_parser.add_subparsers(
        dest="verify_command",
        required=True,
    )
    verify_matrix_parser = verify_subcommands.add_parser(
        "matrix",
        help="export a feature verification matrix",
    )
    verify_matrix_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    verify_matrix_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    verify_matrix_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )

    change_parser = subcommands.add_parser("change", help="inspect local change risk")
    change_subcommands = change_parser.add_subparsers(
        dest="change_command",
        required=True,
    )
    change_risk_parser = change_subcommands.add_parser(
        "risk",
        help="export a local changed-path risk packet",
    )
    change_risk_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    change_risk_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    change_risk_parser.add_argument(
        "--changed",
        action="append",
        default=[],
        metavar="PATH",
        help="changed path; repeat to include more than one",
    )
    change_risk_parser.add_argument(
        "--feature",
        metavar="SLUG",
        help="include focused native feature readiness evidence",
    )

    consistency_parser = subcommands.add_parser(
        "consistency",
        help="inspect local spec-code consistency",
    )
    consistency_subcommands = consistency_parser.add_subparsers(
        dest="consistency_command",
        required=True,
    )
    consistency_scan_parser = consistency_subcommands.add_parser(
        "scan",
        help="export a local spec-code consistency report",
    )
    consistency_scan_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    consistency_scan_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    consistency_scan_parser.add_argument(
        "--feature",
        metavar="SLUG",
        help="scan one native feature slug",
    )
    consistency_scan_parser.add_argument(
        "--changed",
        action="append",
        default=[],
        metavar="PATH",
        help="changed path; repeat to include more than one",
    )

    hygiene_parser = subcommands.add_parser(
        "hygiene",
        help="inspect local repository hygiene",
    )
    hygiene_subcommands = hygiene_parser.add_subparsers(
        dest="hygiene_command",
        required=True,
    )
    hygiene_scan_parser = hygiene_subcommands.add_parser(
        "scan",
        help="export a local repository hygiene scan",
    )
    hygiene_scan_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    hygiene_scan_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    hygiene_scan_parser.add_argument(
        "--changed",
        action="append",
        default=[],
        metavar="PATH",
        help="changed path; repeat to include more than one",
    )
    hygiene_scan_parser.add_argument(
        "--strict",
        action="store_true",
        help="return nonzero when high-severity findings are present",
    )

    security_parser = subcommands.add_parser(
        "security",
        help="inspect local security review cues",
    )
    security_subcommands = security_parser.add_subparsers(
        dest="security_command",
        required=True,
    )
    security_cues_parser = security_subcommands.add_parser(
        "cues",
        help="export local security-sensitive review cues",
    )
    security_cues_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    security_cues_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    security_cues_parser.add_argument(
        "--changed",
        action="append",
        default=[],
        metavar="PATH",
        help="changed path; repeat to include more than one",
    )
    security_cues_parser.add_argument(
        "--feature",
        metavar="SLUG",
        help="include focused native feature readiness evidence",
    )

    provenance_parser = subcommands.add_parser(
        "provenance",
        help="export local provenance and audit evidence",
    )
    provenance_subcommands = provenance_parser.add_subparsers(
        dest="provenance_command",
        required=True,
    )
    provenance_manifest_parser = provenance_subcommands.add_parser(
        "manifest",
        help="export a local provenance manifest",
    )
    provenance_manifest_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    provenance_manifest_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    provenance_manifest_parser.add_argument(
        "--feature",
        metavar="SLUG",
        help="include focused native feature evidence",
    )
    provenance_manifest_parser.add_argument(
        "--include",
        action="append",
        default=[],
        metavar="PATH",
        help="include a local file in the manifest; repeat to include more than one",
    )

    review_parser = subcommands.add_parser("review", help="compose local review packets")
    review_subcommands = review_parser.add_subparsers(dest="review_command", required=True)
    review_packet_parser = review_subcommands.add_parser(
        "packet",
        help="export a local pre-merge review evidence packet",
    )
    review_packet_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    review_packet_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    review_packet_parser.add_argument(
        "--feature",
        metavar="SLUG",
        help="include focused native feature evidence",
    )
    review_packet_parser.add_argument(
        "--changed",
        action="append",
        default=[],
        metavar="PATH",
        help="changed source or test path; repeat to include more than one",
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

    orchestrate_parser = subcommands.add_parser(
        "orchestrate",
        help="coordinate multi-agent feature implementation",
    )
    orchestrate_subcommands = orchestrate_parser.add_subparsers(
        dest="orchestrate_command",
        required=True,
    )
    orchestrate_plan_parser = orchestrate_subcommands.add_parser(
        "plan",
        help="build an orchestration plan for parallel feature implementation",
    )
    orchestrate_plan_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    orchestrate_plan_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    orchestrate_plan_parser.add_argument(
        "--feature",
        metavar="SLUG",
        help="focus the orchestration plan on one native feature slug",
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

    execute_parser = subcommands.add_parser(
        "execute",
        help="turn specs into execution plans and self-correcting loops",
    )
    execute_subcommands = execute_parser.add_subparsers(dest="execute_command", required=True)

    execute_plan_parser = execute_subcommands.add_parser(
        "plan",
        help="build a topologically-sorted execution plan from a feature spec",
    )
    execute_plan_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    execute_plan_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    execute_plan_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )

    execute_grade_parser = execute_subcommands.add_parser(
        "grade",
        help="build a grading rubric mapping ACs to validation checks",
    )
    execute_grade_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    execute_grade_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    execute_grade_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )

    execute_loop_parser = execute_subcommands.add_parser(
        "loop",
        help="run a self-correcting plan-grade-gap loop",
    )
    execute_loop_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    execute_loop_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    execute_loop_parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="maximum loop iterations (default: 3)",
    )
    execute_loop_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )

    harness_parser = subcommands.add_parser(
        "harness",
        help="agent self-correction harness with verification and repair",
    )
    harness_subcommands = harness_parser.add_subparsers(dest="harness_command", required=True)

    harness_feedback_parser = harness_subcommands.add_parser(
        "feedback",
        help="run harness sensors and generate repair strategies for a feature",
    )
    harness_feedback_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    harness_feedback_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    harness_feedback_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )

    harness_repair_parser = harness_subcommands.add_parser(
        "repair",
        help="show repair strategies for a feature's failed acceptance criteria",
    )
    harness_repair_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    harness_repair_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    harness_repair_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )

    harness_quality_parser = harness_subcommands.add_parser(
        "quality",
        help="compute workspace-level harness quality metrics",
    )
    harness_quality_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    harness_quality_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )

    blueprint_parser = subcommands.add_parser(
        "blueprint",
        help="generate spec-to-code implementation blueprints",
    )
    blueprint_subcommands = blueprint_parser.add_subparsers(
        dest="blueprint_command",
        required=True,
    )
    blueprint_generate_parser = blueprint_subcommands.add_parser(
        "generate",
        help="generate an implementation blueprint from acceptance criteria",
    )
    blueprint_generate_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    blueprint_generate_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    blueprint_generate_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    blueprint_generate_parser.add_argument(
        "--output-dir",
        help="write blueprint artifacts to a directory",
    )
    blueprint_generate_parser.add_argument(
        "--fail-on-gaps",
        action="store_true",
        help="return nonzero when blueprint coverage gaps are found",
    )
    blueprint_generate_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing output files",
    )

    cicd_parser = subcommands.add_parser(
        "cicd",
        help="generate CI/CD pipelines from spec metadata",
    )
    cicd_subcommands = cicd_parser.add_subparsers(
        dest="cicd_command",
        required=True,
    )
    cicd_generate_parser = cicd_subcommands.add_parser(
        "generate",
        help="generate CI/CD pipeline config from spec metadata and quality gates",
    )
    cicd_generate_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    cicd_generate_parser.add_argument(
        "--format",
        choices=SUPPORTED_FORMATS,
        default="github-actions",
        help="pipeline format (default: github-actions)",
    )
    cicd_generate_parser.add_argument(
        "--feature",
        metavar="SLUG",
        help="include feature-specific readiness gate",
    )
    cicd_generate_parser.add_argument(
        "--output-dir",
        help="write generated pipeline artifacts to a directory",
    )
    cicd_generate_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    cicd_generate_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing output files",
    )

    cicd_validate_parser = cicd_subcommands.add_parser(
        "validate",
        help="validate generated pipeline configuration",
    )
    cicd_validate_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    cicd_validate_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
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

    scaffold_parser = subcommands.add_parser(
        "scaffold",
        help="generate test scaffolds from acceptance criteria",
    )
    scaffold_subcommands = scaffold_parser.add_subparsers(
        dest="scaffold_command",
        required=True,
    )
    scaffold_tests_parser = scaffold_subcommands.add_parser(
        "tests",
        help="generate Python test scaffolds from feature acceptance criteria",
    )
    scaffold_tests_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    scaffold_tests_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    scaffold_tests_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    scaffold_tests_parser.add_argument(
        "--output-dir",
        help="write scaffold file to a directory",
    )
    scaffold_tests_parser.add_argument(
        "--update-quality",
        action="store_true",
        help="append new coverage links to the quality file Test Coverage section",
    )
    scaffold_tests_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing scaffold output file",
    )

    retrospective_parser = subcommands.add_parser(
        "retrospective",
        help="build local feature retrospective reports",
    )
    retrospective_subcommands = retrospective_parser.add_subparsers(
        dest="retrospective_command",
        required=True,
    )
    retrospective_report_parser = retrospective_subcommands.add_parser(
        "report",
        help="scan native feature bundles and recommend follow-up work",
    )
    retrospective_report_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    retrospective_report_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    retrospective_report_parser.add_argument(
        "--feature",
        metavar="SLUG",
        help="focus on one native feature slug",
    )
    retrospective_report_parser.add_argument(
        "--limit",
        type=int,
        help="limit recommendation rows without changing summary or theme counts",
    )
    retrospective_analytics_parser = retrospective_subcommands.add_parser(
        "analytics",
        help="compute retrospective analytics with anti-pattern detection",
    )
    retrospective_analytics_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    retrospective_analytics_parser.add_argument("--json", action="store_true", help="print stable JSON")
    retrospective_analytics_parser.add_argument("--improvements", action="store_true", help="include improvement recommendations")
    retrospective_analytics_parser.add_argument("--feature", metavar="SLUG", help="focus on one feature")

    spec_parser = subcommands.add_parser("spec", help="inspect spec changes and evolution")
    spec_subcommands = spec_parser.add_subparsers(dest="spec_command", required=True)

    spec_diff_parser = spec_subcommands.add_parser(
        "diff",
        help="compute semantic diff for a feature spec bundle",
    )
    spec_diff_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    spec_diff_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    spec_diff_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    spec_diff_parser.add_argument(
        "--base",
        metavar="COMMIT",
        help="git commit to diff against",
    )
    spec_diff_parser.add_argument(
        "--unstaged",
        action="store_true",
        help="show unstaged changes",
    )
    spec_diff_parser.add_argument(
        "--output",
        help="write output to a file",
    )
    spec_diff_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing output file",
    )

    spec_evolution_parser = spec_subcommands.add_parser(
        "evolution",
        help="show evolution timeline for a feature spec bundle",
    )
    spec_evolution_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    spec_evolution_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    spec_evolution_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    spec_evolution_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="limit timeline entries (default: 20)",
    )

    release_parser = subcommands.add_parser(
        "release",
        help="generate release notes from validated and archived features",
    )
    release_subcommands = release_parser.add_subparsers(
        dest="release_command",
        required=True,
    )
    release_notes_parser = release_subcommands.add_parser(
        "notes",
        help="generate structured release notes",
    )
    release_notes_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    release_notes_parser.add_argument(
        "--since",
        metavar="TAG",
        help="start tag or date for the release range",
    )
    release_notes_parser.add_argument(
        "--until",
        metavar="TAG",
        help="end tag or date for the release range",
    )
    release_notes_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    release_notes_parser.add_argument(
        "--format",
        choices=["markdown", "json", "json-lines"],
        default="markdown",
        help="output format (default: markdown)",
    )
    release_notes_parser.add_argument(
        "--group-by",
        choices=["priority", "project", "status", "effort"],
        default="priority",
        help="group features by field (default: priority)",
    )
    release_notes_parser.add_argument(
        "--output",
        help="write output to a file",
    )

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

        if args.feature_command == "dependency":
            root = Path(args.path).expanduser().resolve()
            feature_slugs: list[str] | None = None
            if args.features:
                feature_slugs = [s.strip() for s in args.features.split(",") if s.strip()]
            elif args.feature:
                feature_slugs = [args.feature]
            try:
                result = build_dependency_graph(root, feature_slugs=feature_slugs)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except OSError as error:
                print(f"Could not build dependency graph: {error}", file=sys.stderr)
                return 1

            if args.json:
                print(render_dependency_json(result), end="")
            else:
                print(render_dependency_text(result), end="")
            return 0

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
        if args.coverage_command == "plan":
            if args.limit is not None and args.limit < 0:
                print("--limit must be non-negative", file=sys.stderr)
                return 2
            try:
                report = build_coverage_plan_report(
                    Path(args.path),
                    use_policy=args.policy,
                    feature_filter=args.feature,
                    limit=getattr(args, "limit", None),
                )
            except InvalidFeatureSlug as error:
                print(f"Invalid feature slug: {error}", file=sys.stderr)
                return 2
            except ValueError as error:
                print(str(error), file=sys.stderr)
                return 2
            except OSError as error:
                print(f"Could not read coverage plan: {error}", file=sys.stderr)
                return 1

            if args.json:
                print(render_coverage_plan_json(report), end="")
            else:
                print(render_coverage_plan_text(report), end="")
            if report["summary"].get("feature_missing"):
                return 1
            return 0

    if args.command == "tests":
        if args.tests_command == "impact":
            try:
                report = build_test_impact_report(
                    Path(args.path),
                    changed_files=tuple(args.changed),
                    feature=args.feature,
                )
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except OSError as error:
                print(f"Could not inspect test impact: {error}", file=sys.stderr)
                return 1

            if args.json:
                print(render_test_impact_json(report), end="")
            else:
                print(render_test_impact_text(report), end="")
            if report.feature is not None and not report.feature["has_native_files"]:
                return 1
            return 0

    if args.command == "verify":
        if args.verify_command == "matrix":
            try:
                matrix = build_verification_matrix(Path(args.path), args.slug)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except OSError as error:
                print(f"Could not build verification matrix: {error}", file=sys.stderr)
                return 1

            if args.json:
                print(render_verification_matrix_json(matrix), end="")
            else:
                print(render_verification_matrix_text(matrix), end="")
            if not matrix.evidence["has_native_files"]:
                return 1
            return 0

    if args.command == "change":
        if args.change_command == "risk":
            try:
                report = build_change_risk_report(
                    Path(args.path),
                    changed_files=tuple(args.changed),
                    feature=args.feature,
                )
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except OSError as error:
                print(f"Could not build change risk report: {error}", file=sys.stderr)
                return 1

            if args.json:
                print(render_change_risk_json(report), end="")
            else:
                print(render_change_risk_text(report), end="")
            if any(
                not evidence["has_native_files"]
                for evidence in report.feature_evidence
            ):
                return 1
            return 0

    if args.command == "consistency":
        if args.consistency_command == "scan":
            try:
                report = build_consistency_report(
                    Path(args.path),
                    feature_filter=args.feature,
                    changed_files=tuple(args.changed),
                )
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except OSError as error:
                print(f"Could not build consistency report: {error}", file=sys.stderr)
                return 1

            if args.json:
                print(render_consistency_json(report), end="")
            else:
                print(render_consistency_text(report), end="")
            if args.feature and any(not feature.source_files for feature in report.features):
                return 1
            return 0

    if args.command == "hygiene":
        if args.hygiene_command == "scan":
            try:
                report = build_hygiene_scan_report(
                    Path(args.path),
                    changed_files=tuple(args.changed),
                )
            except OSError as error:
                print(f"Could not build hygiene scan report: {error}", file=sys.stderr)
                return 1

            if args.json:
                print(render_hygiene_scan_json(report), end="")
            else:
                print(render_hygiene_scan_text(report), end="")
            if args.strict and hygiene_report_has_strict_findings(report):
                return 1
            return 0

    if args.command == "security":
        if args.security_command == "cues":
            try:
                report = build_security_cue_report(
                    Path(args.path),
                    changed_files=tuple(args.changed),
                    feature=args.feature,
                )
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except OSError as error:
                print(f"Could not build security cues report: {error}", file=sys.stderr)
                return 1

            if args.json:
                print(render_security_cue_json(report), end="")
            else:
                print(render_security_cue_text(report), end="")
            if any(
                not evidence["has_native_files"]
                for evidence in report.feature_evidence
            ):
                return 1
            return 0

    if args.command == "provenance":
        if args.provenance_command == "manifest":
            try:
                manifest = build_provenance_manifest(
                    Path(args.path),
                    feature=args.feature,
                    includes=tuple(args.include),
                )
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except OSError as error:
                print(f"Could not build provenance manifest: {error}", file=sys.stderr)
                return 1

            if args.json:
                print(render_provenance_manifest_json(manifest), end="")
            else:
                print(render_provenance_manifest_text(manifest), end="")
            if any(
                not evidence["has_native_files"]
                for evidence in manifest.feature_evidence
            ):
                return 1
            return 0

    if args.command == "review":
        if args.review_command == "packet":
            try:
                packet = build_review_packet(
                    Path(args.path),
                    feature=args.feature,
                    changed_files=tuple(args.changed),
                )
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except OSError as error:
                print(f"Could not build review packet: {error}", file=sys.stderr)
                return 1

            if args.json:
                print(render_review_packet_json(packet), end="")
            else:
                print(render_review_packet_text(packet), end="")
            if packet.feature is not None and not packet.feature["has_native_files"]:
                return 1
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

    if args.command == "orchestrate":
        if args.orchestrate_command == "plan":
            try:
                report = build_orchestration_plan(
                    Path(args.path),
                    feature_filter=args.feature,
                )
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except OSError as error:
                print(f"Could not build orchestration plan: {error}", file=sys.stderr)
                return 1

            if args.json:
                print(render_orchestration_json(report), end="")
            else:
                print(render_orchestration_text(report), end="")
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

    if args.command == "retrospective" and args.retrospective_command == "analytics":
        root = Path(args.path).expanduser().resolve()
        try:
            result = build_retrospective_analytics_report(
                root,
                include_improvements=args.improvements,
                feature_slug=args.feature,
            )
        except InvalidFeatureSlug as error:
            print(str(error), file=sys.stderr)
            return 2
        except ValueError as error:
            print(str(error), file=sys.stderr)
            return 2
        except OSError as error:
            print(f"Could not build retrospective analytics: {error}", file=sys.stderr)
            return 1
        print(render_retrospective_analytics_json(result), end="")
        return 0

    if args.command == "retrospective":
        try:
            result = build_retrospective_report(
                Path(args.path),
                feature_slug=args.feature,
                limit=getattr(args, "limit", None),
            )
        except (InvalidFeatureSlug, ValueError) as error:
            print(f"Invalid retrospective option: {error}", file=sys.stderr)
            return 2
        except OSError as error:
            print(f"Could not build retrospective: {error}", file=sys.stderr)
            return 1

        if args.json:
            print(render_retrospective_json(result), end="")
        else:
            print(render_retrospective_text(result), end="")
        return retrospective_report_exit_code(result)

    if args.command == "spec":
        if args.spec_command == "diff":
            root = Path(args.path).expanduser().resolve()
            try:
                diff_result = get_git_diff(
                    args.slug,
                    root,
                    base=args.base,
                    unstaged=args.unstaged,
                )
                classification = classify_changes(diff_result, args.slug, root)
                impacts = resolve_impact(classification.changes, args.slug, root)
                remediation = generate_remediation_plan(
                    classification.changes, impacts.impacts
                )
                payload = {
                    "slug": args.slug,
                    "diff": diff_result.as_dict(),
                    "classification": classification.as_dict(),
                    "impact": impacts.as_dict(),
                    "remediation": [a.as_dict() for a in remediation],
                }
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except InvalidGitBaseError as error:
                print(str(error), file=sys.stderr)
                return 2
            except GitDiffError as error:
                print(str(error), file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not compute spec diff: {error}", file=sys.stderr)
                return 1

            if args.json:
                output = render_diff_json(diff_result)
            else:
                output = render_diff_text(diff_result)

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
                    output_path.write_text(output, encoding="utf-8")
                except OSError as error:
                    print(f"Could not write output: {error}", file=sys.stderr)
                    return 1
            else:
                if args.json:
                    print(json.dumps(payload, indent=2, sort_keys=False) + "\n", end="")
                else:
                    print(output, end="")
            return 0

        if args.spec_command == "evolution":
            root = Path(args.path).expanduser().resolve()
            try:
                diff_result = get_git_diff(args.slug, root)
                classification = classify_changes(diff_result, args.slug, root)
                impacts = resolve_impact(classification.changes, args.slug, root)
                remediation = generate_remediation_plan(
                    classification.changes, impacts.impacts
                )
                timeline = build_evolution_timeline(args.slug, root, limit=args.limit)
                payload = {
                    "slug": args.slug,
                    "diff_summary": diff_result.summary,
                    "classification": classification.as_dict(),
                    "impact": impacts.as_dict(),
                    "remediation": [a.as_dict() for a in remediation],
                    "timeline": [e.as_dict() for e in timeline],
                }
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except OSError as error:
                print(f"Could not build evolution timeline: {error}", file=sys.stderr)
                return 1

            if args.json:
                print(render_evolution_json(payload), end="")
            else:
                print(render_evolution_text(payload), end="")
            return 0

    if args.command == "release":
        if args.release_command == "notes":
            root = Path(args.path).expanduser().resolve()
            group_by = args.group_by
            valid_group_by = ("priority", "project", "status", "effort")
            if group_by not in valid_group_by:
                print(
                    f"Invalid --group-by value '{group_by}'. Use one of: {', '.join(valid_group_by)}.",
                    file=sys.stderr,
                )
                return 2
            try:
                report = build_release_notes_report(
                    root,
                    since=args.since,
                    until=args.until,
                    group_by=group_by,
                )
            except OSError as error:
                print(f"Could not build release notes: {error}", file=sys.stderr)
                return 1

            valid_formats = ("markdown", "json", "json-lines")
            output_format = args.format
            if args.json:
                output_format = "json"
            if output_format not in valid_formats:
                print(
                    f"Invalid --format value '{output_format}'. Use one of: {', '.join(valid_formats)}.",
                    file=sys.stderr,
                )
                return 2

            if output_format == "json":
                output = render_release_notes_json(report)
            elif output_format == "json-lines":
                output = render_release_notes_json_lines(report)
            else:
                output = render_release_notes_text(report)

            if args.output:
                output_path = Path(args.output).expanduser().resolve()
                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(output, encoding="utf-8")
                except OSError as error:
                    print(f"Could not write release notes: {error}", file=sys.stderr)
                    return 1

            print(output, end="")
            return 0

    if args.command == "execute":
        root = Path(args.path).expanduser().resolve()
        if args.execute_command == "plan":
            try:
                result = build_execution_plan(args.slug, root)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not build execution plan: {error}", file=sys.stderr)
                return 1

            if args.json:
                print(render_plan_json(result), end="")
            else:
                print(render_plan_text(result), end="")
            return 0

        if args.execute_command == "grade":
            try:
                result = build_grading_rubric(args.slug, root)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not build grading rubric: {error}", file=sys.stderr)
                return 1

            if args.json:
                print(render_grade_json(result), end="")
            else:
                print(render_grade_text(result), end="")
            return 0

        if args.execute_command == "loop":
            if args.max_iterations is not None and args.max_iterations < 1:
                print("--max-iterations must be at least 1", file=sys.stderr)
                return 2
            try:
                result = run_execution_loop(args.slug, root, max_iterations=args.max_iterations)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not run execution loop: {error}", file=sys.stderr)
                return 1

            if args.json:
                print(render_loop_json(result), end="")
            else:
                print(render_loop_text(result), end="")
            return 0 if result["final_status"] == "complete" else 1

    if args.command == "harness":
        root = Path(args.path).expanduser().resolve()
        if args.harness_command == "feedback":
            try:
                report = build_harness_feedback(args.slug, root)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not build harness feedback: {error}", file=sys.stderr)
                return 1

            if args.json:
                print(render_harness_feedback_json(report), end="")
            else:
                print(render_harness_feedback_text(report), end="")
            return 0 if report.status == "healthy" else 1

        if args.harness_command == "repair":
            try:
                report = build_harness_feedback(args.slug, root)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not build harness feedback: {error}", file=sys.stderr)
                return 1

            if args.json:
                payload = {
                    "feature_id": report.feature_id,
                    "repair_strategies": [s.as_dict() for s in report.repair_strategies],
                    "status": report.status,
                }
                print(json.dumps(payload, indent=2, sort_keys=True) + "\n", end="")
            else:
                lines = [
                    f"Repair strategies: {report.feature_id}",
                    f"Status: {report.status}",
                    "",
                ]
                if report.repair_strategies:
                    for strategy in report.repair_strategies:
                        lines.append(f"- {strategy.ac_id}:")
                        lines.append(f"    target: {strategy.target_file}")
                        lines.append(f"    edit: {strategy.edit_description}")
                        lines.append(f"    verify: {strategy.verification_command}")
                        lines.append(f"    success: {strategy.success_criteria}")
                else:
                    lines.append("No repair strategies needed.")
                print("\n".join(lines) + "\n", end="")
            return 0

        if args.harness_command == "quality":
            try:
                report = build_harness_quality(root)
            except OSError as error:
                print(f"Could not build harness quality: {error}", file=sys.stderr)
                return 1

            if args.json:
                print(render_harness_quality_json(report), end="")
            else:
                print(render_harness_quality_text(report), end="")
            return 0

    if args.command == "blueprint":
        if args.blueprint_command == "generate":
            root = Path(args.path).expanduser().resolve()
            try:
                report = build_spec_code_blueprint(root, args.slug)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not build blueprint: {error}", file=sys.stderr)
                return 1

            if args.output_dir:
                output_dir = Path(args.output_dir).expanduser().resolve()
                output_dir.mkdir(parents=True, exist_ok=True)
                json_path = output_dir / "blueprint.json"
                text_path = output_dir / "blueprint.md"
                if json_path.exists() and not args.force:
                    print(
                        f"Blueprint file already exists: {json_path}. "
                        "Use --force to overwrite it.",
                        file=sys.stderr,
                    )
                    return 1
                json_path.write_text(render_blueprint_json(report), encoding="utf-8")
                text_path.write_text(render_blueprint_text(report), encoding="utf-8")

            if args.json:
                print(render_blueprint_json(report), end="")
            else:
                print(render_blueprint_text(report), end="")

            if args.fail_on_gaps:
                if not report.modules or not report.functions:
                    return 3
            return 0

    if args.command == "cicd":
        if args.cicd_command == "generate":
            root = Path(args.path).expanduser().resolve()
            try:
                result = generate_pipeline(
                    root,
                    format=args.format,
                    feature_slug=args.feature,
                )
            except ValueError as error:
                print(str(error), file=sys.stderr)
                return 1
            except FileNotFoundError as error:
                print(str(error), file=sys.stderr)
                return 2
            except OSError as error:
                print(f"Could not generate pipeline: {error}", file=sys.stderr)
                return 1

            if args.output_dir:
                output_dir = Path(args.output_dir).expanduser().resolve()
                output_dir.mkdir(parents=True, exist_ok=True)
                if args.format == "github-actions":
                    workflow_dir = output_dir / ".github" / "workflows"
                    workflow_dir.mkdir(parents=True, exist_ok=True)
                    pipeline_path = workflow_dir / "specspine.yml"
                elif args.format == "gitlab-ci":
                    pipeline_path = output_dir / ".gitlab-ci.yml"
                else:
                    pipeline_path = output_dir / "specspine-pipeline.sh"

                if pipeline_path.exists() and not args.force:
                    print(
                        f"Pipeline file already exists: {pipeline_path}. "
                        "Use --force to overwrite it.",
                        file=sys.stderr,
                    )
                    return 1

                raw_content = result["raw_content"] if "raw_content" in result else ""
                if raw_content:
                    pipeline_path.write_text(raw_content, encoding="utf-8")

            if args.json:
                print(render_pipeline_json(result), end="")
            else:
                print(render_pipeline_text(result), end="")
            return 0

        if args.cicd_command == "validate":
            root = Path(args.path).expanduser().resolve()
            try:
                pipeline_result = generate_pipeline(root)
            except ValueError as error:
                print(str(error), file=sys.stderr)
                return 1
            except FileNotFoundError as error:
                print(str(error), file=sys.stderr)
                return 2
            except OSError as error:
                print(f"Could not validate pipeline: {error}", file=sys.stderr)
                return 1

            payload = {
                "ok": True,
                "pipeline_type": pipeline_result["pipeline_type"],
                "jobs_total": len(pipeline_result["jobs"]),
                "merge_conditions_total": len(pipeline_result["merge_conditions"]),
                "safety_notes": list(pipeline_result["safety_notes"]),
            }
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True) + "\n", end="")
            else:
                print(f"Pipeline validation: {pipeline_result['pipeline_type']}")
                print(f"Jobs: {payload['jobs_total']}")
                print(f"Merge conditions: {payload['merge_conditions_total']}")
                print(f"Status: ok")
            return 0

    if args.command == "scaffold":
        if args.scaffold_command == "tests":
            root = Path(args.path).expanduser().resolve()
            try:
                report = build_ac_test_scaffold(root, args.slug)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not build test scaffold: {error}", file=sys.stderr)
                return 1

            if args.output_dir:
                output_dir = Path(args.output_dir).expanduser().resolve()
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / report.scaffold_file.split("/")[-1]
            else:
                output_path = root / report.scaffold_file

            if output_path.exists() and not args.force:
                print(
                    f"Scaffold file already exists: {output_path}. "
                    "Use --force to overwrite it.",
                    file=sys.stderr,
                )
                return 1

            if not args.json or args.output_dir or args.force:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                source_lines: list[str] = []
                for method in report.test_methods:
                    method_info = {
                        "method_name": method.method_name,
                        "docstring": method.docstring,
                        "body": method.body,
                    }
                    source_lines.append(method_info)
                from .scaffold import _generate_test_class
                camel_class = report.test_methods[0].method_name.split("_")[2].title() if report.test_methods else ""
                source = _generate_test_class(args.slug, source_lines)
                output_path.write_text(source, encoding="utf-8")

            if args.update_quality and report.coverage_links:
                from .scaffold import _update_quality_file
                links_payload = [
                    {"ac_id": link.ac_id, "target_path": link.target_path}
                    for link in report.coverage_links
                ]
                _update_quality_file(root, args.slug, links_payload)

            if args.json:
                print(render_scaffold_json(report), end="")
            else:
                print(render_scaffold_text(report), end="")
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

    parser.print_help()
    return 1
