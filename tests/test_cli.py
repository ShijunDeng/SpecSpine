from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from specspine.cli import check_workspace, init_workspace


class WorkspaceTests(TestCase):
    def test_init_workspace_creates_expected_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            written = init_workspace(root)
            _present, missing = check_workspace(root)

            self.assertGreater(len(written), 0)
            self.assertEqual(missing, [])
            self.assertTrue((root / ".specspine" / "spine.yaml").exists())
            self.assertTrue((root / "specs" / "intent.md").exists())
            self.assertTrue((root / "quality" / "checklist.md").exists())

    def test_init_workspace_does_not_overwrite_without_force(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            intent = root / "specs" / "intent.md"
            intent.write_text("custom intent\n", encoding="utf-8")
            init_workspace(root)

            self.assertEqual(intent.read_text(encoding="utf-8"), "custom intent\n")

    def test_init_workspace_overwrites_with_force(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            intent = root / "specs" / "intent.md"
            intent.write_text("custom intent\n", encoding="utf-8")
            init_workspace(root, force=True)

            self.assertIn("# Intent", intent.read_text(encoding="utf-8"))
