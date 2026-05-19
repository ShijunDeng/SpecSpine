import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from specspine.blueprint import (
    BlueprintDataEntity,
    BlueprintErrorPath,
    BlueprintFunction,
    BlueprintModule,
    BlueprintReport,
    _collect_all_ac_items,
    _compute_coverage_summary,
    _derive_error_paths,
    _derive_module_structure,
    _derive_safety_notes,
    _extract_ac_ids,
    _extract_behavioral_domains,
    _extract_behavioral_verb,
    _extract_target_noun,
    _generate_function_signatures,
    _identify_data_entities,
    build_spec_code_blueprint,
    render_blueprint_json,
    render_blueprint_text,
)
from specspine.cli import main
from specspine.features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    create_feature_bundle,
)


def _write_feature_with_ac(
    root: Path,
    slug: str,
    ac_lines: list[str],
    status: str = "planned",
    title: str = "Test Feature",
) -> None:
    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)
    ac_block = "\n".join(f"- [ ] {line}" for line in ac_lines)
    (root / "specs" / "features" / f"{slug}.md").write_text(
        f"# {title}\n\nFeature ID: {slug}\nStatus: {status}\n\n"
        f"## Acceptance Criteria\n\n{ac_block}\n",
        encoding="utf-8",
    )
    (root / "execution" / "features" / f"{slug}.md").write_text(
        f"# Test Feature Execution\n\nFeature ID: {slug}\nStatus: {status}\n\n"
        f"## Tasks\n\n- [ ] Do something.\n",
        encoding="utf-8",
    )
    (root / "quality" / "features" / f"{slug}.md").write_text(
        f"# Test Feature Quality\n\nFeature ID: {slug}\nStatus: {status}\n\n"
        f"## Required Checks\n\n- [ ] Check something.\n\n"
        f"## Test Coverage\n\n\n## Test Plan\n\n- Run tests.\n",
        encoding="utf-8",
    )


class TestExtractAcIds(TestCase):
    def test_single_ac(self) -> None:
        self.assertEqual(_extract_ac_ids("AC001 The system SHALL do something"), ("AC001",))

    def test_multiple_acs(self) -> None:
        result = _extract_ac_ids("AC001 and AC002 are related")
        self.assertEqual(result, ("AC001", "AC002"))

    def test_no_ac(self) -> None:
        self.assertEqual(_extract_ac_ids("No ac here"), ())

    def test_lowercase_ac(self) -> None:
        result = _extract_ac_ids("ac001 text")
        self.assertEqual(result, ("AC001",))

    def test_ac_with_more_digits(self) -> None:
        result = _extract_ac_ids("AC0012 text")
        self.assertEqual(result, ("AC0012",))


class TestExtractBehavioralVerb(TestCase):
    def test_finds_add(self) -> None:
        self.assertEqual(_extract_behavioral_verb("The system SHALL add a new item"), "add")

    def test_finds_validate(self) -> None:
        self.assertEqual(_extract_behavioral_verb("SHALL validate input"), "validate")

    def test_no_verb_found(self) -> None:
        self.assertIsNone(_extract_behavioral_verb("The system is nice"))

    def test_finds_handle(self) -> None:
        self.assertEqual(_extract_behavioral_verb("SHALL handle errors gracefully"), "handle")


class TestExtractTargetNoun(TestCase):
    def test_finds_toggle(self) -> None:
        self.assertEqual(_extract_target_noun("add a dark toggle"), "toggle")

    def test_finds_mode(self) -> None:
        self.assertEqual(_extract_target_noun("enable dark mode"), "mode")

    def test_finds_user(self) -> None:
        self.assertEqual(_extract_target_noun("create a user for the system"), "user")

    def test_defaults_to_component(self) -> None:
        self.assertEqual(_extract_target_noun("do something weird"), "component")


