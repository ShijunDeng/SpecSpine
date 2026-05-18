from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from specspine.agents import AgentsFileExistsError, build_agents_file, init_agents_file
from specspine.cli import main


class AgentsTests(TestCase):
    def test_init_agents_file_creates_agents_md(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            written = init_agents_file(root)

            self.assertEqual(written, root / "AGENTS.md")
            content = written.read_text(encoding="utf-8")
            self.assertIn("# AGENTS.md", content)
            self.assertIn("spec-driven AI development hub", content)
            self.assertIn("why / what / how", content)
            self.assertIn("`specs/`", content)
            self.assertIn("`execution/`", content)
            self.assertIn("`quality/`", content)
            self.assertIn("`integrations/`", content)
            self.assertIn("`docs/`", content)

    def test_init_agents_file_creates_missing_target_directory(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "missing" / "project"

            written = init_agents_file(root)

            self.assertEqual(written, root / "AGENTS.md")
            self.assertTrue(written.exists())
            self.assertIn("# AGENTS.md", written.read_text(encoding="utf-8"))

    def test_agents_content_includes_required_commands_and_boundaries(self) -> None:
        content = build_agents_file()

        for expected in (
            "specspine status . --json",
            "specspine status . --json --validate --validation-warnings",
            "specspine status . --json --validate --feature-summaries",
            "specspine status . --json --validate --feature-summaries --feature-status validated --feature-ready yes --feature-sort slug",
            "specspine status . --json --validate --feature-summaries --feature-require-coverage --feature-ready yes --feature-sort priority",
            "specspine status . --json --readiness-summary",
            "specspine status . --json --readiness-summary --readiness-policy",
            "specspine coverage debt . --json",
            "specspine coverage debt . --json --policy",
            "specspine coverage plan . --json",
            "specspine coverage plan . --feature <slug> --limit 3 --json",
            "specspine tests impact . --json",
            "specspine tests impact . --feature <slug> --json",
            "specspine consistency scan . --json",
            "specspine consistency scan . --feature <slug> --json",
            "specspine hygiene scan . --json",
            "specspine hygiene scan . --strict --json",
            "specspine retrospective report . --json",
            "specspine retrospective report . --feature <slug> --limit 3 --json",
            "specspine verify matrix <slug> . --json",
            "specspine change risk . --json",
            "specspine change risk . --feature <slug> --json",
            "specspine security cues . --json",
            "specspine security cues . --feature <slug> --json",
            "specspine provenance manifest . --json",
            "specspine provenance manifest . --feature <slug> --json",
            "specspine review packet . --json",
            "specspine review packet . --feature <slug> --json",
            "specspine loop packet . --json",
            "specspine gates . --json",
            "specspine adapters lifecycle . --json",
            "specspine validate .",
            "specspine validate . --features",
            "specspine validate . --fusion --features",
            'specspine propose "..." . --slug <slug> --dry-run',
            'specspine propose "..." . --slug <slug> --json',
            'specspine feature new <slug> . --title "..." --why "..."',
            "specspine feature status <slug> . --json",
            "specspine feature status <slug> . --set planned --enforce-transition --json",
            "specspine feature handoff <slug> . --json",
            "specspine feature trace <slug> . --json",
            "specspine feature ready <slug> . --json",
            "specspine feature tasks <slug> . --json",
            "specspine feature task-issues <slug> . --json",
            "specspine feature tests <slug> . --json",
            "specspine feature issue <slug> . --json",
            "specspine feature pr <slug> . --json",
            "PYTHONPATH=src python3 -m unittest discover -s tests",
            "Do not vendor upstream code.",
            "do not read or write GitHub tokens",
            "do not call the GitHub API",
            "prefer `--enforce-transition` when advancing lifecycle state",
            "Before archiving, run `specspine feature ready <slug> . --json`",
            "specspine feature status <slug> . --set archived --enforce-transition",
            "focused handoff, task issue drafts, tests, PR, readiness, and validation guidance",
            "start with `specspine propose",
            "preview the deterministic native bundle",
            "repository-level quality gate definitions",
            "adapter lifecycle definitions",
            "exact feature and AC coverage gaps",
            "read-only reviewer or agent remediation steps",
            "local source-to-test impact recommendations",
            "local spec-code-test-doc drift",
            "repository hygiene evidence",
            "Do not treat coverage plan recommended commands as executed commands or proof that tests ran.",
            "feature delivery themes",
            "Do not treat retrospective recommended commands as executed commands.",
            "generated cache artifacts",
            "AC-level verification evidence",
            "proof that tests ran",
            "changed paths by source, tests, feature peers, docs, or config",
            "security-sensitive keywords",
            "without proving vulnerabilities",
            "hash local evidence files",
            "without reading file contents into the report",
            "local pre-merge review evidence",
            "local, deterministic agent loop packet",
            "Recommended commands are advisory and are not executed.",
            "Do not treat loop packet recommended commands as executed commands.",
            "Use `--run-upstream` only when the user explicitly asks",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, content)

    def test_agents_content_is_ascii_and_has_no_external_dependency_links(self) -> None:
        content = build_agents_file()

        content.encode("ascii")
        self.assertNotIn("http://", content)
        self.assertNotIn("https://", content)

    def test_init_agents_file_refuses_to_overwrite_without_force(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents = root / "AGENTS.md"
            agents.write_text("custom instructions\n", encoding="utf-8")

            with self.assertRaises(AgentsFileExistsError):
                init_agents_file(root)

            self.assertEqual(agents.read_text(encoding="utf-8"), "custom instructions\n")

    def test_init_agents_file_force_overwrites(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents = root / "AGENTS.md"
            agents.write_text("custom instructions\n", encoding="utf-8")

            written = init_agents_file(root, force=True)

            self.assertEqual(written, agents)
            self.assertEqual(agents.read_text(encoding="utf-8"), build_agents_file())

    def test_agents_init_cli_default_path_creates_file_in_current_directory(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            previous_cwd = Path.cwd()
            stdout = StringIO()
            stderr = StringIO()
            try:
                os.chdir(root)

                with redirect_stdout(stdout), redirect_stderr(stderr):
                    returncode = main(["agents", "init"])
            finally:
                os.chdir(previous_cwd)

            self.assertEqual(returncode, 0)
            self.assertTrue((root / "AGENTS.md").exists())
            self.assertIn("Initialized SpecSpine agent instructions", stdout.getvalue())
            self.assertIn("created AGENTS.md", stdout.getvalue())
            self.assertEqual(stderr.getvalue(), "")

    def test_agents_init_cli_creates_file_and_returns_zero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                returncode = main(["agents", "init", str(root)])

            self.assertEqual(returncode, 0)
            self.assertTrue((root / "AGENTS.md").exists())
            self.assertIn("Initialized SpecSpine agent instructions", stdout.getvalue())
            self.assertIn("created AGENTS.md", stdout.getvalue())
            self.assertEqual(stderr.getvalue(), "")

    def test_agents_init_cli_rejects_existing_file_with_nonzero_return_code(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents = root / "AGENTS.md"
            agents.write_text("custom instructions\n", encoding="utf-8")
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                returncode = main(["agents", "init", str(root)])

            self.assertEqual(returncode, 1)
            self.assertEqual(agents.read_text(encoding="utf-8"), "custom instructions\n")
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("AGENTS.md already exists", stderr.getvalue())
            self.assertIn("Use --force", stderr.getvalue())

    def test_agents_init_cli_force_overwrites_existing_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents = root / "AGENTS.md"
            agents.write_text("custom instructions\n", encoding="utf-8")
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                returncode = main(["agents", "init", str(root), "--force"])

            self.assertEqual(returncode, 0)
            self.assertEqual(agents.read_text(encoding="utf-8"), build_agents_file())
            self.assertIn("created AGENTS.md", stdout.getvalue())
            self.assertEqual(stderr.getvalue(), "")
