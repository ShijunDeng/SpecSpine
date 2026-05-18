import json
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from specspine.cli import main
from specspine.features import (
    build_feature_ready_report,
    build_proposal_files,
    parse_acceptance_criteria,
    parse_feature_tasks,
    parse_quality_checks,
    parse_test_coverage,
)
from specspine.proposer import (
    InvalidProposalIntent,
    MAX_INTENT_CHARS,
    generate_ears_criteria,
    generate_slug_from_intent,
    normalize_intent,
    parse_intent,
    validate_intent,
)
from specspine.validation import build_validation_report
from specspine.workspace import init_workspace


def run_cli(argv: list[str]) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = main(argv)
    return code, stdout.getvalue(), stderr.getvalue()


class ProposalGeneratorTests(TestCase):
    def test_parse_intent_and_criteria_are_deterministic_for_complex_intent(self) -> None:
        parsed = parse_intent(
            "add dark mode toggle and user preferences with persistence"
        )
        criteria = generate_ears_criteria(parsed)

        self.assertEqual(parsed["action"], "add")
        self.assertEqual(parsed["target"], "toggle")
        self.assertTrue(parsed["is_complex"])
        self.assertGreaterEqual(len(criteria), 3)
        self.assertTrue(all("The system SHALL" in item["text"] for item in criteria))
        self.assertTrue(any("WHEN" in item["text"] for item in criteria))
        self.assertTrue(any("user preferences" in item["text"] for item in criteria))

    def test_empty_and_punctuation_only_intents_are_rejected(self) -> None:
        for intent in ("", "   ", "?!.,;"):
            with self.subTest(intent=intent):
                with self.assertRaises(InvalidProposalIntent):
                    validate_intent(intent)

    def test_slug_generation_uses_meaningful_words_and_valid_slug_shape(self) -> None:
        self.assertEqual(
            generate_slug_from_intent("Add dark mode toggle!"),
            "add-dark-mode-toggle",
        )

    def test_long_intent_is_truncated_with_warning(self) -> None:
        intent = "add " + ("searchable audit history " * 300)

        normalized, warnings = normalize_intent(intent)
        files = build_proposal_files("audit-history", intent)

        self.assertEqual(len(normalized), MAX_INTENT_CHARS)
        self.assertEqual(len(warnings), 1)
        self.assertIn("truncated", warnings[0])
        self.assertIn(normalized, files["specs/features/audit-history.md"])
        self.assertNotIn(intent, files["specs/features/audit-history.md"])

    def test_build_proposal_files_have_traceable_sections_without_todos(self) -> None:
        files = build_proposal_files(
            "dark-mode-toggle",
            "add dark mode toggle and user preferences with persistence",
            owner="Platform",
            milestone="Beta",
            target_release="0.3.0",
            project="Native feature bundles",
            effort="M",
        )

        spec = files["specs/features/dark-mode-toggle.md"]
        execution = files["execution/features/dark-mode-toggle.md"]
        quality = files["quality/features/dark-mode-toggle.md"]
        combined = "\n".join(files.values())

        self.assertNotIn("TODO", combined)
        acceptance = parse_acceptance_criteria(
            spec,
            source_file="specs/features/dark-mode-toggle.md",
        )
        tasks = parse_feature_tasks(
            execution,
            source_file="execution/features/dark-mode-toggle.md",
        )
        checks = parse_quality_checks(
            quality,
            source_file="quality/features/dark-mode-toggle.md",
        )
        coverage = parse_test_coverage(
            quality,
            source_file="quality/features/dark-mode-toggle.md",
            root=Path("."),
        )

        self.assertGreaterEqual(len(acceptance), 3)
        self.assertGreaterEqual(len(tasks), 3)
        self.assertEqual(len(checks), len(acceptance))
        self.assertEqual(len(coverage), len(acceptance))
        self.assertIn("_Boundary:", execution)
        self.assertIn("_Depends:", execution)
        self.assertIn("Owner: Platform", spec)
        self.assertIn("Target Release: 0.3.0", spec)