class TestExtractBehavioralDomains(TestCase):
    def test_groups_by_verb_and_target(self) -> None:
        spec = (
            "# Test\n\nFeature ID: test-feature\nStatus: planned\n\n"
            "## Acceptance Criteria\n\n"
            "- [ ] AC001 The system SHALL add a new user profile\n"
            "- [ ] AC002 The system SHALL add another user profile\n"
            "- [ ] AC003 The system SHALL validate the input data\n"
        )
        domains = _extract_behavioral_domains(spec, "test-feature")
        self.assertIn("add_profile", domains)
        self.assertIn("validate_input", domains)
        self.assertEqual(len(domains["add_profile"]), 2)

    def test_empty_spec(self) -> None:
        spec = "# Test\n\nFeature ID: test\nStatus: planned\n\n## Acceptance Criteria\n\n"
        domains = _extract_behavioral_domains(spec, "test")
        self.assertEqual(domains, {})

    def test_single_domain(self) -> None:
        spec = (
            "# Test\n\nFeature ID: test-feature\nStatus: planned\n\n"
            "## Acceptance Criteria\n\n"
            "- [ ] AC001 The system SHALL create a new document\n"
        )
        domains = _extract_behavioral_domains(spec, "test-feature")
        self.assertEqual(len(domains), 1)
        self.assertIn("create_document", domains)


class TestDeriveModuleStructure(TestCase):
    def test_derives_modules_from_domains(self) -> None:
        domains = {
            "add_user": [{"text": "add a new user", "full_text": "AC001 SHAL...", "verb": "add", "target": "user"}],
            "validate_input": [{"text": "validate the input", "full_text": "AC002 SHALL...", "verb": "validate", "target": "input"}],
        }
        modules = _derive_module_structure(domains, "test-feature")
        self.assertEqual(len(modules), 2)
        paths = [m.module_path for m in modules]
        self.assertIn("src/user.py", paths)
        self.assertIn("src/input.py", paths)

    def test_modules_have_ac_ids(self) -> None:
        domains = {
            "create_config": [{"text": "create config", "full_text": "AC003 The system SHALL...", "verb": "create", "target": "config"}],
        }
        modules = _derive_module_structure(domains, "test-feature")
        self.assertEqual(modules[0].ac_ids, ("AC003",))

    def test_empty_domains(self) -> None:
        modules = _derive_module_structure({}, "test-feature")
        self.assertEqual(modules, [])


class TestGenerateFunctionSignatures(TestCase):
    def test_generates_function_from_ac(self) -> None:
        ac_list = [
            {"text": "add a new user profile", "full_text": "AC001 SHALL...", "verb": "add", "target": "profile"},
        ]
        funcs = _generate_function_signatures(ac_list, "test-feature")
        self.assertEqual(len(funcs), 1)
        self.assertEqual(funcs[0].name, "add_profile")

    def test_function_has_ac_ids(self) -> None:
        ac_list = [
            {"text": "validate input", "full_text": "AC005 The system SHALL...", "verb": "validate", "target": "input"},
        ]
        funcs = _generate_function_signatures(ac_list, "test-feature")
        self.assertEqual(funcs[0].ac_ids, ("AC005",))

    def test_function_parameters_from_text(self) -> None:
        ac_list = [
            {"text": "add a record for the user", "full_text": "AC001 SHALL...", "verb": "add", "target": "record"},
        ]
        funcs = _generate_function_signatures(ac_list, "test-feature")
        self.assertTrue(len(funcs[0].parameters) > 0)

    def test_return_type_for_list(self) -> None:
        ac_list = [
            {"text": "list all items in the collection", "full_text": "AC001 SHALL...", "verb": "list", "target": "items"},
        ]
        funcs = _generate_function_signatures(ac_list, "test-feature")
        self.assertIn("list[", funcs[0].return_type.lower())

    def test_multiple_functions(self) -> None:
        ac_list = [
            {"text": "add a new user", "full_text": "AC001 SHALL...", "verb": "add", "target": "user"},
            {"text": "delete the user", "full_text": "AC002 SHALL...", "verb": "delete", "target": "user"},
        ]
        funcs = _generate_function_signatures(ac_list, "test-feature")
        self.assertEqual(len(funcs), 2)


