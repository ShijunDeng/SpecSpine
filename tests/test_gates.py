import json
import os
import socket
import stat
import subprocess
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from specspine.cli import main
from specspine.gates import (
    build_quality_gate_report,
    parse_definition_of_done,
    parse_required_checks,
)
from specspine.validation import build_validation_report
from specspine.features import build_feature_ready_report
from specspine.workspace import init_workspace


REPO_ROOT = Path(__file__).resolve().parents[1]


class QualityGateTests(TestCase):
    def test_gates_json_parses_initialized_workspace_quality_checklist(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["gates", str(root), "--json"])

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["root"], str(root.resolve()))
            self.assertEqual(payload["source_file"], "quality/checklist.md")
            self.assertFalse(payload["source_missing"])
            self.assertEqual(payload["summary"]["required_total"], 5)
            self.assertEqual(payload["summary"]["required_done"], 0)
            self.assertEqual(payload["summary"]["required_open"], 5)
            self.assertEqual(payload["summary"]["definition_total"], 0)
            self.assertEqual(
                payload["summary"]["severity_counts"],
                {"critical": 0, "high": 0, "medium": 5, "low": 0},
            )
            self.assertEqual(payload["summary"]["owners_total"], 0)
            self.assertEqual(payload["summary"]["ci_checks_total"], 0)
            self.assertEqual(payload["required_checks"][0]["id"], "GATE001")
            self.assertEqual(payload["required_checks"][0]["line"], 5)
            self.assertFalse(payload["required_checks"][0]["done"])
            self.assertEqual(payload["required_checks"][0]["source_file"], "quality/checklist.md")
            self.assertEqual(payload["required_checks"][0]["severity"], "medium")
            self.assertEqual(payload["required_checks"][0]["owner"], "unassigned")
            self.assertIsNone(payload["required_checks"][0]["ci_check"])
            self.assertEqual(payload["required_checks"][0]["metadata"], {})
            self.assertEqual(payload["required_checks"][0]["metadata_warnings"], [])
            self.assertEqual(payload["definition_of_done"], [])
            self.assertIn(
                "specspine validate . --fusion --features",
                payload["recommended_commands"],
            )
            self.assertIn(
                "specspine status . --json --validate",
                payload["recommended_commands"],
            )

    def test_gates_json_counts_custom_gate_and_definition_shapes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            quality_dir = root / "quality"
            quality_dir.mkdir()
            (quality_dir / "checklist.md").write_text(
                "\n".join(
                    [
                        "# Quality Checklist",
                        "",
                        "## Required Checks",
                        "",
                        "- [ ] Dash open gate.",
                        "- [x] Dash done gate.",
                        "* [ ] Star open gate.",
                        "* [x] Star done gate.",
                        "",
                        "## Definition Of Done",
                        "",
                        "- Dash DOD item.",
                        "* Star DOD item.",
                    ]
                ),
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["gates", str(root), "--json"])

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["summary"]["definition_total"], 2)
            self.assertEqual(payload["summary"]["required_done"], 2)
            self.assertEqual(payload["summary"]["required_open"], 2)
            self.assertEqual(payload["summary"]["required_total"], 4)
            self.assertEqual(
                payload["summary"]["severity_counts"],
                {"critical": 0, "high": 0, "medium": 4, "low": 0},
            )
            self.assertEqual(
                [(gate["id"], gate["done"], gate["text"]) for gate in payload["required_checks"]],
                [
                    ("GATE001", False, "Dash open gate."),
                    ("GATE002", True, "Dash done gate."),
                    ("GATE003", False, "Star open gate."),
                    ("GATE004", True, "Star done gate."),
                ],
            )
            self.assertEqual(
                [(item["id"], item["text"]) for item in payload["definition_of_done"]],
                [
                    ("DOD001", "Dash DOD item."),
                    ("DOD002", "Star DOD item."),
                ],
            )

    def test_gates_text_includes_summary_and_ids(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["gates", str(root)])

            text = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("Source: quality/checklist.md", text)
            self.assertIn("Summary: required=5 done=0 open=5 definition=0", text)
            self.assertIn(
                "- [ ] GATE001 quality/checklist.md:5 Acceptance criteria are complete. "
                "(severity=medium owner=unassigned)",
                text,
            )
            self.assertIn("Definition Of Done:", text)

    def test_gates_text_includes_done_open_markers_and_definition_ids(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            quality_dir = root / "quality"
            quality_dir.mkdir()
            (quality_dir / "checklist.md").write_text(
                "\n".join(
                    [
                        "# Quality Checklist",
                        "",
                        "## Required Checks",
                        "",
                        "- [x] Shipping tests pass.",
                        "* [ ] Documentation is updated.",
                        "",
                        "## Definition Of Done",
                        "",
                        "- Reviewer approved.",
                        "* Release note published.",
                    ]
                ),
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["gates", str(root)])

            text = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("Source: quality/checklist.md", text)
            self.assertIn("Summary: required=2 done=1 open=1 definition=2", text)
            self.assertIn(
                "- [x] GATE001 quality/checklist.md:5 Shipping tests pass. "
                "(severity=medium owner=unassigned)",
                text,
            )
            self.assertIn(
                "- [ ] GATE002 quality/checklist.md:6 Documentation is updated. "
                "(severity=medium owner=unassigned)",
                text,
            )
            self.assertIn("- DOD001 quality/checklist.md:10 Reviewer approved.", text)
            self.assertIn("- DOD002 quality/checklist.md:11 Release note published.", text)

    def test_gates_parse_metadata_tags_case_insensitively_and_strip_text(self) -> None:
        content = "\n".join(
            [
                "# Quality Checklist",
                "",
                "## Required Checks",
                "",
                "- [x] Run unit tests. [SEVERITY: high] [Owner: qa] [ci: unit-tests]",
                "- [ ] Keep release notes current. [owner: docs] [Ci: docs-check] [severity: LOW]",
            ]
        )

        checks = parse_required_checks(content)

        self.assertEqual([check.text for check in checks], ["Run unit tests.", "Keep release notes current."])
        self.assertEqual([check.severity for check in checks], ["high", "low"])
        self.assertEqual([check.owner for check in checks], ["qa", "docs"])
        self.assertEqual([check.ci_check for check in checks], ["unit-tests", "docs-check"])
        self.assertEqual(checks[0].metadata, {"severity": "high", "owner": "qa", "ci": "unit-tests"})
        self.assertEqual(checks[0].raw_text, "Run unit tests. [SEVERITY: high] [Owner: qa] [ci: unit-tests]")

    def test_gates_metadata_order_values_and_duplicate_tags_are_stable(self) -> None:
        content = "\n".join(
            [
                "# Quality Checklist",
                "",
                "## Required Checks",
                "",
                "- [ ] [owner: platform quality] Deploy gate [ci: smoke-tests] [severity: high] passes.",
                "- [x] Release gate [ci: release candidate] [owner: release-manager] [severity: low] [owner: final owner] [ci: final-ci-check]",
                "- [ ] Escalation gate [severity: low] [severity: critical] [owner: qa-team]",
            ]
        )

        checks = parse_required_checks(content)

        self.assertEqual(
            [check.text for check in checks],
            [
                "Deploy gate passes.",
                "Release gate",
                "Escalation gate",
            ],
        )
        self.assertEqual([check.severity for check in checks], ["high", "low", "critical"])
        self.assertEqual(
            [check.owner for check in checks],
            ["platform quality", "final owner", "qa-team"],
        )
        self.assertEqual(
            [check.ci_check for check in checks],
            ["smoke-tests", "final-ci-check", None],
        )
        self.assertEqual(
            checks[1].metadata,
            {"ci": "final-ci-check", "owner": "final owner", "severity": "low"},
        )
        self.assertEqual(checks[2].metadata, {"severity": "critical", "owner": "qa-team"})

    def test_gates_unknown_metadata_key_is_preserved_as_text_not_metadata(self) -> None:
        content = "\n".join(
            [
                "# Quality Checklist",
                "",
                "## Required Checks",
                "",
                "- [ ] Audit trail [ticket: OPS-123] is linked. [owner: qa]",
            ]
        )

        checks = parse_required_checks(content)

        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0].text, "Audit trail [ticket: OPS-123] is linked.")
        self.assertEqual(checks[0].owner, "qa")
        self.assertEqual(checks[0].metadata, {"owner": "qa"})

    def test_gates_metadata_stripping_normalizes_surrounding_whitespace(self) -> None:
        content = "\n".join(
            [
                "# Quality Checklist",
                "",
                "## Required Checks",
                "",
                "- [ ] Prefix   [severity: high]   middle\t[owner: qa team]   suffix.   [ci: smoke suite]",
            ]
        )

        checks = parse_required_checks(content)

        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0].text, "Prefix middle suffix.")
        self.assertEqual(checks[0].severity, "high")
        self.assertEqual(checks[0].owner, "qa team")
        self.assertEqual(checks[0].ci_check, "smoke suite")

    def test_gates_invalid_severity_warns_and_keeps_medium(self) -> None:
        content = "\n".join(
            [
                "# Quality Checklist",
                "",
                "## Required Checks",
                "",
                "- [ ] Security review passes. [severity: blocker] [owner: security]",
            ]
        )

        checks = parse_required_checks(content)

        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0].text, "Security review passes.")
        self.assertEqual(checks[0].severity, "medium")
        self.assertEqual(checks[0].owner, "security")
        self.assertIn("unsupported severity: blocker", checks[0].metadata_warnings)

    def test_gates_summary_counts_metadata_coverage(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            quality_dir = root / "quality"
            quality_dir.mkdir()
            (quality_dir / "checklist.md").write_text(
                "\n".join(
                    [
                        "# Quality Checklist",
                        "",
                        "## Required Checks",
                        "",
                        "- [x] Critical gate. [severity: critical] [owner: qa] [ci: critical-check]",
                        "- [x] High gate. [severity: high] [owner: security]",
                        "- [ ] Default gate.",
                        "- [ ] Bad severity. [severity: urgent] [ci: urgent-check]",
                    ]
                ),
                encoding="utf-8",
            )

            report = build_quality_gate_report(root)

            self.assertEqual(
                report.summary["severity_counts"],
                {"critical": 1, "high": 1, "medium": 2, "low": 0},
            )
            self.assertEqual(report.summary["owners_total"], 2)
            self.assertEqual(report.summary["ci_checks_total"], 2)

    def test_gates_text_includes_explicit_metadata(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            quality_dir = root / "quality"
            quality_dir.mkdir()
            (quality_dir / "checklist.md").write_text(
                "\n".join(
                    [
                        "# Quality Checklist",
                        "",
                        "## Required Checks",
                        "",
                        "- [x] Run unit tests. [severity: high] [owner: qa] [ci: unit-tests]",
                    ]
                ),
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["gates", str(root)])

            self.assertEqual(exit_code, 0)
            self.assertIn(
                "- [x] GATE001 quality/checklist.md:5 Run unit tests. "
                "(severity=high owner=qa ci=unit-tests)",
                stdout.getvalue(),
            )

    def test_gates_source_missing_returns_one_with_empty_json_lists(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["gates", str(root), "--json"])

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 1)
            self.assertTrue(payload["source_missing"])
            self.assertEqual(payload["source_file"], "quality/checklist.md")
            self.assertEqual(payload["required_checks"], [])
            self.assertEqual(payload["definition_of_done"], [])
            self.assertEqual(payload["summary"]["definition_total"], 0)
            self.assertEqual(payload["summary"]["required_done"], 0)
            self.assertEqual(payload["summary"]["required_open"], 0)
            self.assertEqual(payload["summary"]["required_total"], 0)
            self.assertEqual(
                payload["summary"]["severity_counts"],
                {"critical": 0, "high": 0, "medium": 0, "low": 0},
            )
            self.assertEqual(payload["summary"]["owners_total"], 0)
            self.assertEqual(payload["summary"]["ci_checks_total"], 0)

    def test_gates_source_missing_text_is_clear(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["gates", str(root)])

            text = stdout.getvalue()
            self.assertEqual(exit_code, 1)
            self.assertIn("Source missing: yes", text)
            self.assertIn("None found because quality/checklist.md is missing", text)

    def test_gates_only_parse_required_checks_and_definition_of_done(self) -> None:
        content = "\n".join(
            [
                "# Quality Checklist",
                "",
                "## Required Checks",
                "",
                "- [x] Unit tests pass.",
                "* [ ] Documentation is updated.",
                "- Plain bullets here are ignored.",
                "",
                "## Other Section",
                "",
                "- [x] This checkbox is outside the required section.",
                "- This bullet is outside the definition section.",
                "",
                "## Definition Of Done",
                "",
                "- Release notes are ready.",
                "* [x] Deployment owner has approved.",
                "",
                "## Later Section",
                "",
                "- This bullet is outside both parsed sections.",
            ]
        )

        checks = parse_required_checks(content)
        definition = parse_definition_of_done(content)

        self.assertEqual([check.id for check in checks], ["GATE001", "GATE002"])
        self.assertEqual([check.text for check in checks], ["Unit tests pass.", "Documentation is updated."])
        self.assertEqual([check.done for check in checks], [True, False])
        self.assertEqual([item.id for item in definition], ["DOD001", "DOD002"])
        self.assertEqual(
            [item.text for item in definition],
            ["Release notes are ready.", "Deployment owner has approved."],
        )

    def test_gates_ignore_nested_same_named_headings(self) -> None:
        content = "\n".join(
            [
                "# Quality Checklist",
                "",
                "## Other Section",
                "",
                "### Required Checks",
                "",
                "- [x] Nested required checks must be ignored.",
                "",
                "### Definition Of Done",
                "",
                "- Nested Definition Of Done must be ignored.",
                "",
                "## Required Checks",
                "",
                "- [x] Top-level quality gate is parsed.",
                "",
                "## Definition Of Done",
                "",
                "- Top-level release rule is parsed.",
            ]
        )

        checks = parse_required_checks(content)
        definition = parse_definition_of_done(content)

        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0].id, "GATE001")
        self.assertEqual(checks[0].text, "Top-level quality gate is parsed.")
        self.assertEqual(len(definition), 1)
        self.assertEqual(definition[0].id, "DOD001")
        self.assertEqual(definition[0].text, "Top-level release rule is parsed.")

    def test_gates_reads_only_quality_checklist_and_skips_external_tools(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            token_file = root / "token.txt"
            token_file.write_text("not-a-real-token\n", encoding="utf-8")
            bin_dir = root / "bin"
            bin_dir.mkdir()
            sentinel = root / "gh-called"
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                f"#!/bin/sh\ntouch {sentinel}\nexit 99\n",
                encoding="utf-8",
            )
            gh_path.chmod(gh_path.stat().st_mode | stat.S_IXUSR)

            source_path = (root / "quality" / "checklist.md").resolve()
            original_read_text = Path.read_text
            read_paths: list[Path] = []

            def tracked_read_text(path: Path, *args: object, **kwargs: object) -> str:
                read_paths.append(path.resolve())
                if path.resolve() != source_path:
                    raise AssertionError(f"unexpected file read: {path}")
                return original_read_text(path, *args, **kwargs)

            stdout = StringIO()
            with (
                patch.object(Path, "read_text", autospec=True, side_effect=tracked_read_text),
                patch.object(subprocess, "run", side_effect=AssertionError("subprocess.run should not be called")),
                patch.object(subprocess, "Popen", side_effect=AssertionError("subprocess.Popen should not be called")),
                patch.object(subprocess, "check_call", side_effect=AssertionError("subprocess.check_call should not be called")),
                patch.object(subprocess, "check_output", side_effect=AssertionError("subprocess.check_output should not be called")),
                patch.object(socket, "create_connection", side_effect=AssertionError("network should not be called")),
                patch.object(os, "system", side_effect=AssertionError("os.system should not be called")),
                patch.dict(os.environ, {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}),
                redirect_stdout(stdout),
            ):
                exit_code = main(["gates", str(root), "--json"])

            self.assertEqual(exit_code, 0)
            self.assertEqual(read_paths, [source_path])
            self.assertFalse(sentinel.exists())
            token_prefix = "gh" + "p_"
            self.assertFalse(token_file.read_text(encoding="utf-8").startswith(token_prefix))

    def test_quality_gate_definitions_dogfood_bundle_passes_readiness_and_validation(self) -> None:
        report = build_quality_gate_report(REPO_ROOT)
        readiness = build_feature_ready_report(REPO_ROOT, "quality-gate-definitions")
        validation = build_validation_report(
            REPO_ROOT,
            include_fusion=True,
            include_features=True,
        )

        self.assertFalse(report.source_missing)
        self.assertGreaterEqual(report.summary["required_total"], 1)
        self.assertTrue(readiness.ready)
        self.assertEqual(readiness.status, "validated")
        self.assertEqual(validation["summary"]["fail"], 0)
