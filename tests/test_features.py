import json
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from specspine.cli import main
from specspine.features import (
    FeatureBundleExistsError,
    InvalidFeatureSlug,
    create_feature_bundle,
)
from specspine.status import build_status
from specspine.validation import build_validation_report, validation_exit_code
from specspine.workspace import init_workspace


EXPECTED_FEATURE_FILES = {
    "specs/features/add-dark-mode.md",
    "execution/features/add-dark-mode.md",
    "quality/features/add-dark-mode.md",
}


class FeatureBundleTests(TestCase):
    def test_create_feature_bundle_in_plain_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            written = create_feature_bundle(
                root,
                "add-dark-mode",
                title="Add dark mode",
                why="Reduce eye strain",
            )

            self.assertEqual(
                {str(path.relative_to(root)) for path in written},
                EXPECTED_FEATURE_FILES,
            )
            for relative_path in EXPECTED_FEATURE_FILES:
                content = (root / relative_path).read_text(encoding="utf-8")
                self.assertIn("Add dark mode", content)
                self.assertIn("Reduce eye strain", content)
                self.assertIn("Feature ID: add-dark-mode", content)
                self.assertIn("Status: proposed", content)

            spec = (root / "specs" / "features" / "add-dark-mode.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("## Why", spec)
            self.assertIn("## Users", spec)
            self.assertIn("## Scope", spec)
            self.assertIn("## Non-Goals", spec)
            self.assertIn("## Acceptance Criteria", spec)

            execution = (
                root / "execution" / "features" / "add-dark-mode.md"
            ).read_text(encoding="utf-8")
            self.assertIn("## Milestones", execution)
            self.assertIn("## Tasks", execution)
            self.assertIn("## Dependencies", execution)
            self.assertIn("## Open Questions", execution)

            quality = (root / "quality" / "features" / "add-dark-mode.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("## Required Checks", quality)
            self.assertIn("## Test Plan", quality)
            self.assertIn("## Review Notes", quality)
            self.assertIn("## Release Readiness", quality)

            report = build_validation_report(root, include_features=True)
            self.assertTrue(report["ok"])
            self.assertEqual(validation_exit_code(report), 0)

    def test_create_feature_bundle_does_not_overwrite_existing_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            existing = root / "specs" / "features" / "add-dark-mode.md"
            existing.write_text("custom spec\n", encoding="utf-8")

            with self.assertRaises(FeatureBundleExistsError):
                create_feature_bundle(root, "add-dark-mode")

            self.assertEqual(existing.read_text(encoding="utf-8"), "custom spec\n")
            self.assertFalse(
                (root / "execution" / "features" / "add-dark-mode.md").exists()
            )
            self.assertFalse(
                (root / "quality" / "features" / "add-dark-mode.md").exists()
            )

    def test_create_feature_bundle_force_overwrites_existing_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            spec = root / "specs" / "features" / "add-dark-mode.md"
            spec.write_text("custom spec\n", encoding="utf-8")

            create_feature_bundle(
                root,
                "add-dark-mode",
                title="Add dark mode",
                why="Reduce eye strain",
                force=True,
            )

            content = spec.read_text(encoding="utf-8")
            self.assertNotEqual(content, "custom spec\n")
            self.assertIn("Add dark mode", content)
            self.assertIn("Reduce eye strain", content)

    def test_invalid_feature_slug_is_rejected(self) -> None:
        invalid_slugs = ["Add-dark-mode", "-bad", "bad-", "bad_slug", "bad.slug"]

        for slug in invalid_slugs:
            with self.subTest(slug=slug):
                with self.assertRaises(InvalidFeatureSlug):
                    create_feature_bundle(Path("."), slug)

    def test_single_character_feature_slug_is_valid(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            written = create_feature_bundle(root, "a")

            self.assertEqual(
                {str(path.relative_to(root)) for path in written},
                {
                    "specs/features/a.md",
                    "execution/features/a.md",
                    "quality/features/a.md",
                },
            )
            self.assertIn(
                "Feature ID: a",
                (root / "specs" / "features" / "a.md").read_text(encoding="utf-8"),
            )

    def test_feature_slug_allows_consecutive_hyphens(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            written = create_feature_bundle(root, "add--dark-mode")

            self.assertEqual(len(written), 3)
            self.assertTrue((root / "specs" / "features" / "add--dark-mode.md").exists())

    def test_feature_new_cli_creates_bundle_and_returns_zero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "new",
                        "add-dark-mode",
                        str(root),
                        "--title",
                        "Add dark mode",
                        "--why",
                        "Reduce eye strain",
                    ]
                )

            self.assertEqual(returncode, 0)
            self.assertIn("Created SpecSpine feature bundle", output.getvalue())
            for relative_path in EXPECTED_FEATURE_FILES:
                self.assertTrue((root / relative_path).exists())

    def test_feature_new_cli_rejects_invalid_slug_with_nonzero_return_code(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(["feature", "new", "BadSlug", str(root)])

            self.assertEqual(returncode, 2)
            self.assertIn("Invalid feature slug", stderr.getvalue())

    def test_feature_new_cli_does_not_overwrite_without_force(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(["feature", "new", "add-dark-mode", str(root)])

            self.assertEqual(returncode, 1)
            self.assertIn("Use --force", stderr.getvalue())
            self.assertIn(
                "existing specs/features/add-dark-mode.md",
                stderr.getvalue(),
            )
            self.assertIn(
                "existing execution/features/add-dark-mode.md",
                stderr.getvalue(),
            )
            self.assertIn(
                "existing quality/features/add-dark-mode.md",
                stderr.getvalue(),
            )

    def test_feature_new_cli_force_overwrites(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            spec = root / "specs" / "features" / "add-dark-mode.md"
            spec.write_text("custom spec\n", encoding="utf-8")

            with redirect_stdout(StringIO()):
                returncode = main(
                    [
                        "feature",
                        "new",
                        "add-dark-mode",
                        str(root),
                        "--title",
                        "Add dark mode",
                        "--force",
                    ]
                )

            self.assertEqual(returncode, 0)
            self.assertIn("Add dark mode", spec.read_text(encoding="utf-8"))

    def test_status_json_lists_feature_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")

            status = build_status(root)

            self.assertEqual(status["features"][0]["slug"], "add-dark-mode")
            self.assertTrue(status["features"][0]["complete"])
            self.assertTrue(
                status["artifacts"]["specs/features/add-dark-mode.md"]["exists"]
            )

    def test_validate_cli_can_check_feature_bundles(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["validate", str(root), "--features", "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(
                any(
                    check["id"] == "feature.id:add-dark-mode:spec"
                    and check["status"] == "pass"
                    for check in payload["checks"]
                )
            )

    def test_validate_features_skips_when_no_feature_bundles_exist(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["validate", str(root), "--features", "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(
                any(
                    check["id"] == "feature.discovery"
                    and check["status"] == "skip"
                    for check in payload["checks"]
                )
            )

    def test_validate_features_fails_when_feature_id_does_not_match_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            spec = root / "specs" / "features" / "add-dark-mode.md"
            spec.write_text(
                spec.read_text(encoding="utf-8").replace(
                    "Feature ID: add-dark-mode",
                    "Feature ID: wrong-feature",
                ),
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["validate", str(root), "--features", "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 1)
            self.assertFalse(payload["ok"])
            self.assertTrue(
                any(
                    check["id"] == "feature.id:add-dark-mode:spec"
                    and check["status"] == "fail"
                    for check in payload["checks"]
                )
            )

    def test_feature_validation_fails_incomplete_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "execution" / "features" / "add-dark-mode.md").unlink()

            report = build_validation_report(root, include_features=True)

            self.assertFalse(report["ok"])
            self.assertTrue(
                any(
                    check["id"] == "feature.required_file:add-dark-mode:execution"
                    and check["status"] == "fail"
                    for check in report["checks"]
                )
            )