class ProposalCliTests(TestCase):
    def test_text_write_creates_three_files_and_prints_created_paths(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            code, stdout, stderr = run_cli(
                [
                    "propose",
                    "add dark mode toggle",
                    str(root),
                    "--slug",
                    "dark-mode-toggle",
                ]
            )

            self.assertEqual(code, 0, stderr)
            self.assertIn(
                "Created SpecSpine proposal bundle 'dark-mode-toggle'", stdout
            )
            expected_paths = (
                "specs/features/dark-mode-toggle.md",
                "execution/features/dark-mode-toggle.md",
                "quality/features/dark-mode-toggle.md",
            )
            for relative_path in expected_paths:
                with self.subTest(relative_path=relative_path):
                    self.assertIn(f"created {relative_path}", stdout)
                    self.assertTrue((root / relative_path).exists())

    def test_dry_run_text_prints_content_without_writing_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            code, stdout, stderr = run_cli(
                [
                    "propose",
                    "add dark mode toggle",
                    str(root),
                    "--slug",
                    "dark-mode-toggle",
                    "--dry-run",
                ]
            )

            self.assertEqual(code, 0, stderr)
            self.assertIn("specs/features/dark-mode-toggle.md", stdout)
            self.assertIn("The system SHALL", stdout)
            self.assertFalse((root / "specs/features/dark-mode-toggle.md").exists())

    def test_json_write_outputs_stable_payload_and_writes_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            code, stdout, stderr = run_cli(
                [
                    "propose",
                    "add dark mode toggle",
                    str(root),
                    "--slug",
                    "dark-mode-toggle",
                    "--json",
                    "--priority",
                    "high",
                    "--owner",
                    "Platform",
                    "--milestone",
                    "Beta",
                    "--target-release",
                    "0.3.0",
                    "--project",
                    "Native feature bundles",
                    "--effort",
                    "M",
                ]
            )

            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["slug"], "dark-mode-toggle")
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["metadata"]["priority"], "high")
            self.assertEqual(payload["metadata"]["target_release"], "0.3.0")
            self.assertEqual(
                sorted(payload["written_paths"]),
                [
                    "execution/features/dark-mode-toggle.md",
                    "quality/features/dark-mode-toggle.md",
                    "specs/features/dark-mode-toggle.md",
                ],
            )
            self.assertTrue((root / "specs/features/dark-mode-toggle.md").exists())

    def test_conflict_fails_without_force_and_force_overwrites(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            first = run_cli(
                [
                    "propose",
                    "add dark mode toggle",
                    str(root),
                    "--slug",
                    "dark-mode-toggle",
                ]
            )
            self.assertEqual(first[0], 0, first[2])

            conflict = run_cli(
                [
                    "propose",
                    "add light mode toggle",
                    str(root),
                    "--slug",
                    "dark-mode-toggle",
                ]
            )
            self.assertEqual(conflict[0], 1)
            self.assertIn("already has existing files", conflict[2])

            forced = run_cli(
                [
                    "propose",
                    "add light mode toggle",
                    str(root),
                    "--slug",
                    "dark-mode-toggle",
                    "--force",
                ]
            )
            self.assertEqual(forced[0], 0, forced[2])
            spec = (root / "specs/features/dark-mode-toggle.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("add light mode toggle", spec)

    def test_dry_run_conflict_fails_without_force(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            first = run_cli(
                [
                    "propose",
                    "add dark mode toggle",
                    str(root),
                    "--slug",
                    "dark-mode-toggle",
                ]
            )
            self.assertEqual(first[0], 0, first[2])
            original_files = {
                relative_path: (root / relative_path).read_text(encoding="utf-8")
                for relative_path in (
                    "specs/features/dark-mode-toggle.md",
                    "execution/features/dark-mode-toggle.md",
                    "quality/features/dark-mode-toggle.md",
                )
            }

            conflict = run_cli(
                [
                    "propose",
                    "add light mode toggle",
                    str(root),
                    "--slug",
                    "dark-mode-toggle",
                    "--dry-run",
                ]
            )
            self.assertEqual(conflict[0], 1)
            self.assertIn("already has existing files", conflict[2])

            forced = run_cli(
                [
                    "propose",
                    "add light mode toggle",
                    str(root),
                    "--slug",
                    "dark-mode-toggle",
                    "--dry-run",
                    "--force",
                    "--json",
                ]
            )
            self.assertEqual(forced[0], 0, forced[2])
            payload = json.loads(forced[1])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["written_paths"], [])
            self.assertEqual(
                sorted(payload["existing_paths"]),
                [
                    "execution/features/dark-mode-toggle.md",
                    "quality/features/dark-mode-toggle.md",
                    "specs/features/dark-mode-toggle.md",
                ],
            )
            for relative_path, original_content in original_files.items():
                with self.subTest(relative_path=relative_path):
                    self.assertEqual(
                        (root / relative_path).read_text(encoding="utf-8"),
                        original_content,
                    )

    def test_long_intent_warning_surfaces_in_text_and_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            intent = "add " + ("searchable audit history " * 300)

            text_code, text_stdout, text_stderr = run_cli(
                [
                    "propose",
                    intent,
                    str(root),
                    "--slug",
                    "audit-history",
                    "--dry-run",
                ]
            )
            self.assertEqual(text_code, 0, text_stderr)
            self.assertIn("Warning: Proposal intent exceeded", text_stdout)
            self.assertNotIn(intent, text_stdout)

            json_code, json_stdout, json_stderr = run_cli(
                [
                    "propose",
                    intent,
                    str(root),
                    "--slug",
                    "audit-history",
                    "--json",
                ]
            )
            self.assertEqual(json_code, 0, json_stderr)
            payload = json.loads(json_stdout)
            self.assertEqual(len(payload["intent"]), MAX_INTENT_CHARS)
            self.assertEqual(len(payload["warnings"]), 1)
            self.assertIn("truncated", payload["warnings"][0])
            self.assertNotIn(intent, "\n".join(payload["files"].values()))

    def test_autoslug_and_generated_bundle_validate(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            code, stdout, stderr = run_cli(
                ["propose", "Add dark mode toggle!", str(root)]
            )

            self.assertEqual(code, 0, stderr)
            self.assertIn("add-dark-mode-toggle", stdout)
            report = build_validation_report(root, include_features=True)
            self.assertTrue(report["ok"], report["checks"])

    def test_autoslug_handles_unicode_and_special_characters_gracefully(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            code, stdout, stderr = run_cli(
                ["propose", "添加 暗色模式 ✨!!!", str(root), "--dry-run", "--json"]
            )

            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["slug"], "proposal")
            self.assertIn("specs/features/proposal.md", payload["files"])
            self.assertFalse((root / "specs/features/proposal.md").exists())

    def test_empty_and_punctuation_only_cli_return_code_2(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            for intent in ("", "   ", "?!"):
                with self.subTest(intent=intent):
                    code, _stdout, stderr = run_cli(["propose", intent, str(root)])
                    self.assertEqual(code, 2)
                    self.assertIn("Proposal intent", stderr)

    def test_complex_intent_decomposes_acceptance_tasks_and_quality(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            code, _stdout, stderr = run_cli(
                [
                    "propose",
                    "add dark mode toggle and user preferences with persistence",
                    str(root),
                    "--slug",
                    "dark-mode-toggle",
                ]
            )

            self.assertEqual(code, 0, stderr)
            spec = (root / "specs/features/dark-mode-toggle.md").read_text(
                encoding="utf-8"
            )
            execution = (root / "execution/features/dark-mode-toggle.md").read_text(
                encoding="utf-8"
            )
            quality = (root / "quality/features/dark-mode-toggle.md").read_text(
                encoding="utf-8"
            )
            acceptance = parse_acceptance_criteria(
                spec,
                source_file="specs/features/dark-mode-toggle.md",
            )
            checks = parse_quality_checks(
                quality,
                source_file="quality/features/dark-mode-toggle.md",
            )

            self.assertGreaterEqual(len(acceptance), 3)
            self.assertEqual(len(checks), len(acceptance))
            self.assertIn("user preferences", spec)
            self.assertGreaterEqual(execution.count("_Boundary:"), 3)
            self.assertGreaterEqual(execution.count("_Depends:"), 3)

    def test_generated_bundle_can_be_made_ready_with_real_coverage_links(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, _stdout, stderr = run_cli(
                [
                    "propose",
                    "add dark mode toggle",
                    str(root),
                    "--slug",
                    "dark-mode-toggle",
                ]
            )
            self.assertEqual(code, 0, stderr)

            test_target = root / "tests/test_propose_generated.py"
            test_target.parent.mkdir(parents=True)
            test_target.write_text("# generated coverage evidence\n", encoding="utf-8")

            for relative in (
                "specs/features/dark-mode-toggle.md",
                "execution/features/dark-mode-toggle.md",
                "quality/features/dark-mode-toggle.md",
            ):
                path = root / relative
                content = path.read_text(encoding="utf-8")
                content = content.replace("Status: proposed", "Status: validated")
                content = content.replace("- [ ]", "- [x]")
                content = content.replace(
                    "tests/test_dark_mode_toggle.py",
                    "tests/test_propose_generated.py",
                )
                path.write_text(content, encoding="utf-8")

            ready = build_feature_ready_report(
                root,
                "dark-mode-toggle",
                require_coverage=True,
            )
            self.assertTrue(ready.ready, ready.as_dict())
