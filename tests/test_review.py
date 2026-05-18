import json
import os
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from specspine.cli import main
from specspine.review import build_review_packet
from specspine.workspace import init_workspace


def write_review_workspace(root: Path) -> None:
    init_workspace(root)
    (root / ".specspine" / "adapters").mkdir(parents=True, exist_ok=True)
    (root / ".specspine" / "fusion.yaml").write_text(
        "integration_mode: adapter\nvendored_upstream_code: false\n",
        encoding="utf-8",
    )
    (root / ".specspine" / "fusion-map.md").write_text(
        "SpecSpine fusion map\n",
        encoding="utf-8",
    )
    for adapter in ("openspec", "speckit", "superpowers"):
        (root / ".specspine" / "adapters" / f"{adapter}.md").write_text(
            "No vendored upstream code.\n",
            encoding="utf-8",
        )
    (root / "quality" / "superpowers.md").write_text(
        "Superpowers quality notes\n",
        encoding="utf-8",
    )
    (root / "quality" / "checklist.md").write_text(
        "\n".join(
            [
                "# Quality Checklist",
                "",
                "## Required Checks",
                "",
                "- [x] Tests pass.",
                "- [x] Review packet is complete.",
                "",
                "## Definition Of Done",
                "",
                "- Review evidence is local.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "src" / "specspine").mkdir(parents=True, exist_ok=True)
    (root / "src" / "specspine" / "__init__.py").write_text("", encoding="utf-8")
    (root / "src" / "specspine" / "review.py").write_text(
        "def build_review_packet():\n    return None\n",
        encoding="utf-8",
    )
    (root / "tests").mkdir(parents=True, exist_ok=True)
    (root / "tests" / "test_review.py").write_text(
        "from specspine.review import build_review_packet\n",
        encoding="utf-8",
    )


def write_review_feature(root: Path, slug: str = "review-packet") -> None:
    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)
    (root / "specs" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Review packet",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Acceptance Criteria",
                "",
                "- [x] Review packets include workspace evidence.",
                "- [x] Feature packets include readiness and tests.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "execution" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Review packet Execution",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Tasks",
                "",
                "- [x] AC001 Build workspace review evidence.",
                "- [x] AC002 Add feature evidence.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "quality" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Review packet Quality",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Required Checks",
                "",
                "- [x] Review packet checks pass.",
                "",
                "## Test Coverage",
                "",
                "- [x] AC001 -> tests/test_review.py",
                "- [x] AC002 -> tests/test_review.py",
                "",
                "## Test Plan",
                "",
                "- Run `PYTHONPATH=src python3 -m unittest tests.test_review`.",
                "",
                "## Release Readiness",
                "",
                "- [x] Review evidence is complete.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_cli(argv: list[str]) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = main(argv)
    return code, stdout.getvalue(), stderr.getvalue()


class ReviewPacketTests(TestCase):
    def test_workspace_json_shape(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_review_workspace(root)

            code, stdout, stderr = run_cli(["review", "packet", str(root), "--json"])

            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertIsNone(payload["feature_id"])
            self.assertTrue(payload["validation"]["ok"])
            self.assertFalse(payload["quality_gates"]["source_missing"])
            self.assertIn("test_impact", payload)
            self.assertGreater(len(payload["review_checks"]), 0)
            self.assertIn("specspine review packet . --json", payload["recommended_commands"])

    def test_feature_json_shape_and_changed_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_review_workspace(root)
            write_review_feature(root)

            code, stdout, stderr = run_cli(
                [
                    "review",
                    "packet",
                    str(root),
                    "--json",
                    "--feature",
                    "review-packet",
                    "--changed",
                    "src/specspine/review.py",
                ]
            )

            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["feature_id"], "review-packet")
            self.assertEqual(payload["changed_files"], ["src/specspine/review.py"])
            self.assertTrue(payload["feature"]["has_native_files"])
            self.assertTrue(payload["feature"]["ready"]["ready"])
            self.assertEqual(payload["feature"]["gaps"], [])
            self.assertIn(
                "specspine review packet . --feature review-packet --json",
                payload["recommended_commands"],
            )
            self.assertIn(
                "PYTHONPATH=src python3 -m unittest tests.test_review",
                payload["test_impact"]["recommended_commands"],
            )

    def test_text_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_review_workspace(root)

            code, stdout, stderr = run_cli(["review", "packet", str(root)])

            self.assertEqual(code, 0, stderr)
            self.assertIn("Review packet:", stdout)
            self.assertIn("Review checks:", stdout)
            self.assertIn("Recommended commands:", stdout)

    def test_invalid_feature_slug_returns_two(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_review_workspace(root)

            code, _stdout, stderr = run_cli(
                ["review", "packet", str(root), "--json", "--feature", "Bad_Slug"]
            )

            self.assertEqual(code, 2)
            self.assertIn("Invalid feature slug", stderr)

    def test_missing_feature_returns_one_with_report(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_review_workspace(root)

            code, stdout, stderr = run_cli(
                ["review", "packet", str(root), "--json", "--feature", "missing-feature"]
            )

            self.assertEqual(code, 1, stderr)
            payload = json.loads(stdout)
            self.assertFalse(payload["feature"]["has_native_files"])
            self.assertIn("review.feature_exists", [check["id"] for check in payload["review_checks"]])

    def test_report_is_local_only(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_review_workspace(root)
            write_review_feature(root)

            class GuardedEnviron(dict):
                def __getitem__(self, key: str) -> str:
                    if "TOKEN" in key.upper():
                        raise AssertionError(f"unexpected token read: {key}")
                    return super().__getitem__(key)

                def get(self, key: str, default: object = None) -> object:
                    if "TOKEN" in key.upper():
                        raise AssertionError(f"unexpected token read: {key}")
                    return super().get(key, default)

            with patch("subprocess.run", side_effect=AssertionError("unexpected process")):
                with patch("socket.create_connection", side_effect=AssertionError("unexpected network")):
                    with patch("urllib.request.urlopen", side_effect=AssertionError("unexpected network")):
                        with patch("os.environ", GuardedEnviron(os.environ)):
                            packet = build_review_packet(
                                root,
                                feature="review-packet",
                                changed_files=("src/specspine/review.py",),
                            )

            self.assertEqual(packet.feature_id, "review-packet")
            self.assertIn(
                "PYTHONPATH=src python3 -m unittest tests.test_review",
                packet.recommended_commands,
            )
