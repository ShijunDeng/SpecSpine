import json
import os
import re
import stat
from collections import defaultdict
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
    EARS_PATTERNS,
    generate_ears_criteria,
    generate_slug_from_intent,
    generate_tasks,
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


class IntentParsingEdgeCases(TestCase):
    def test_very_long_intent_is_truncated(self) -> None:
        intent = "add " + ("searchable audit history " * 300)
        self.assertGreater(len(intent), MAX_INTENT_CHARS)
        normalized, warnings = normalize_intent(intent)
        self.assertEqual(len(normalized), MAX_INTENT_CHARS)
        self.assertEqual(len(warnings), 1)
        self.assertIn("truncated", warnings[0])

    def test_intent_exactly_at_max_length(self) -> None:
        intent = "a" * MAX_INTENT_CHARS
        normalized, warnings = normalize_intent(intent)
        self.assertEqual(len(normalized), MAX_INTENT_CHARS)
        self.assertEqual(len(warnings), 0)

    def test_intent_one_char_over_max_length(self) -> None:
        intent = "a" * (MAX_INTENT_CHARS + 1)
        normalized, warnings = normalize_intent(intent)
        self.assertEqual(len(normalized), MAX_INTENT_CHARS)
        self.assertEqual(len(warnings), 1)

    def test_intent_with_double_quotes(self) -> None:
        parsed = parse_intent('add "user profile" toggle')
        self.assertEqual(parsed["action"], "add")
        self.assertEqual(parsed["target"], "toggle")

    def test_intent_with_single_quotes(self) -> None:
        parsed = parse_intent("add 'dark mode' button")
        self.assertEqual(parsed["action"], "add")
        self.assertEqual(parsed["target"], "button")

    def test_intent_with_brackets(self) -> None:
        parsed = parse_intent("create [advanced] settings panel")
        self.assertEqual(parsed["action"], "create")
        self.assertEqual(parsed["target"], "panel")

    def test_intent_with_unicode_characters(self) -> None:
        intent = "add dark mode toggle with \u00e9mojis and \u00fcnicode"
        normalized, warnings = normalize_intent(intent)
        self.assertIn("dark mode", normalized)
        self.assertEqual(len(warnings), 0)

    def test_intent_with_unicode_chinese(self) -> None:
        intent = "add dark mode toggle for \u4e2d\u6587 users"
        normalized, warnings = normalize_intent(intent)
        self.assertTrue(len(normalized) > 0)
        self.assertEqual(len(warnings), 0)

    def test_intent_with_special_chars_ampersand_at(self) -> None:
        intent = "add analytics @ dashboard & reporting"
        normalized, warnings = normalize_intent(intent)
        self.assertEqual(len(warnings), 0)

    def test_intent_with_multiple_action_verbs(self) -> None:
        parsed = parse_intent("add create and build a dashboard")
        self.assertIn(parsed["action"], ("add", "create", "build"))

    def test_intent_with_no_recognizable_action_verbs_uses_default(self) -> None:
        parsed = parse_intent("the thing about the widget")
        self.assertEqual(parsed["action"], "implement")

    def test_intent_pattern_implement_x_for_y(self) -> None:
        parsed = parse_intent("implement audit logging for admin panel")
        self.assertEqual(parsed["action"], "implement")
        self.assertEqual(parsed["target"], "panel")
        self.assertTrue(any("admin" in m for m in parsed["modifiers"]))

    def test_intent_pattern_build_x_that_does_y(self) -> None:
        parsed = parse_intent("build notification system that sends alerts")
        self.assertEqual(parsed["action"], "build")
        self.assertEqual(parsed["target"], "notification")

    def test_intent_pattern_create_x_with_y_and_z(self) -> None:
        parsed = parse_intent("create dashboard with charts and filters")
        self.assertEqual(parsed["action"], "create")
        self.assertEqual(parsed["target"], "dashboard")
        self.assertTrue(parsed["is_complex"])

    def test_intent_pattern_enable_x_when_y(self) -> None:
        parsed = parse_intent("enable dark mode when user prefers it")
        self.assertEqual(parsed["action"], "enable")
        self.assertEqual(parsed["target"], "mode")

    def test_intent_leading_whitespace_normalized(self) -> None:
        normalized, warnings = normalize_intent("   add dark mode toggle   ")
        self.assertEqual(normalized, "add dark mode toggle")
        self.assertEqual(len(warnings), 0)

    def test_intent_with_only_numbers_accepted(self) -> None:
        normalized, warnings = normalize_intent("12345")
        self.assertEqual(normalized, "12345")
        self.assertEqual(len(warnings), 0)

    def test_intent_with_numbers_and_words_accepted(self) -> None:
        normalized, _ = normalize_intent("add feature 2.0")
        self.assertEqual(normalized, "add feature 2.0")

    def test_intent_with_newlines_normalized(self) -> None:
        intent = "add dark mode\n toggle"
        normalized, warnings = normalize_intent(intent)
        self.assertIn("dark mode", normalized)

    def test_complex_intent_detected_via_and_splitter(self) -> None:
        parsed = parse_intent("add dark mode and light mode toggle")
        self.assertTrue(parsed["is_complex"])
        self.assertGreater(len(parsed["components"]), 1)

    def test_complex_intent_detected_via_with_splitter(self) -> None:
        parsed = parse_intent("add settings with notifications and alerts")
        self.assertTrue(parsed["is_complex"])

    def test_complex_intent_detected_via_semicolon(self) -> None:
        parsed = parse_intent("add dark mode; enable user preferences")
        self.assertTrue(parsed["is_complex"])

    def test_simple_intent_not_complex(self) -> None:
        parsed = parse_intent("add dark mode toggle")
        self.assertFalse(parsed["is_complex"])
        self.assertEqual(len(parsed["components"]), 1)

    def test_slug_generation_deterministic(self) -> None:
        slug1 = generate_slug_from_intent("Add dark mode toggle!")
        slug2 = generate_slug_from_intent("Add dark mode toggle!")
        self.assertEqual(slug1, slug2)

    def test_slug_no_uppercase(self) -> None:
        slug = generate_slug_from_intent("Add Dark Mode Toggle")
        self.assertEqual(slug, slug.lower())

    def test_slug_no_spaces(self) -> None:
        slug = generate_slug_from_intent("add dark mode toggle")
        self.assertNotIn(" ", slug)

    def test_slug_starts_with_alphanumeric(self) -> None:
        slug = generate_slug_from_intent("add dark mode toggle")
        self.assertTrue(slug[0].isalnum())


