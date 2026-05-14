import json
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from specspine.cli import main
from specspine.policy import load_workspace_policy
from specspine.workspace import init_workspace


def write_policy(root: Path, body: str) -> None:
    policy_path = root / ".specspine" / "policy.yaml"
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    policy_path.write_text(body, encoding="utf-8")


def write_feature(
    root: Path,
    slug: str,
    *,
    status: str = "validated",
    priority: str = "medium",
    include_coverage: bool = False,
) -> None:
    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)
    (root / "specs" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# {slug}",
                "",
                f"Feature ID: {slug}",
                f"Status: {status}",
                f"Priority: {priority}",
                "Owner: Platform",
                "",
                "## Acceptance Criteria",
                "",
                "- [x] First outcome works.",
                "- [x] Second outcome works.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "execution" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# {slug} Execution",
                "",
                f"Feature ID: {slug}",
                f"Status: {status}",
                "",
                "## Tasks",
                "",
                "- [x] Implement the behavior.",
                "- [x] Add verification.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    coverage_lines: list[str] = []
    if include_coverage:
        target = root / "tests" / f"test_{slug.replace('-', '_')}.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# coverage target\n", encoding="utf-8")
        coverage_lines = [
            "",
            "## Test Coverage",
            "",
            f"- [x] AC001 -> tests/{target.name}",
            f"- [x] AC002 -> tests/{target.name}",
        ]
    (root / "quality" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# {slug} Quality",
                "",
                f"Feature ID: {slug}",
                f"Status: {status}",
                "",
                "## Required Checks",
                "",
                "- [x] Unit tests pass.",
                "- [x] Documentation updated.",
                "",
                "## Test Plan",
                "",
                "- Run local unit tests.",
                "",
                "## Release Readiness",
                "",
                "- [x] Reviewer gate passes.",
                "- [x] No release blockers remain.",
                *coverage_lines,
            ]
        )
        + "\n",
        encoding="utf-8",
    )


