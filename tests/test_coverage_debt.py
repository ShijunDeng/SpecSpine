import json
import os
import socket
import subprocess
import urllib.request
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from specspine.cli import main
from specspine.workspace import init_workspace


def write_coverage_debt_feature(
    root: Path,
    slug: str,
    *,
    status: str = "validated",
    include_execution: bool = True,
    include_quality: bool = True,
    acceptance_criteria: list[str] | None = None,
    coverage_lines: list[str] | None = None,
    priority: str | None = None,
) -> None:
    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)
    metadata = [f"Priority: {priority}"] if priority is not None else []
    criteria = acceptance_criteria or [
        "- [x] First behavior works.",
        "- [x] Second behavior works.",
    ]
    (root / "specs" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# {slug}",
                "",
                f"Feature ID: {slug}",
                f"Status: {status}",
                *metadata,
                "",
                "## Acceptance Criteria",
                "",
                *criteria,
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    if include_execution:
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
                    "- [x] Implement behavior.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
    if include_quality:
        coverage_section: list[str] = []
        if coverage_lines is not None:
            coverage_section = ["", "## Test Coverage", "", *coverage_lines]
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
                    "- [x] Checks pass.",
                    "",
                    "## Test Plan",
                    "",
                    "- Run `python -m unittest`.",
                    "",
                    "## Release Readiness",
                    "",
                    "- [x] Ready for release.",
                    *coverage_section,
                ]
            )
            + "\n",
            encoding="utf-8",
        )


def write_coverage_target(root: Path, name: str = "test_coverage_debt.py") -> None:
    target = root / "tests" / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("def test_placeholder():\n    pass\n", encoding="utf-8")


def write_policy(root: Path, feature_id: str) -> None:
    write_policy_body(
        root,
        [
            "readiness:",
            "  require_coverage:",
            "    enabled: true",
            "    feature_ids:",
            f"      - {feature_id}",
        ],
    )


def write_policy_body(root: Path, lines: list[str]) -> None:
    policy = root / ".specspine" / "policy.yaml"
    policy.parent.mkdir(parents=True, exist_ok=True)
    policy.write_text("\n".join(lines) + "\n", encoding="utf-8")


