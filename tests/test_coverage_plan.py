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

from tests.test_coverage_debt import (
    write_coverage_debt_feature,
    write_coverage_target,
    write_policy,
)


class CoveragePlanTests(TestCase):
    def test_json_reports_actionable_items_for_missing_acceptance_criteria(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_coverage_debt_feature(
                root,
                "missing-feature",
                priority="high",
                acceptance_criteria=[
                    "- [x] First behavior works.",
                    "- [x] Second behavior works.",
                ],
                coverage_lines=[
                    "- [x] AC001 -> tests/missing_target.py",
                    "- [ ] AC002 -> tests/test_coverage_plan.py",
                ],
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["coverage", "plan", str(root), "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["mode"], "universal")
            self.assertIsNone(payload["feature_filter"])
            self.assertEqual(payload["summary"]["items_total"], 1)
            self.assertEqual(payload["summary"]["items_returned"], 1)
            item = payload["items"][0]
            self.assertEqual(item["feature_id"], "missing-feature")
            self.assertEqual(item["priority"], "high")
            self.assertEqual(item["owner"], "unassigned")
            self.assertEqual(
                [criterion["id"] for criterion in item["missing_acceptance_criteria"]],
                ["AC001", "AC002"],
            )
            self.assertEqual(
                item["missing_acceptance_criteria"][0]["source_file"],
                "specs/features/missing-feature.md",
            )
            self.assertIn("tests/test_missing_feature.py", item["candidate_test_files"])
            self.assertIn("- [ ] AC001 -> tests/...", item["suggested_quality_links"])
            self.assertIn(
                "specspine feature ready missing-feature . --json --require-coverage",
                item["recommended_commands"],
            )
            self.assertIn("read-only", " ".join(payload["safety_notes"]))

    def test_text_output_includes_plan_items_and_safety_notes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_coverage_debt_feature(root, "missing-feature")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["coverage", "plan", str(root)])

            text = output.getvalue()
            self.assertEqual(returncode, 0)
            self.assertIn("Coverage remediation plan:", text)
            self.assertIn("with_plan_items=1", text)
            self.assertIn("- missing-feature (validated):", text)
            self.assertIn("Safety notes:", text)
            self.assertIn("read-only", text)

    def test_policy_mode_limits_plan_items_to_policy_selected_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_coverage_debt_feature(root, "policy-feature")
            write_coverage_debt_feature(root, "skipped-feature")
            write_policy(root, "policy-feature")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["coverage", "plan", str(root), "--json", "--policy"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["mode"], "policy")
            self.assertTrue(payload["policy_applied"])
            self.assertEqual(payload["summary"]["coverage_required_total"], 1)
            self.assertEqual(payload["summary"]["items_total"], 1)
            self.assertEqual(payload["items"][0]["feature_id"], "policy-feature")

    def test_feature_filter_focuses_summary_and_items(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_coverage_debt_feature(root, "first-feature")
            write_coverage_debt_feature(root, "second-feature")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "coverage",
                        "plan",
                        str(root),
                        "--json",
                        "--feature",
                        "second-feature",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["feature_filter"], "second-feature")
            self.assertEqual(payload["summary"]["features_scanned"], 1)
            self.assertEqual(payload["summary"]["coverage_required_total"], 1)
            self.assertEqual(payload["summary"]["missing_acceptance_criteria"], 2)
            self.assertEqual(
                [item["feature_id"] for item in payload["items"]],
                ["second-feature"],
            )

    def test_limit_trims_items_without_changing_summary(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_coverage_debt_feature(root, "first-feature")
            write_coverage_debt_feature(root, "second-feature")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["coverage", "plan", str(root), "--json", "--limit", "1"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["limit"], 1)
            self.assertEqual(payload["summary"]["items_total"], 2)
            self.assertEqual(payload["summary"]["items_returned"], 1)
            self.assertEqual(len(payload["items"]), 1)

    def test_missing_feature_returns_structured_report_and_exit_one(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "coverage",
                        "plan",
                        str(root),
                        "--json",
                        "--feature",
                        "missing-feature",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 1)
            self.assertEqual(payload["error"], "feature_not_found")
            self.assertTrue(payload["summary"]["feature_missing"])
            self.assertEqual(payload["feature_filter"], "missing-feature")
            self.assertIn(
                "specs/features/missing-feature.md",
                payload["summary"]["missing_files"],
            )

    def test_invalid_slug_and_negative_limit_return_usage_error(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stderr = StringIO()

            with redirect_stderr(stderr):
                invalid_returncode = main(
                    ["coverage", "plan", str(root), "--feature", "../bad", "--json"]
                )
            with redirect_stderr(stderr):
                limit_returncode = main(
                    ["coverage", "plan", str(root), "--limit", "-1", "--json"]
                )

            self.assertEqual(invalid_returncode, 2)
            self.assertEqual(limit_returncode, 2)
            self.assertIn("Invalid feature slug", stderr.getvalue())
            self.assertIn("--limit must be non-negative", stderr.getvalue())

    def test_no_debt_still_returns_zero_with_empty_items(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_coverage_target(root, "test_coverage_plan.py")
            write_coverage_debt_feature(
                root,
                "covered-feature",
                coverage_lines=[
                    "- [x] AC001 -> tests/test_coverage_plan.py",
                    "- [x] AC002 -> tests/test_coverage_plan.py",
                ],
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["coverage", "plan", str(root), "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["summary"]["items_total"], 0)
            self.assertEqual(payload["items"], [])

    def test_coverage_plan_does_not_call_subprocess_network_or_read_tokens(self) -> None:
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
                    returncode = main(["coverage", "plan", str(root), "--json"])

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