class WorkspacePolicyTests(TestCase):
    def test_policy_missing_reports_defaults_without_failure(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["policy", str(root), "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertTrue(payload["source_missing"])
            require_coverage = payload["readiness"]["require_coverage"]
            self.assertFalse(require_coverage["enabled"])
            self.assertFalse(require_coverage["default"])
            self.assertEqual(require_coverage["priorities"], [])
            self.assertEqual(require_coverage["statuses"], [])
            self.assertEqual(require_coverage["feature_ids"], [])
            self.assertEqual(payload["summary"]["warning_count"], 0)

    def test_policy_parser_supports_require_coverage_selectors(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_policy(
                root,
                "\n".join(
                    [
                        "readiness:",
                        "  require_coverage:",
                        "    enabled: true",
                        "    default: false",
                        "    priorities:",
                        "      - high",
                        "    statuses:",
                        "      - implemented",
                        "      - validated",
                        "    feature_ids:",
                        "      - critical-feature",
                    ]
                )
                + "\n",
            )

            policy = load_workspace_policy(root)

            self.assertFalse(policy.source_missing)
            self.assertTrue(policy.require_coverage.enabled)
            self.assertFalse(policy.require_coverage.default)
            self.assertEqual(policy.require_coverage.priorities, ("high",))
            self.assertEqual(policy.require_coverage.statuses, ("implemented", "validated"))
            self.assertEqual(policy.require_coverage.feature_ids, ("critical-feature",))
            self.assertEqual(policy.require_coverage.warnings, ())

    def test_invalid_policy_values_warn_without_failure(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_policy(
                root,
                "\n".join(
                    [
                        "readiness:",
                        "  require_coverage:",
                        "    enabled: true",
                        "    default: false",
                        "    priorities:",
                        "      - urgent",
                        "    statuses:",
                        "      - shipped",
                    ]
                )
                + "\n",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["policy", str(root), "--json"])

            payload = json.loads(output.getvalue())
            warnings = payload["readiness"]["require_coverage"]["warnings"]
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["summary"]["warning_count"], 2)
            self.assertIn("Unknown readiness.require_coverage priority: urgent.", warnings)
            self.assertIn("Unknown readiness.require_coverage status: shipped.", warnings)

    def test_invalid_policy_selectors_warn_and_preserve_valid_selectors(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature(root, "target-feature", priority="high", status="validated")
            write_policy(
                root,
                "\n".join(
                    [
                        "readiness:",
                        "  require_coverage:",
                        "    enabled: true",
                        "    default: false",
                        "    priorities:",
                        "      - high",
                        "      - urgent",
                        "    statuses:",
                        "      - validated",
                        "      - shipped",
                    ]
                )
                + "\n",
            )
            policy_output = StringIO()
            ready_output = StringIO()

            with redirect_stdout(policy_output):
                policy_returncode = main(["policy", str(root), "--json"])
            with redirect_stdout(ready_output):
                ready_returncode = main(
                    ["feature", "ready", "target-feature", str(root), "--json", "--policy"]
                )

            policy_payload = json.loads(policy_output.getvalue())
            ready_payload = json.loads(ready_output.getvalue())
            require_coverage = policy_payload["readiness"]["require_coverage"]
            self.assertEqual(policy_returncode, 0)
            self.assertEqual(require_coverage["priorities"], ["high"])
            self.assertEqual(require_coverage["statuses"], ["validated"])
            self.assertEqual(
                require_coverage["warnings"],
                [
                    "Unknown readiness.require_coverage priority: urgent.",
                    "Unknown readiness.require_coverage status: shipped.",
                ],
            )
            self.assertEqual(ready_returncode, 1)
            self.assertTrue(ready_payload["coverage_required_by_policy"])
            self.assertTrue(ready_payload["coverage_required"])

    def test_disabled_policy_ignores_default_and_all_selectors(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature(root, "target-feature", priority="high", status="validated")
            write_policy(
                root,
                "\n".join(
                    [
                        "readiness:",
                        "  require_coverage:",
                        "    enabled: false",
                        "    default: true",
                        "    priorities:",
                        "      - high",
                        "    statuses:",
                        "      - validated",
                        "    feature_ids:",
                        "      - target-feature",
                    ]
                )
                + "\n",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "ready", "target-feature", str(root), "--json", "--policy"]
                )

            payload = json.loads(output.getvalue())
            check_ids = [check["id"] for check in payload["checks"]]
            self.assertEqual(returncode, 0)
            self.assertTrue(payload["policy_applied"])
            self.assertFalse(payload["coverage_required_by_policy"])
            self.assertNotIn("coverage_required", payload)
            self.assertNotIn("feature.test_coverage", check_ids)

    def test_empty_policy_selector_lists_do_not_require_coverage(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature(root, "target-feature", priority="high", status="validated")
            write_policy(
                root,
                "\n".join(
                    [
                        "readiness:",
                        "  require_coverage:",
                        "    enabled: true",
                        "    default: false",
                        "    priorities:",
                        "    statuses:",
                        "    feature_ids:",
                    ]
                )
                + "\n",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "ready", "target-feature", str(root), "--json", "--policy"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertTrue(payload["policy_applied"])
            self.assertFalse(payload["coverage_required_by_policy"])
            self.assertNotIn("coverage_required", payload)

    def test_feature_ready_policy_selectors_require_coverage(self) -> None:
        cases = (
            ("by-id", "feature_ids:\n      - target-feature", "target-feature", "medium", "validated"),
            ("by-priority", "priorities:\n      - high", "target-feature", "high", "validated"),
            ("by-status", "statuses:\n      - implemented", "target-feature", "medium", "implemented"),
            ("by-default", "default: true", "target-feature", "medium", "validated"),
        )
        for label, selector, slug, priority, status in cases:
            with self.subTest(label=label), TemporaryDirectory() as tmp:
                root = Path(tmp)
                init_workspace(root)
                write_feature(root, slug, priority=priority, status=status)
                write_policy(
                    root,
                    "\n".join(
                        [
                            "readiness:",
                            "  require_coverage:",
                            "    enabled: true",
                            "    default: false",
                            *[f"    {line}" for line in selector.splitlines()],
                        ]
                    )
                    + "\n",
                )
                output = StringIO()

                with redirect_stdout(output):
                    returncode = main(["feature", "ready", slug, str(root), "--json", "--policy"])

                payload = json.loads(output.getvalue())
                self.assertEqual(returncode, 1)
                self.assertTrue(payload["policy_applied"])
                self.assertTrue(payload["coverage_required_by_policy"])
                self.assertTrue(payload["coverage_required"])
                self.assertIn("feature.test_coverage", [check["id"] for check in payload["checks"]])

    def test_feature_ready_require_coverage_overrides_policy(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature(root, "target-feature")
            write_policy(
                root,
                "\n".join(
                    [
                        "readiness:",
                        "  require_coverage:",
                        "    enabled: true",
                        "    default: false",
                        "    feature_ids:",
                        "      - other-feature",
                    ]
                )
                + "\n",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "ready",
                        "target-feature",
                        str(root),
                        "--json",
                        "--policy",
                        "--require-coverage",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 1)
            self.assertTrue(payload["policy_applied"])
            self.assertFalse(payload["coverage_required_by_policy"])
            self.assertTrue(payload["coverage_required"])
            self.assertEqual(
                payload["policy_source"],
                str(root.resolve() / ".specspine" / "policy.yaml"),
            )

    def test_status_feature_policy_requires_feature_summaries(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                returncode = main(["status", str(root), "--feature-policy"])

            self.assertEqual(returncode, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("--feature-policy", stderr.getvalue())
            self.assertIn("require --feature-summaries", stderr.getvalue())

    def test_status_feature_policy_ready_filter_uses_policy_readiness(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature(root, "covered-feature", include_coverage=True)
            write_feature(root, "missing-coverage")
            write_policy(
                root,
                "\n".join(
                    [
                        "readiness:",
                        "  require_coverage:",
                        "    enabled: true",
                        "    default: false",
                        "    feature_ids:",
                        "      - covered-feature",
                        "      - missing-coverage",
                    ]
                )
                + "\n",
            )
            ready_output = StringIO()
            not_ready_output = StringIO()

            with redirect_stdout(ready_output):
                ready_returncode = main(
                    [
                        "status",
                        str(root),
                        "--json",
                        "--feature-summaries",
                        "--feature-policy",
                        "--feature-ready",
                        "yes",
                        "--feature-sort",
                        "slug",
                    ]
                )
            with redirect_stdout(not_ready_output):
                not_ready_returncode = main(
                    [
                        "status",
                        str(root),
                        "--json",
                        "--feature-summaries",
                        "--feature-policy",
                        "--feature-ready",
                        "no",
                        "--feature-sort",
                        "slug",
                    ]
                )

            ready_payload = json.loads(ready_output.getvalue())
            not_ready_payload = json.loads(not_ready_output.getvalue())
            self.assertEqual(ready_returncode, 0)
            self.assertEqual(not_ready_returncode, 0)
            self.assertEqual(
                [summary["slug"] for summary in ready_payload["feature_summaries"]],
                ["covered-feature"],
            )
            self.assertEqual(
                [summary["slug"] for summary in not_ready_payload["feature_summaries"]],
                ["missing-coverage"],
            )
            self.assertTrue(
                ready_payload["feature_summaries"][0]["policy_coverage_required"]
            )
            self.assertTrue(
                not_ready_payload["feature_summaries"][0]["policy_coverage_required"]
            )
            self.assertIn(
                "Resolve blocking readiness check(s): feature.test_coverage",
                not_ready_payload["feature_summaries"][0]["next_actions"],
            )

    def test_status_feature_policy_default_true_requires_all_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature(root, "first-feature", priority="low", status="validated")
            write_feature(root, "second-feature", priority="high", status="implemented")
            write_policy(
                root,
                "\n".join(
                    [
                        "readiness:",
                        "  require_coverage:",
                        "    enabled: true",
                        "    default: true",
                    ]
                )
                + "\n",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "status",
                        str(root),
                        "--json",
                        "--feature-summaries",
                        "--feature-policy",
                        "--feature-sort",
                        "slug",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            summaries = payload["feature_summaries"]
            self.assertEqual(
                [summary["slug"] for summary in summaries],
                ["first-feature", "second-feature"],
            )
            for summary in summaries:
                self.assertTrue(summary["coverage_required"])
                self.assertTrue(summary["policy_coverage_required"])
                self.assertFalse(summary["ready"])
                self.assertIn(
                    "Resolve blocking readiness check(s): feature.test_coverage",
                    summary["next_actions"],
                )

    def test_default_status_and_ready_remain_compatible(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature(root, "target-feature")
            write_policy(
                root,
                "\n".join(
                    [
                        "readiness:",
                        "  require_coverage:",
                        "    enabled: true",
                        "    default: true",
                    ]
                )
                + "\n",
            )
            ready_output = StringIO()
            status_output = StringIO()

            with redirect_stdout(ready_output):
                ready_returncode = main(["feature", "ready", "target-feature", str(root), "--json"])
            with redirect_stdout(status_output):
                status_returncode = main(
                    ["status", str(root), "--json", "--feature-summaries"]
                )

            ready_payload = json.loads(ready_output.getvalue())
            status_payload = json.loads(status_output.getvalue())
            self.assertEqual(ready_returncode, 0)
            self.assertNotIn("policy_applied", ready_payload)
            self.assertNotIn("coverage_required", ready_payload)
            self.assertEqual(status_returncode, 0)
            summary = status_payload["feature_summaries"][0]
            self.assertNotIn("policy_coverage_required", summary)
            self.assertNotIn("policy_source", summary)
            self.assertTrue(summary["ready"])