class TestIdentifyDataEntities(TestCase):
    def test_identifies_entity_from_indicator(self) -> None:
        ac_list = [
            {"text": "add a new user record", "full_text": "AC001 The system SHALL add a new user record with name and email", "verb": "add", "target": "user"},
        ]
        entities = _identify_data_entities(ac_list, "test-feature")
        self.assertTrue(len(entities) > 0)
        names = [e.name for e in entities]
        self.assertIn("user", names)

    def test_entity_has_attributes(self) -> None:
        ac_list = [
            {"text": "create config entity", "full_text": "AC001 The system SHALL create config entity with name and value", "verb": "create", "target": "config"},
        ]
        entities = _identify_data_entities(ac_list, "test-feature")
        if entities:
            for entity in entities:
                if entity.name == "config":
                    self.assertTrue(len(entity.attributes) > 0)

    def test_empty_ac_list(self) -> None:
        entities = _identify_data_entities([], "test-feature")
        self.assertEqual(entities, [])

    def test_entity_ac_ids(self) -> None:
        ac_list = [
            {"text": "store data entity", "full_text": "AC007 The system SHALL store data entity with fields", "verb": "store", "target": "data"},
        ]
        entities = _identify_data_entities(ac_list, "test-feature")
        for entity in entities:
            if "AC007" in entity.ac_ids:
                self.assertIn("AC007", entity.ac_ids)


class TestDeriveErrorPaths(TestCase):
    def test_detects_error_condition(self) -> None:
        ac_list = [
            {"text": "handle the error when operation fails", "full_text": "AC001 The system SHALL handle the error when operation fails", "verb": "handle", "target": "error"},
        ]
        paths = _derive_error_paths(ac_list, "test-feature")
        self.assertTrue(len(paths) > 0)

    def test_detects_missing_condition(self) -> None:
        ac_list = [
            {"text": "reject when input is missing", "full_text": "AC002 The system SHALL reject when input is missing", "verb": "reject", "target": "input"},
        ]
        paths = _derive_error_paths(ac_list, "test-feature")
        if paths:
            self.assertEqual(paths[0].exception_type, "FileNotFoundError")

    def test_detects_timeout_condition(self) -> None:
        ac_list = [
            {"text": "fail when connection times out or is unavailable", "full_text": "AC003 The system SHALL fail when connection times out or is unavailable", "verb": "fail", "target": "connection"},
        ]
        paths = _derive_error_paths(ac_list, "test-feature")
        if paths:
            self.assertEqual(paths[0].exception_type, "TimeoutError")

    def test_no_error_indicators(self) -> None:
        ac_list = [
            {"text": "add a new item", "full_text": "AC001 The system SHALL add a new item", "verb": "add", "target": "item"},
        ]
        paths = _derive_error_paths(ac_list, "test-feature")
        self.assertEqual(paths, [])

    def test_error_path_has_ac_ids(self) -> None:
        ac_list = [
            {"text": "handle the error gracefully", "full_text": "AC005 The system SHALL handle the error gracefully", "verb": "handle", "target": "error"},
        ]
        paths = _derive_error_paths(ac_list, "test-feature")
        if paths:
            self.assertIn("AC005", paths[0].ac_ids)

    def test_invalid_condition(self) -> None:
        ac_list = [
            {"text": "reject invalid input", "full_text": "AC004 The system SHALL reject invalid input", "verb": "reject", "target": "input"},
        ]
        paths = _derive_error_paths(ac_list, "test-feature")
        if paths:
            self.assertEqual(paths[0].exception_type, "ValueError")