class EarsCriteriaQuality(TestCase):
    def test_all_criteria_follow_ears_format(self) -> None:
        parsed = parse_intent("add dark mode toggle with persistence")
        criteria = generate_ears_criteria(parsed)
        for criterion in criteria:
            self.assertIn("The system SHALL", criterion["text"])

    def test_criteria_have_valid_ids(self) -> None:
        parsed = parse_intent("add dark mode toggle")
        criteria = generate_ears_criteria(parsed)
        for criterion in criteria:
            self.assertTrue(re.match(r"^AC\d{3}$", criterion["id"]))

    def test_criteria_ids_sequential(self) -> None:
        parsed = parse_intent("add dark mode toggle")
        criteria = generate_ears_criteria(parsed)
        expected_ids = [f"AC{i+1:03d}" for i in range(len(criteria))]
        actual_ids = [c["id"] for c in criteria]
        self.assertEqual(actual_ids, expected_ids)

    def test_criteria_no_duplicates(self) -> None:
        parsed = parse_intent("add dark mode toggle with persistence")
        criteria = generate_ears_criteria(parsed)
        texts = [c["text"] for c in criteria]
        self.assertEqual(len(texts), len(set(texts)))

    def test_criteria_cover_different_patterns(self) -> None:
        parsed = parse_intent("add dark mode toggle for night viewing")
        criteria = generate_ears_criteria(parsed)
        patterns = {c["pattern"] for c in criteria}
        self.assertIn("event-driven", patterns)
        self.assertIn("simple", patterns)
        self.assertIn("conditional", patterns)
        self.assertIn("ubiquitous", patterns)

    def test_criteria_at_least_three_generated(self) -> None:
        parsed = parse_intent("add dark mode toggle")
        criteria = generate_ears_criteria(parsed)
        self.assertGreaterEqual(len(criteria), 3)

    def test_criteria_max_eight_generated(self) -> None:
        parsed = parse_intent("add dark mode and light mode and alert system and notification panel with persistence")
        criteria = generate_ears_criteria(parsed)
        self.assertLessEqual(len(criteria), 8)

    def test_complex_intent_produces_more_criteria_than_simple(self) -> None:
        simple = parse_intent("add dark mode toggle")
        complex_intent = parse_intent("add dark mode toggle and user preferences with persistence")
        simple_criteria = generate_ears_criteria(simple)
        complex_criteria = generate_ears_criteria(complex_intent)
        self.assertGreater(len(complex_criteria), len(simple_criteria))

    def test_criteria_testable_not_vague(self) -> None:
        parsed = parse_intent("add dark mode toggle")
        criteria = generate_ears_criteria(parsed)
        vague_terms = ["etc", "and so on", "maybe", "possibly", "might"]
        for criterion in criteria:
            text_lower = criterion["text"].lower()
            for term in vague_terms:
                self.assertNotIn(term, text_lower)

    def test_criteria_each_have_pattern_field(self) -> None:
        parsed = parse_intent("add dark mode toggle")
        criteria = generate_ears_criteria(parsed)
        valid_patterns = set(EARS_PATTERNS)
        for criterion in criteria:
            self.assertIn(criterion["pattern"], valid_patterns)

    def test_event_driven_criteria_has_when(self) -> None:
        parsed = parse_intent("add dark mode toggle")
        criteria = generate_ears_criteria(parsed)
        event_criteria = [c for c in criteria if c["pattern"] == "event-driven"]
        self.assertGreater(len(event_criteria), 0)
        self.assertTrue(any("when" in c["text"].lower() for c in event_criteria))

    def test_conditional_criteria_has_if(self) -> None:
        parsed = parse_intent("add dark mode toggle for night viewing")
        criteria = generate_ears_criteria(parsed)
        conditional_criteria = [c for c in criteria if c["pattern"] == "conditional"]
        self.assertGreater(len(conditional_criteria), 0)
        self.assertTrue(any("if" in c["text"].lower() for c in conditional_criteria))

    def test_ubiquitous_criteria_has_where(self) -> None:
        parsed = parse_intent("add dark mode toggle")
        criteria = generate_ears_criteria(parsed)
        ubiquitous_criteria = [c for c in criteria if c["pattern"] == "ubiquitous"]
        self.assertGreater(len(ubiquitous_criteria), 0)
        self.assertTrue(any("where" in c["text"].lower() for c in ubiquitous_criteria))