class CoverageDebtTests(TestCase):
    def test_json_universal_counts_covered_and_missing_criteria(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_coverage_target(root)
            write_coverage_debt_feature(
                root,
                "covered-feature",
                coverage_lines=[
                    "- [x] AC001 -> tests/test_coverage_debt.py::test_first",
                    "- [x] AC002 -> tests/test_coverage_debt.py::test_second",
                ],
            )
            write_coverage_debt_feature(root, "missing-feature")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["coverage", "debt", str(root), "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["mode"], "universal")
            self.assertEqual(payload["features_total"], 2)
            self.assertEqual(payload["coverage_required_total"], 2)
            self.assertEqual(payload["features_with_debt"], 1)
            self.assertEqual(payload["acceptance_criteria_total"], 4)
            self.assertEqual(payload["covered_acceptance_criteria"], 2)
            self.assertEqual(payload["missing_acceptance_criteria"], 2)
            records = {feature["feature_id"]: feature for feature in payload["features"]}
            self.assertEqual(records["covered-feature"]["missing_acceptance_criteria"], 0)
            self.assertEqual(
                records["missing-feature"]["missing_acceptance_criterion_ids"],
                ["AC001", "AC002"],
            )
            self.assertIn(
                "specspine feature ready missing-feature . --json --require-coverage",
                payload["recommended_commands"],
            )

    def test_text_shows_only_features_with_debt_and_commands(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_coverage_target(root)
            write_coverage_debt_feature(
                root,
                "covered-feature",
                coverage_lines=[
                    "- [x] AC001 -> tests/test_coverage_debt.py",
                    "- [x] AC002 -> tests/test_coverage_debt.py",
                ],
            )
            write_coverage_debt_feature(root, "missing-feature")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["coverage", "debt", str(root)])

            text = output.getvalue()
            self.assertEqual(returncode, 0)
            self.assertIn("Coverage debt:", text)
            self.assertIn("with_debt=1", text)
            self.assertIn("- missing-feature (validated): missing=2 [AC001, AC002]", text)
            self.assertIn(
                "command: specspine feature ready missing-feature . --json --require-coverage",
                text,
            )
            self.assertNotIn("- covered-feature", text)

    def test_feature_with_checked_existing_targets_for_all_criteria_has_no_debt(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_coverage_target(root)
            write_coverage_debt_feature(
                root,
                "covered-feature",
                coverage_lines=[
                    "- [x] AC001 -> tests/test_coverage_debt.py",
                    "- [x] AC002 -> tests/test_coverage_debt.py",
                ],
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["coverage", "debt", str(root), "--json"])

            payload = json.loads(output.getvalue())
            record = payload["features"][0]
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["features_with_debt"], 0)
            self.assertEqual(record["covered_acceptance_criteria"], 2)
            self.assertEqual(record["missing_acceptance_criteria"], 0)
            self.assertEqual(record["recommended_commands"], [])

    def test_link_classification_reports_open_missing_target_and_unknown_ac_links(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_coverage_target(root)
            write_coverage_debt_feature(
                root,
                "classified-feature",
                coverage_lines=[
                    "- [ ] AC001 -> tests/test_coverage_debt.py",
                    "- [x] AC002 -> tests/missing_coverage_debt.py",
                    "- [x] AC999 -> tests/test_coverage_debt.py",
                    "- [x] No AC marker -> tests/test_coverage_debt.py",
                ],
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["coverage", "debt", str(root), "--json"])

            payload = json.loads(output.getvalue())
            record = payload["features"][0]
            self.assertEqual(returncode, 0)
            self.assertEqual(record["open_coverage_link_ids"], ["COV001"])
            self.assertEqual(record["missing_target_link_ids"], ["COV002"])
            self.assertEqual(
                record["unknown_acceptance_criterion_link_ids"],
                ["COV003", "COV004"],
            )
            self.assertEqual(
                record["missing_acceptance_criterion_ids"],
                ["AC001", "AC002"],
            )

    def test_missing_criteria_match_feature_ready_require_coverage(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_coverage_target(root)
            write_coverage_debt_feature(
                root,
                "semantics-feature",
                acceptance_criteria=[
                    "- [x] First behavior works.",
                    "- [x] Second behavior works.",
                    "- [x] Third behavior works.",
                ],
                coverage_lines=[
                    "- [x] AC001 -> tests/test_coverage_debt.py::test_first",
                    "- [ ] AC002 -> tests/test_coverage_debt.py::test_second",
                    "- [x] AC003 -> tests/missing_coverage_debt.py::test_third",
                    "- [x] AC999 -> tests/test_coverage_debt.py::test_unknown",
                ],
            )
            debt_output = StringIO()
            ready_output = StringIO()

            with redirect_stdout(debt_output):
                debt_returncode = main(["coverage", "debt", str(root), "--json"])
            with redirect_stdout(ready_output):
                ready_returncode = main(
                    [
                        "feature",
                        "ready",
                        "semantics-feature",
                        str(root),
                        "--json",
                        "--require-coverage",
                    ]
                )

            debt_payload = json.loads(debt_output.getvalue())
            ready_payload = json.loads(ready_output.getvalue())
            debt_record = debt_payload["features"][0]
            blocking = {check["id"]: check for check in ready_payload["blocking_checks"]}
            ready_message = blocking["feature.test_coverage"]["message"]
            self.assertEqual(debt_returncode, 0)
            self.assertEqual(ready_returncode, 1)
            self.assertEqual(debt_record["covered_acceptance_criteria"], 1)
            self.assertEqual(
                debt_record["missing_acceptance_criterion_ids"],
                ["AC002", "AC003"],
            )
            self.assertIn("AC002", ready_message)
            self.assertIn("AC003", ready_message)
            self.assertNotIn("AC001", ready_message)
            self.assertNotIn("AC999", ready_message)

    def test_partial_bundle_missing_quality_does_not_crash(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_coverage_debt_feature(
                root,
                "partial-feature",
                include_execution=False,
                include_quality=False,
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["coverage", "debt", str(root), "--json"])

            payload = json.loads(output.getvalue())
            record = payload["features"][0]
            self.assertEqual(returncode, 0)
            self.assertEqual(record["missing_acceptance_criteria"], 2)
            self.assertIn("execution/features/partial-feature.md", record["missing_files"])
            self.assertIn("quality/features/partial-feature.md", record["missing_files"])

    def test_policy_mode_limits_required_debt_to_policy_selected_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_coverage_debt_feature(root, "policy-feature")
            write_coverage_debt_feature(root, "skipped-feature")
            write_policy(root, "policy-feature")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["coverage", "debt", str(root), "--json", "--policy"])

            payload = json.loads(output.getvalue())
            records = {feature["feature_id"]: feature for feature in payload["features"]}
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["mode"], "policy")
            self.assertTrue(payload["policy_applied"])
            self.assertEqual(payload["features_total"], 2)
            self.assertEqual(payload["coverage_required_total"], 1)
            self.assertEqual(payload["policy_coverage_required_total"], 1)
            self.assertEqual(payload["features_with_debt"], 1)
            self.assertEqual(payload["missing_acceptance_criteria"], 2)
            self.assertTrue(records["policy-feature"]["coverage_required"])
            self.assertTrue(records["policy-feature"]["policy_coverage_required"])
            self.assertFalse(records["skipped-feature"]["coverage_required"])
            self.assertFalse(records["skipped-feature"]["policy_coverage_required"])
            self.assertEqual(payload["summary"]["features_skipped"], 1)
            self.assertIn(
                "specspine feature ready policy-feature . --json --policy",
                payload["recommended_commands"],
            )

    def test_policy_mode_uses_priority_and_status_selectors_like_feature_ready_policy(
        self,
    ) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_coverage_debt_feature(
                root,
                "priority-feature",
                priority="high",
                status="validated",
            )
            write_coverage_debt_feature(
                root,
                "status-feature",
                priority="low",
                status="implemented",
            )
            write_coverage_debt_feature(
                root,
                "skipped-feature",
                priority="low",
                status="validated",
            )
            write_policy_body(
                root,
                [
                    "readiness:",
                    "  require_coverage:",
                    "    enabled: true",
                    "    priorities:",
                    "      - high",
                    "    statuses:",
                    "      - implemented",
                ],
            )
            debt_output = StringIO()
            priority_ready_output = StringIO()
            skipped_ready_output = StringIO()

            with redirect_stdout(debt_output):
                debt_returncode = main(
                    ["coverage", "debt", str(root), "--json", "--policy"]
                )
            with redirect_stdout(priority_ready_output):
                priority_ready_returncode = main(
                    [
                        "feature",
                        "ready",
                        "priority-feature",
                        str(root),
                        "--json",
                        "--policy",
                    ]
                )
            with redirect_stdout(skipped_ready_output):
                skipped_ready_returncode = main(
                    [
                        "feature",
                        "ready",
                        "skipped-feature",
                        str(root),
                        "--json",
                        "--policy",
                    ]
                )

            debt_payload = json.loads(debt_output.getvalue())
            priority_ready_payload = json.loads(priority_ready_output.getvalue())
            skipped_ready_payload = json.loads(skipped_ready_output.getvalue())
            records = {feature["feature_id"]: feature for feature in debt_payload["features"]}
            skipped_ready_checks = {
                check["id"] for check in skipped_ready_payload["checks"]
            }
            self.assertEqual(debt_returncode, 0)
            self.assertEqual(priority_ready_returncode, 1)
            self.assertEqual(skipped_ready_returncode, 0)
            self.assertEqual(debt_payload["features_total"], 3)
            self.assertEqual(debt_payload["coverage_required_total"], 2)
            self.assertEqual(debt_payload["policy_coverage_required_total"], 2)
            self.assertEqual(debt_payload["features_with_debt"], 2)
            self.assertEqual(debt_payload["missing_acceptance_criteria"], 4)
            self.assertTrue(records["priority-feature"]["coverage_required"])
            self.assertTrue(records["priority-feature"]["policy_coverage_required"])
            self.assertTrue(records["status-feature"]["coverage_required"])
            self.assertTrue(records["status-feature"]["policy_coverage_required"])
            self.assertFalse(records["skipped-feature"]["coverage_required"])
            self.assertFalse(records["skipped-feature"]["policy_coverage_required"])
            self.assertTrue(priority_ready_payload["coverage_required"])
            self.assertTrue(priority_ready_payload["coverage_required_by_policy"])
            self.assertFalse(skipped_ready_payload["coverage_required_by_policy"])
            self.assertNotIn("coverage_required", skipped_ready_payload)
            self.assertNotIn("feature.test_coverage", skipped_ready_checks)

    def test_coverage_debt_does_not_call_subprocess_network_or_read_tokens(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_coverage_debt_feature(root, "missing-feature")
            output = StringIO()
            token_names = {
                "GH_TOKEN",
                "GITHUB_API_TOKEN",
                "GITHUB_PAT",
                "GITHUB_TOKEN",
            }
            environ_type = os.environ.__class__
            original_get = environ_type.get
            original_getitem = environ_type.__getitem__
            original_contains = environ_type.__contains__

            def guarded_get(environ, key, default=None):
                if key in token_names:
                    raise AssertionError(f"token read: {key}")
                return original_get(environ, key, default)

            def guarded_getitem(environ, key):
                if key in token_names:
                    raise AssertionError(f"token read: {key}")
                return original_getitem(environ, key)

            def guarded_contains(environ, key):
                if key in token_names:
                    raise AssertionError(f"token read: {key}")
                return original_contains(environ, key)

            with patch.dict(
                "os.environ",
                {
                    "GH_TOKEN": "secret-gh-token",
                    "GITHUB_API_TOKEN": "secret-github-api-token",
                    "GITHUB_PAT": "secret-github-pat",
                    "GITHUB_TOKEN": "secret-github-token",
                    "PATH": "",
                },
                clear=False,
            ), patch.object(environ_type, "get", guarded_get), patch.object(
                environ_type, "__getitem__", guarded_getitem
            ), patch.object(
                environ_type, "__contains__", guarded_contains
            ), patch.object(
                subprocess, "run"
            ) as subprocess_run, patch.object(
                subprocess, "Popen"
            ) as subprocess_popen, patch.object(
                urllib.request, "urlopen"
            ) as urlopen, patch.object(
                socket, "create_connection"
            ) as create_connection, patch.object(
                socket.socket, "connect"
            ) as socket_connect:
                with redirect_stdout(output):
                    returncode = main(["coverage", "debt", str(root), "--json"])

            self.assertEqual(returncode, 0)
            subprocess_run.assert_not_called()
            subprocess_popen.assert_not_called()
            urlopen.assert_not_called()
            create_connection.assert_not_called()
            socket_connect.assert_not_called()
            self.assertNotIn("secret-gh-token", output.getvalue())
            self.assertNotIn("secret-github-api-token", output.getvalue())
            self.assertNotIn("secret-github-pat", output.getvalue())
            self.assertNotIn("secret-github-token", output.getvalue())

    def test_coverage_debt_help_is_available(self) -> None:
        output = StringIO()
        with self.assertRaises(SystemExit) as raised, redirect_stdout(output):
            main(["coverage", "debt", "--help"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("specspine coverage debt", output.getvalue())