class TestComputeCoverageSummary(TestCase):
    def test_summary_counts(self) -> None:
        modules = [
            BlueprintModule("src/user.py", "Manage users", (), ("AC001",)),
        ]
        functions = [
            BlueprintFunction("add_user", ("name",), "bool", "Add user", ("AC001", "AC002")),
        ]
        entities = [
            BlueprintDataEntity("user", ("name", "email"), "User entity", ("AC001",)),
        ]
        error_paths = [
            BlueprintErrorPath("missing input", "ValueError", "Log", ("AC002",)),
        ]
        summary = _compute_coverage_summary(modules, functions, entities, error_paths)
        self.assertEqual(summary["modules_total"], 1)
        self.assertEqual(summary["functions_total"], 1)
        self.assertEqual(summary["data_entities_total"], 1)
        self.assertEqual(summary["error_paths_total"], 1)
        self.assertEqual(summary["unique_ac_covered"], 2)


class TestDeriveSafetyNotes(TestCase):
    def test_no_validation_warning(self) -> None:
        funcs = [BlueprintFunction("add_user", ("name",), "bool", "Add", ())]
        notes = _derive_safety_notes(funcs, [])
        self.assertTrue(any("validation" in n.lower() for n in notes))

    def test_no_error_handling_warning(self) -> None:
        funcs = [BlueprintFunction("validate_input", ("data",), "bool", "Validate", ())]
        notes = _derive_safety_notes(funcs, [])
        self.assertTrue(any("error" in n.lower() for n in notes))

    def test_persistence_warning(self) -> None:
        funcs = [
            BlueprintFunction("save_record", ("data",), "bool", "Save", ()),
            BlueprintFunction("validate_input", ("data",), "bool", "Validate", ()),
        ]
        notes = _derive_safety_notes(funcs, [])
        self.assertTrue(any("persistence" in n.lower() for n in notes))

    def test_always_has_review_note(self) -> None:
        funcs = [BlueprintFunction("add_user", ("name",), "bool", "Add", ())]
        notes = _derive_safety_notes(funcs, [])
        self.assertTrue(any("review" in n.lower() for n in notes))


