from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from specspine.adapters import build_upstream_init_commands
from specspine.fusion import FUSION_REQUIRED_FILES, build_fusion_files, init_fusion_workspace
from specspine.workspace import BASE_WORKSPACE_FILES, check_workspace


class FusionTests(TestCase):
    def test_init_fusion_workspace_creates_required_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            init_fusion_workspace(root, agent="codex")
            required = dict(BASE_WORKSPACE_FILES)
            required.update(FUSION_REQUIRED_FILES)
            _present, missing = check_workspace(root, required_files=required)

            self.assertEqual(missing, [])
            self.assertTrue((root / ".specspine" / "fusion.yaml").exists())
            self.assertTrue((root / ".specspine" / "adapters" / "openspec.md").exists())
            self.assertTrue((root / "quality" / "superpowers.md").exists())

    def test_init_fusion_workspace_enables_adapters_in_spine(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            init_fusion_workspace(root, agent="codex", include_speckit=False)
            spine = (root / ".specspine" / "spine.yaml").read_text(encoding="utf-8")

            self.assertIn("fusion:", spine)
            self.assertIn("openspec:\n    enabled: true", spine)
            self.assertIn("speckit:\n    enabled: false", spine)
            self.assertIn("superpowers:\n    enabled: true", spine)

    def test_fusion_yaml_records_adapter_mode_without_vendoring(self) -> None:
        files = build_fusion_files("codex")

        fusion_yaml = files[".specspine/fusion.yaml"]

        self.assertIn("integration_mode: adapter", fusion_yaml)
        self.assertIn("vendored_upstream_code: false", fusion_yaml)
        self.assertIn("  - openspec: \"openspec init . --tools codex\"", fusion_yaml)
        self.assertIn("  - speckit: \"specify init . --integration codex\"", fusion_yaml)

    def test_fusion_yaml_uses_agent_specific_adapter_keys(self) -> None:
        files = build_fusion_files("cursor", include_superpowers=False)

        fusion_yaml = files[".specspine/fusion.yaml"]

        self.assertIn("openspec_tool: cursor", fusion_yaml)
        self.assertIn("speckit_integration: cursor-agent", fusion_yaml)
        self.assertIn("enabled: false", fusion_yaml)

    def test_upstream_init_commands_are_constructed_from_public_clis(self) -> None:
        commands = build_upstream_init_commands(agent="cursor", force=True)
        by_key = {command.key: command for command in commands}

        self.assertEqual(
            by_key["openspec"].args,
            ("openspec", "init", ".", "--tools", "cursor", "--force"),
        )
        self.assertEqual(
            by_key["speckit"].args,
            ("specify", "init", ".", "--integration", "cursor-agent"),
        )
        self.assertEqual(by_key["superpowers"].args, ())
