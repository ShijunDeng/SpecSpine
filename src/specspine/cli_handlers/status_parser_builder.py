"""Parser builder for the `status` CLI command."""

from __future__ import annotations

import argparse


def build_status_parser(subparsers) -> None:
    """Build the status subparser. Extracted from cli._build_status_parser."""
    status_parser = subparsers.add_parser("status", help="summarize SpecSpine workspace status")
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
    status_parser.add_argument(
        "--health",
        action="store_true",
        help="show unified health dashboard instead of standard status",
    )