class TestBuildSpecCodeBlueprint(TestCase):
    def test_builds_blueprint_from_feature(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_feature_with_ac(
                root,
                "add-user",
                [
                    "AC001 The system SHALL add a new user profile",
                    "AC002 The system SHALL validate the input data",
                    "AC003 The system SHALL handle errors when the operation fails",
                ],
            )
            report = build_spec_code_blueprint(root, "add-user")
            self.assertEqual(report.feature_id, "add-user")
            self.assertIsInstance(report.modules, tuple)
            self.assertIsInstance(report.functions, tuple)
            self.assertIsInstance(report.coverage_summary, dict)

    def test_raises_for_missing_bundle(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            with self.assertRaises(FeatureBundleNotFoundError):
                build_spec_code_blueprint(root, "nonexistent")

    def test_raises_for_invalid_slug(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            with self.assertRaises(InvalidFeatureSlug):
                build_spec_code_blueprint(root, "INVALID SLUG!")

    def test_blueprint_has_safety_notes(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_feature_with_ac(
                root,
                "safe-feature",
                [
                    "AC001 The system SHALL add a new record",
                ],
            )
            report = build_spec_code_blueprint(root, "safe-feature")
            self.assertTrue(len(report.safety_notes) > 0)

    def test_blueprint_with_error_paths(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_feature_with_ac(
                root,
                "error-feature",
                [
                    "AC001 The system SHALL handle the error when processing fails",
                ],
            )
            report = build_spec_code_blueprint(root, "error-feature")
            self.assertTrue(len(report.error_paths) > 0)


class TestRenderBlueprintJson(TestCase):
    def test_json_is_valid(self) -> None:
        report = BlueprintReport(
            feature_id="test-feature",
            modules=(),
            functions=(),
            data_entities=(),
            error_paths=(),
            coverage_summary={"modules_total": 0, "functions_total": 0, "data_entities_total": 0, "error_paths_total": 0, "unique_ac_covered": 0, "ac_ids_covered": []},
            safety_notes=("Test note",),
        )
        result = render_blueprint_json(report)
        parsed = json.loads(result)
        self.assertEqual(parsed["feature_id"], "test-feature")

    def test_json_contains_modules(self) -> None:
        report = BlueprintReport(
            feature_id="test-feature",
            modules=(BlueprintModule("src/test.py", "Test module", (), ("AC001",)),),
            functions=(),
            data_entities=(),
            error_paths=(),
            coverage_summary={"modules_total": 1, "functions_total": 0, "data_entities_total": 0, "error_paths_total": 0, "unique_ac_covered": 1, "ac_ids_covered": ["AC001"]},
            safety_notes=(),
        )
        result = render_blueprint_json(report)
        parsed = json.loads(result)
        self.assertEqual(len(parsed["modules"]), 1)

    def test_json_contains_functions(self) -> None:
        report = BlueprintReport(
            feature_id="test-feature",
            modules=(),
            functions=(BlueprintFunction("test_fn", ("x",), "bool", "Test", ("AC001",)),),
            data_entities=(),
            error_paths=(),
            coverage_summary={"modules_total": 0, "functions_total": 1, "data_entities_total": 0, "error_paths_total": 0, "unique_ac_covered": 1, "ac_ids_covered": ["AC001"]},
            safety_notes=(),
        )
        result = render_blueprint_json(report)
        parsed = json.loads(result)
        self.assertEqual(len(parsed["functions"]), 1)

    def test_json_is_deterministic(self) -> None:
        report = BlueprintReport(
            feature_id="test-feature",
            modules=(BlueprintModule("src/test.py", "Test", (), ("AC001",)),),
            functions=(BlueprintFunction("fn", ("a",), "bool", "Desc", ("AC001",)),),
            data_entities=(BlueprintDataEntity("entity", ("attr",), "Desc", ("AC001",)),),
            error_paths=(BlueprintErrorPath("cond", "ValueError", "handle", ("AC001",)),),
            coverage_summary={"modules_total": 1, "functions_total": 1, "data_entities_total": 1, "error_paths_total": 1, "unique_ac_covered": 1, "ac_ids_covered": ["AC001"]},
            safety_notes=("Note 1", "Note 2"),
        )
        result1 = render_blueprint_json(report)
        result2 = render_blueprint_json(report)
        self.assertEqual(result1, result2)


class TestRenderBlueprintText(TestCase):
    def test_text_has_feature_id(self) -> None:
        report = BlueprintReport(
            feature_id="my-feature",
            modules=(),
            functions=(),
            data_entities=(),
            error_paths=(),
            coverage_summary={"modules_total": 0, "functions_total": 0, "data_entities_total": 0, "error_paths_total": 0, "unique_ac_covered": 0, "ac_ids_covered": []},
            safety_notes=(),
        )
        result = render_blueprint_text(report)
        self.assertIn("my-feature", result)

    def test_text_has_modules_section(self) -> None:
        report = BlueprintReport(
            feature_id="test",
            modules=(BlueprintModule("src/mod.py", "Do things", (), ("AC001",)),),
            functions=(),
            data_entities=(),
            error_paths=(),
            coverage_summary={"modules_total": 1, "functions_total": 0, "data_entities_total": 0, "error_paths_total": 0, "unique_ac_covered": 1, "ac_ids_covered": ["AC001"]},
            safety_notes=(),
        )
        result = render_blueprint_text(report)
        self.assertIn("Modules:", result)
        self.assertIn("src/mod.py", result)

    def test_text_has_data_entities_section(self) -> None:
        report = BlueprintReport(
            feature_id="test",
            modules=(),
            functions=(),
            data_entities=(BlueprintDataEntity("record", ("id",), "A record", ("AC001",)),),
            error_paths=(),
            coverage_summary={"modules_total": 0, "functions_total": 0, "data_entities_total": 1, "error_paths_total": 0, "unique_ac_covered": 1, "ac_ids_covered": ["AC001"]},
            safety_notes=(),
        )
        result = render_blueprint_text(report)
        self.assertIn("Data Entities:", result)

    def test_text_has_error_paths_section(self) -> None:
        report = BlueprintReport(
            feature_id="test",
            modules=(),
            functions=(),
            data_entities=(),
            error_paths=(BlueprintErrorPath("timeout", "TimeoutError", "Retry", ("AC001",)),),
            coverage_summary={"modules_total": 0, "functions_total": 0, "data_entities_total": 0, "error_paths_total": 1, "unique_ac_covered": 1, "ac_ids_covered": ["AC001"]},
            safety_notes=(),
        )
        result = render_blueprint_text(report)
        self.assertIn("Error Paths:", result)

    def test_text_has_safety_notes_section(self) -> None:
        report = BlueprintReport(
            feature_id="test",
            modules=(),
            functions=(),
            data_entities=(),
            error_paths=(),
            coverage_summary={"modules_total": 0, "functions_total": 0, "data_entities_total": 0, "error_paths_total": 0, "unique_ac_covered": 0, "ac_ids_covered": []},
            safety_notes=("Note 1",),
        )
        result = render_blueprint_text(report)
        self.assertIn("Safety Notes:", result)

    def test_text_shows_no_modules_when_empty(self) -> None:
        report = BlueprintReport(
            feature_id="test",
            modules=(),
            functions=(),
            data_entities=(),
            error_paths=(),
            coverage_summary={"modules_total": 0, "functions_total": 0, "data_entities_total": 0, "error_paths_total": 0, "unique_ac_covered": 0, "ac_ids_covered": []},
            safety_notes=(),
        )
        result = render_blueprint_text(report)
        self.assertIn("No modules derived", result)


class TestBlueprintCLI(TestCase):
    def test_blueprint_generate_help(self) -> None:
        with self.assertRaises(SystemExit) as cm:
            main(["blueprint", "generate", "--help"])
        self.assertEqual(cm.exception.code, 0)

    def test_blueprint_generate_missing_feature(self) -> None:
        with TemporaryDirectory() as tmpdir:
            result = main(["blueprint", "generate", "nonexistent", tmpdir])
            self.assertEqual(result, 1)

    def test_blueprint_generate_invalid_slug(self) -> None:
        with TemporaryDirectory() as tmpdir:
            result = main(["blueprint", "generate", "INVALID SLUG!", tmpdir])
            self.assertEqual(result, 2)

    def test_blueprint_generate_success(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_feature_with_ac(
                root,
                "test-feature",
                [
                    "AC001 The system SHALL add a new user",
                    "AC002 The system SHALL validate the input",
                ],
            )
            result = main(["blueprint", "generate", "test-feature", tmpdir])
            self.assertEqual(result, 0)

    def test_blueprint_generate_json(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_feature_with_ac(
                root,
                "json-feature",
                [
                    "AC001 The system SHALL create a new record",
                ],
            )
            result = main(["blueprint", "generate", "json-feature", tmpdir, "--json"])
            self.assertEqual(result, 0)

    def test_blueprint_generate_output_dir(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_feature_with_ac(
                root,
                "output-feature",
                [
                    "AC001 The system SHALL add an item",
                ],
            )
            output_dir = os.path.join(tmpdir, "output")
            result = main(["blueprint", "generate", "output-feature", tmpdir, "--output-dir", output_dir])
            self.assertEqual(result, 0)
            self.assertTrue(Path(output_dir, "blueprint.json").exists())
            self.assertTrue(Path(output_dir, "blueprint.md").exists())

    def test_blueprint_generate_output_dir_no_force_overwrite(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_feature_with_ac(
                root,
                "force-feature",
                [
                    "AC001 The system SHALL add an item",
                ],
            )
            output_dir = os.path.join(tmpdir, "output")
            main(["blueprint", "generate", "force-feature", tmpdir, "--output-dir", output_dir])
            result = main(["blueprint", "generate", "force-feature", tmpdir, "--output-dir", output_dir])
            self.assertEqual(result, 1)

    def test_blueprint_generate_output_dir_force_overwrite(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_feature_with_ac(
                root,
                "force2-feature",
                [
                    "AC001 The system SHALL add an item",
                ],
            )
            output_dir = os.path.join(tmpdir, "output2")
            main(["blueprint", "generate", "force2-feature", tmpdir, "--output-dir", output_dir])
            result = main(["blueprint", "generate", "force2-feature", tmpdir, "--output-dir", output_dir, "--force"])
            self.assertEqual(result, 0)

    def test_blueprint_generate_fail_on_gaps_no_gaps(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_feature_with_ac(
                root,
                "no-gap-feature",
                [
                    "AC001 The system SHALL add a user for testing",
                ],
            )
            result = main(["blueprint", "generate", "no-gap-feature", tmpdir, "--fail-on-gaps"])
            self.assertEqual(result, 0)

    def test_blueprint_generate_fail_on_gaps_has_gaps(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_feature_with_ac(
                root,
                "gap-feature",
                [
                ],
            )
            result = main(["blueprint", "generate", "gap-feature", tmpdir, "--fail-on-gaps"])
            self.assertEqual(result, 3)

    def test_blueprint_generate_text_output(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_feature_with_ac(
                root,
                "text-feature",
                [
                    "AC001 The system SHALL display a message",
                ],
            )
            result = main(["blueprint", "generate", "text-feature", tmpdir])
            self.assertEqual(result, 0)


class TestDataStructures(TestCase):
    def test_blueprint_function_as_dict(self) -> None:
        fn = BlueprintFunction("test_fn", ("a", "b"), "int", "Description", ("AC001",))
        d = fn.as_dict()
        self.assertEqual(d["name"], "test_fn")
        self.assertEqual(d["parameters"], ["a", "b"])
        self.assertEqual(d["return_type"], "int")
        self.assertEqual(d["ac_ids"], ["AC001"])

    def test_blueprint_module_as_dict(self) -> None:
        fn = BlueprintFunction("fn", ("x",), "bool", "Test", ("AC001",))
        mod = BlueprintModule("src/test.py", "Test module", (fn,), ("AC001",))
        d = mod.as_dict()
        self.assertEqual(d["module_path"], "src/test.py")
        self.assertEqual(len(d["functions"]), 1)

    def test_blueprint_data_entity_as_dict(self) -> None:
        entity = BlueprintDataEntity("user", ("name", "email"), "User", ("AC001",))
        d = entity.as_dict()
        self.assertEqual(d["name"], "user")
        self.assertEqual(d["attributes"], ["name", "email"])

    def test_blueprint_error_path_as_dict(self) -> None:
        ep = BlueprintErrorPath("timeout", "TimeoutError", "Retry", ("AC001",))
        d = ep.as_dict()
        self.assertEqual(d["condition"], "timeout")
        self.assertEqual(d["exception_type"], "TimeoutError")

    def test_blueprint_report_as_dict(self) -> None:
        report = BlueprintReport(
            feature_id="test",
            modules=(),
            functions=(),
            data_entities=(),
            error_paths=(),
            coverage_summary={"modules_total": 0, "functions_total": 0, "data_entities_total": 0, "error_paths_total": 0, "unique_ac_covered": 0, "ac_ids_covered": []},
            safety_notes=(),
        )
        d = report.as_dict()
        self.assertEqual(d["feature_id"], "test")
        self.assertIn("coverage_summary", d)