class TaskDecompositionQuality(TestCase):
    def test_tasks_have_valid_ids(self) -> None:
        parsed = parse_intent("add dark mode toggle")
        criteria = generate_ears_criteria(parsed)
        tasks = generate_tasks(parsed, criteria)
        for task in tasks:
            self.assertTrue(re.match(r"^T\d{3}$", task["id"]))

    def test_tasks_ids_sequential(self) -> None:
        parsed = parse_intent("add dark mode toggle")
        criteria = generate_ears_criteria(parsed)
        tasks = generate_tasks(parsed, criteria)
        expected_ids = [f"T{i+1:03d}" for i in range(len(tasks))]
        actual_ids = [t["id"] for t in tasks]
        self.assertEqual(actual_ids, expected_ids)

    def test_tasks_no_duplicates(self) -> None:
        parsed = parse_intent("add dark mode toggle")
        criteria = generate_ears_criteria(parsed)
        tasks = generate_tasks(parsed, criteria)
        texts = [t["text"] for t in tasks]
        self.assertEqual(len(texts), len(set(texts)))

    def test_tasks_valid_topological_ordering(self) -> None:
        parsed = parse_intent("add dark mode toggle")
        criteria = generate_ears_criteria(parsed)
        tasks = generate_tasks(parsed, criteria)
        task_ids = {t["id"] for t in tasks}
        seen = set()
        for task in tasks:
            deps = task["depends"]
            if deps != "none":
                dep_list = [d.strip() for d in deps.split(",")]
                for dep in dep_list:
                    self.assertIn(dep, task_ids)
                    self.assertIn(dep, seen)
            seen.add(task["id"])

    def test_tasks_no_circular_dependencies(self) -> None:
        parsed = parse_intent("add dark mode toggle")
        criteria = generate_ears_criteria(parsed)
        tasks = generate_tasks(parsed, criteria)
        adj = defaultdict(list)
        for task in tasks:
            if task["depends"] != "none":
                for dep in task["depends"].split(","):
                    adj[dep.strip()].append(task["id"])
        visited = set()
        rec_stack = set()

        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.discard(node)
            return False

        all_ids = {t["id"] for t in tasks}
        for tid in all_ids:
            if tid not in visited:
                self.assertFalse(has_cycle(tid))

    def test_tasks_reference_valid_boundaries(self) -> None:
        parsed = parse_intent("add dark mode toggle")
        criteria = generate_ears_criteria(parsed)
        tasks = generate_tasks(parsed, criteria)
        for task in tasks:
            self.assertTrue(len(task["boundary"]) > 0)
            self.assertIn(task["boundary"][0].upper(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    def test_complex_intent_produces_at_least_as_many_tasks(self) -> None:
        simple = parse_intent("add dark mode toggle")
        complex_intent = parse_intent("add dark mode toggle and user preferences with persistence")
        criteria_simple = generate_ears_criteria(simple)
        criteria_complex = generate_ears_criteria(complex_intent)
        tasks_simple = generate_tasks(simple, criteria_simple)
        tasks_complex = generate_tasks(complex_intent, criteria_complex)
        self.assertGreaterEqual(len(tasks_complex), len(tasks_simple))
        self.assertGreater(len(criteria_complex), len(criteria_simple))

    def test_first_task_has_no_dependencies(self) -> None:
        parsed = parse_intent("add dark mode toggle")
        criteria = generate_ears_criteria(parsed)
        tasks = generate_tasks(parsed, criteria)
        self.assertEqual(tasks[0]["depends"], "none")

    def test_each_task_is_actionable(self) -> None:
        parsed = parse_intent("add dark mode toggle")
        criteria = generate_ears_criteria(parsed)
        tasks = generate_tasks(parsed, criteria)
        action_verbs = {
            "set up", "implement", "wire", "add", "create", "build",
            "update", "verify", "test", "configure", "integrate",
        }
        for task in tasks:
            text_lower = task["text"].lower()
            has_action = any(verb in text_lower for verb in action_verbs)
            self.assertTrue(has_action, f"Task '{task['text']}' is not actionable")

    def test_tasks_reference_criteria_ids(self) -> None:
        parsed = parse_intent("add dark mode toggle")
        criteria = generate_ears_criteria(parsed)
        tasks = generate_tasks(parsed, criteria)
        criterion_ids = {c["id"] for c in criteria}
        for task in tasks:
            if "criterion" in task["text"].lower() or "AC" in task["text"]:
                found_id = False
                for cid in criterion_ids:
                    if cid in task["text"]:
                        found_id = True
                        break
                if "criterion" in task["text"].lower():
                    self.assertTrue(found_id)


class QualityChecksCompleteness(TestCase):
    def test_each_ac_has_corresponding_quality_check(self) -> None:
        parsed = parse_intent("add dark mode toggle")
        criteria = generate_ears_criteria(parsed)
        from specspine.proposer import generate_quality_checks
        checks = generate_quality_checks(criteria)
        self.assertEqual(len(checks), len(criteria))

    def test_quality_checks_reference_ac_ids(self) -> None:
        parsed = parse_intent("add dark mode toggle")
        criteria = generate_ears_criteria(parsed)
        from specspine.proposer import generate_quality_checks
        checks = generate_quality_checks(criteria)
        for criterion in criteria:
            found = any(criterion["id"] in check for check in checks)
            self.assertTrue(found, f"AC {criterion['id']} not referenced in quality checks")

    def test_edge_cases_present_in_spec(self) -> None:
        files = build_proposal_files("edge-case-test", "add dark mode toggle")
        spec = files["specs/features/edge-case-test.md"]
        self.assertIn("Edge Cases", spec)
        self.assertIn("Behavior when", spec)
        self.assertIn("concurrent", spec.lower())

    def test_validation_command_references_correct(self) -> None:
        files = build_proposal_files("validation-test", "add dark mode toggle")
        execution = files["execution/features/validation-test.md"]
        self.assertIn("specspine validate", execution)
        self.assertIn("specspine feature handoff validation-test", execution)

    def test_test_coverage_links_reference_slug(self) -> None:
        files = build_proposal_files("my-feature", "add dark mode toggle")
        quality = files["quality/features/my-feature.md"]
        self.assertIn("test_my_feature.py", quality)

    def test_quality_file_has_required_checks_section(self) -> None:
        files = build_proposal_files("qc-test", "add dark mode toggle")
        quality = files["quality/features/qc-test.md"]
        self.assertIn("Required Checks", quality)

    def test_quality_file_has_test_plan_section(self) -> None:
        files = build_proposal_files("tp-test", "add dark mode toggle")
        quality = files["quality/features/tp-test.md"]
        self.assertIn("Test Plan", quality)

    def test_quality_file_has_release_readiness_section(self) -> None:
        files = build_proposal_files("rr-test", "add dark mode toggle")
        quality = files["quality/features/rr-test.md"]
        self.assertIn("Release Readiness", quality)


class CLIIntegration(TestCase):
    def test_success_exit_code_zero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, _stdout, stderr = run_cli(
                ["propose", "add dark mode toggle", str(root), "--slug", "test-slug"]
            )
            self.assertEqual(code, 0, stderr)

    def test_conflict_exit_code_one(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            run_cli(["propose", "add dark mode toggle", str(root), "--slug", "test-slug"])
            code, _stdout, stderr = run_cli(
                ["propose", "add light mode toggle", str(root), "--slug", "test-slug"]
            )
            self.assertEqual(code, 1, stderr)

    def test_invalid_input_exit_code_two(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, _stdout, stderr = run_cli(["propose", "", str(root)])
            self.assertEqual(code, 2)
            self.assertIn("Proposal intent", stderr)

    def test_invalid_input_punctuation_exit_code_two(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, _stdout, stderr = run_cli(["propose", "?!", str(root)])
            self.assertEqual(code, 2)

    def test_success_stdout_contains_content_text_mode(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, stdout, stderr = run_cli(
                ["propose", "add dark mode toggle", str(root), "--slug", "test-slug"]
            )
            self.assertEqual(code, 0, stderr)
            self.assertIn("test-slug", stdout)

    def test_success_stderr_empty_on_success(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, _stdout, stderr = run_cli(
                ["propose", "add dark mode toggle", str(root), "--slug", "test-slug"]
            )
            self.assertEqual(code, 0)
            self.assertEqual(stderr.strip(), "")

    def test_conflict_stderr_has_message(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            run_cli(["propose", "add dark mode toggle", str(root), "--slug", "test-slug"])
            code, _stdout, stderr = run_cli(
                ["propose", "add light mode toggle", str(root), "--slug", "test-slug"]
            )
            self.assertEqual(code, 1)
            self.assertIn("already has existing files", stderr)

    def test_invalid_stderr_has_message(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, _stdout, stderr = run_cli(["propose", "", str(root)])
            self.assertEqual(code, 2)
            self.assertIn("Proposal intent", stderr)

    def test_file_permissions_after_creation(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            run_cli(["propose", "add dark mode toggle", str(root), "--slug", "test-slug"])
            for relative in [
                "specs/features/test-slug.md",
                "execution/features/test-slug.md",
                "quality/features/test-slug.md",
            ]:
                path = root / relative
                self.assertTrue(path.exists())
                mode = path.stat().st_mode
                self.assertTrue(mode & stat.S_IRUSR)
                self.assertTrue(mode & stat.S_IWUSR)

    def test_idempotent_with_force_produces_same_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            run_cli(["propose", "add dark mode toggle", str(root), "--slug", "test-slug"])
            code, stdout, stderr = run_cli(
                ["propose", "add dark mode toggle", str(root), "--slug", "test-slug", "--force", "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["slug"], "test-slug")

    def test_json_output_valid_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, stdout, stderr = run_cli(
                ["propose", "add dark mode toggle", str(root), "--slug", "test-slug", "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertIsInstance(payload, dict)

    def test_json_output_has_required_keys(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, stdout, _stderr = run_cli(
                ["propose", "add dark mode toggle", str(root), "--slug", "test-slug", "--json"]
            )
            payload = json.loads(stdout)
            required_keys = {"slug", "dry_run", "intent", "files", "warnings", "written_paths"}
            for key in required_keys:
                self.assertIn(key, payload)

    def test_dry_run_does_not_write_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            run_cli(
                ["propose", "add dark mode toggle", str(root), "--slug", "test-slug", "--dry-run"]
            )
            self.assertFalse((root / "specs/features/test-slug.md").exists())
            self.assertFalse((root / "execution/features/test-slug.md").exists())
            self.assertFalse((root / "quality/features/test-slug.md").exists())

    def test_written_paths_match_actual_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, stdout, _stderr = run_cli(
                ["propose", "add dark mode toggle", str(root), "--slug", "test-slug", "--json"]
            )
            payload = json.loads(stdout)
            for written_path in payload["written_paths"]:
                self.assertTrue((root / written_path).exists())

    def test_force_overwrites_content(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            run_cli(["propose", "add dark mode toggle", str(root), "--slug", "test-slug"])
            spec1 = (root / "specs/features/test-slug.md").read_text(encoding="utf-8")

            run_cli(["propose", "add light mode toggle", str(root), "--slug", "test-slug", "--force"])
            spec2 = (root / "specs/features/test-slug.md").read_text(encoding="utf-8")

            self.assertIn("dark mode", spec1)
            self.assertIn("light mode", spec2)

    def test_metadata_in_json_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, stdout, _stderr = run_cli(
                [
                    "propose", "add dark mode toggle", str(root), "--slug", "test-slug", "--json",
                    "--priority", "high", "--owner", "team-x", "--effort", "M",
                ]
            )
            payload = json.loads(stdout)
            self.assertEqual(payload["metadata"]["priority"], "high")
            self.assertEqual(payload["metadata"]["owner"], "team-x")
            self.assertEqual(payload["metadata"]["effort"], "M")

    def test_long_intent_warning_in_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            intent = "add " + ("searchable audit history " * 300)
            code, stdout, _stderr = run_cli(
                ["propose", intent, str(root), "--slug", "audit-test", "--json"]
            )
            payload = json.loads(stdout)
            self.assertEqual(code, 0)
            self.assertGreater(len(payload["warnings"]), 0)
            self.assertIn("truncated", payload["warnings"][0])


class EndToEndWorkflows(TestCase):
    def test_propose_to_ready_cycle(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            code, _stdout, stderr = run_cli(
                ["propose", "add dark mode toggle", str(root), "--slug", "cycle-test"]
            )
            self.assertEqual(code, 0, stderr)

            code2, stdout2, stderr2 = run_cli(
                ["feature", "status", "cycle-test", str(root), "--json"]
            )
            self.assertEqual(code2, 0, stderr2)
            status_payload = json.loads(stdout2)
            self.assertEqual(status_payload["feature_id"], "cycle-test")

    def test_propose_with_custom_metadata(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            code, _stdout, stderr = run_cli(
                [
                    "propose", "add dark mode toggle", str(root), "--slug", "meta-test",
                    "--priority", "high", "--owner", "team-x", "--effort", "M",
                    "--milestone", "Beta", "--target-release", "0.3.0",
                    "--project", "Native feature bundles",
                ]
            )
            self.assertEqual(code, 0, stderr)

            spec = (root / "specs/features/meta-test.md").read_text(encoding="utf-8")
            self.assertIn("Priority: high", spec)
            self.assertIn("Owner: team-x", spec)
            self.assertIn("Effort: M", spec)
            self.assertIn("Milestone: Beta", spec)
            self.assertIn("Target Release: 0.3.0", spec)
            self.assertIn("Project: Native feature bundles", spec)

    def test_propose_then_validate_features_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            run_cli(["propose", "add dark mode toggle", str(root), "--slug", "validate-test"])

            report = build_validation_report(root, include_features=True)
            self.assertTrue(report["ok"], report["checks"])

    def test_propose_creates_three_peer_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            run_cli(["propose", "add dark mode toggle", str(root), "--slug", "peer-test"])

            self.assertTrue((root / "specs/features/peer-test.md").exists())
            self.assertTrue((root / "execution/features/peer-test.md").exists())
            self.assertTrue((root / "quality/features/peer-test.md").exists())

    def test_propose_trace_references_all_sections(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            run_cli(["propose", "add dark mode toggle", str(root), "--slug", "trace-test"])

            code, stdout, stderr = run_cli(
                ["feature", "trace", "trace-test", str(root), "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertIn("acceptance_criteria", payload)
            self.assertIn("tasks", payload)
            self.assertIn("quality_checks", payload)

    def test_propose_feature_status_shows_proposed(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            run_cli(["propose", "add dark mode toggle", str(root), "--slug", "status-test"])

            code, stdout, stderr = run_cli(
                ["feature", "status", "status-test", str(root), "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["status"], "proposed")

    def test_propose_autoslug_validates(self) -> None:
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

    def test_propose_multiple_features_workspace_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            run_cli(["propose", "add dark mode toggle", str(root), "--slug", "feature-a"])
            run_cli(["propose", "add light mode toggle", str(root), "--slug", "feature-b"])

            code, stdout, stderr = run_cli(
                ["status", str(root), "--json", "--validate"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            slugs = [f["slug"] for f in payload.get("features", [])]
            self.assertIn("feature-a", slugs)
            self.assertIn("feature-b", slugs)

    def test_propose_and_feature_ready_not_ready_before_implementation(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            run_cli(["propose", "add dark mode toggle", str(root), "--slug", "ready-test"])

            ready = build_feature_ready_report(root, "ready-test")
            self.assertFalse(ready.ready)

    def test_propose_idempotent_force_same_structure(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            run_cli(["propose", "add dark mode toggle", str(root), "--slug", "idempotent-test"])
            files1 = {
                f.relative_to(root): f.read_text(encoding="utf-8")
                for f in root.rglob("*.md")
            }

            run_cli(["propose", "add dark mode toggle", str(root), "--slug", "idempotent-test", "--force"])
            files2 = {
                f.relative_to(root): f.read_text(encoding="utf-8")
                for f in root.rglob("*.md")
            }

            self.assertEqual(set(files1.keys()), set(files2.keys()))

    def test_propose_deterministic_same_intent_same_output(self) -> None:
        parsed1 = parse_intent("add dark mode toggle")
        criteria1 = generate_ears_criteria(parsed1)
        tasks1 = generate_tasks(parsed1, criteria1)

        parsed2 = parse_intent("add dark mode toggle")
        criteria2 = generate_ears_criteria(parsed2)
        tasks2 = generate_tasks(parsed2, criteria2)

        self.assertEqual([c["text"] for c in criteria1], [c["text"] for c in criteria2])
        self.assertEqual([t["text"] for t in tasks1], [t["text"] for t in tasks2])

    def test_propose_quality_parseable_from_disk(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            run_cli(["propose", "add dark mode toggle", str(root), "--slug", "quality-disk-test"])

            quality = (root / "quality/features/quality-disk-test.md").read_text(encoding="utf-8")
            checks = parse_quality_checks(quality, source_file="quality/features/quality-disk-test.md")
            self.assertGreater(len(checks), 0)

            coverage = parse_test_coverage(
                quality, source_file="quality/features/quality-disk-test.md", root=root
            )
            self.assertGreater(len(coverage), 0)

    def test_propose_spec_parseable_from_disk(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            run_cli(["propose", "add dark mode toggle", str(root), "--slug", "spec-disk-test"])

            spec = (root / "specs/features/spec-disk-test.md").read_text(encoding="utf-8")
            criteria = parse_acceptance_criteria(spec, source_file="specs/features/spec-disk-test.md")
            self.assertGreaterEqual(len(criteria), 3)

    def test_propose_execution_parseable_from_disk(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            run_cli(["propose", "add dark mode toggle", str(root), "--slug", "exec-disk-test"])

            execution = (root / "execution/features/exec-disk-test.md").read_text(encoding="utf-8")
            tasks = parse_feature_tasks(execution, source_file="execution/features/exec-disk-test.md")
            self.assertGreaterEqual(len(tasks), 3)

    def test_propose_coverage_debt_shows_new_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            run_cli(["propose", "add dark mode toggle", str(root), "--slug", "debt-test"])

            from specspine.coverage import build_coverage_debt_report
            debt = build_coverage_debt_report(root)
            slugs_with_debt = [d["feature_id"] for d in debt["features"]]
            self.assertIn("debt-test", slugs_with_debt)

    def test_propose_dry_run_json_has_files_key(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            code, stdout, stderr = run_cli(
                ["propose", "add dark mode toggle", str(root), "--slug", "dry-json-test", "--dry-run", "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertIn("files", payload)
            self.assertGreater(len(payload["files"]), 0)
            self.assertTrue(payload["dry_run"])
