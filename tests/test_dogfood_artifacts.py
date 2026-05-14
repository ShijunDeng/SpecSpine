from pathlib import Path
from unittest import TestCase

from specspine.features import build_feature_ready_report
from specspine.status import build_status
from specspine.validation import build_validation_report


REPO_ROOT = Path(__file__).resolve().parents[1]


class DogfoodArtifactsTests(TestCase):
    def test_current_repository_reports_complete_fused_workspace(self) -> None:
        status = build_status(REPO_ROOT)

        self.assertTrue(status["workspace"]["complete"])
        self.assertTrue(status["fusion"]["complete"])
        self.assertEqual(status["workspace"]["missing"], [])
        self.assertEqual(status["fusion"]["missing"], [])
        features = {
            feature["slug"]: feature
            for feature in status["features"]
        }
        for slug in (
            "feature-status-lifecycle",
            "feature-readiness-gate",
            "feature-handoff-packet",
            "status-feature-summaries",
            "feature-task-export",
            "feature-traceability-export",
            "status-validation-summary",
            "feature-transition-policy",
        ):
            with self.subTest(slug=slug):
                dogfood = features[slug]
                self.assertEqual(dogfood["status"], "validated")
                self.assertTrue(dogfood["status_consistent"])
        for upstream in ("openspec", "speckit", "superpowers"):
            self.assertTrue(status["upstreams"][upstream]["enabled"])
            self.assertTrue(status["upstreams"][upstream]["config_exists"])

    def test_current_repository_validation_contract_passes(self) -> None:
        report = build_validation_report(
            REPO_ROOT,
            include_fusion=True,
            include_features=True,
        )

        self.assertTrue(report["ok"])
        self.assertEqual(report["summary"]["fail"], 0)
        checks = {(check["id"], check["status"]) for check in report["checks"]}
        self.assertIn(("fusion.integration_mode", "pass"), checks)
        self.assertIn(("fusion.vendored_upstream_code", "pass"), checks)
        self.assertIn(("feature.status_consistency:feature-status-lifecycle", "pass"), checks)
        self.assertIn(("feature.status_consistency:feature-readiness-gate", "pass"), checks)
        self.assertIn(("feature.status_consistency:feature-handoff-packet", "pass"), checks)
        self.assertIn(("feature.status_consistency:status-feature-summaries", "pass"), checks)
        self.assertIn(("feature.status_consistency:feature-task-export", "pass"), checks)
        self.assertIn(("feature.status_consistency:feature-traceability-export", "pass"), checks)
        self.assertIn(("feature.status_consistency:status-validation-summary", "pass"), checks)
        self.assertIn(("feature.status_consistency:feature-transition-policy", "pass"), checks)
        for upstream in ("openspec", "speckit", "superpowers"):
            self.assertIn((f"fusion.adapter_boundary:{upstream}", "pass"), checks)

    def test_agents_file_preserves_project_rules(self) -> None:
        content = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

        required_snippets = [
            "PYTHONPATH=src python3 -m specspine status . --json --validate",
            "PYTHONPATH=src python3 -m specspine status . --json --validate --feature-summaries",
            "PYTHONPATH=src python3 -m specspine validate . --fusion --features",
            "PYTHONPATH=src python3 -m unittest discover -s tests",
            "PYTHONPATH=src python3 -m specspine feature status <slug> . --json",
            "PYTHONPATH=src python3 -m specspine feature status <slug> . --set planned --enforce-transition --json",
            "PYTHONPATH=src python3 -m specspine feature handoff <slug> . --json",
            "PYTHONPATH=src python3 -m specspine feature tasks <slug> . --json",
            "Keep feature specs, implementation tasks, and quality checks traceable",
            "prefer `--enforce-transition` when advancing lifecycle state",
            "Do not vendor upstream source code.",
            "Do not read or write GitHub tokens",
            "Use `--run-upstream` only when the user explicitly asks",
        ]
        for snippet in required_snippets:
            self.assertIn(snippet, content)

    def test_fusion_artifacts_keep_no_vendor_contract(self) -> None:
        fusion_yaml = (REPO_ROOT / ".specspine" / "fusion.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("integration_mode: adapter", fusion_yaml)
        self.assertIn("vendored_upstream_code: false", fusion_yaml)

        adapter_dir = REPO_ROOT / ".specspine" / "adapters"
        for adapter in ("openspec", "speckit", "superpowers"):
            content = (adapter_dir / f"{adapter}.md").read_text(encoding="utf-8")
            self.assertIn("no vendored source code", content.lower())

    def test_project_specs_are_not_left_as_generated_placeholders(self) -> None:
        artifact_paths = [
            "specs/intent.md",
            "specs/product.md",
            "specs/architecture.md",
            "execution/plan.md",
            "execution/tasks.md",
            "quality/checklist.md",
            "quality/review.md",
        ]
        generated_placeholder_phrases = [
            "What problem are we solving, and why does it matter now?",
            "Who benefits from this work?",
            "What measurable signals show that the work succeeded?",
            "What business, technical, legal, operational, or timing constraints shape the solution?",
            "What should be built?",
            "What is explicitly out of scope?",
            "What should users be able to do from start to finish?",
            "What must be true before this work is considered complete?",
            "What are the major components and boundaries?",
            "What data structures, APIs, files, commands, or events matter?",
            "What decisions have been made, and why?",
            "What can break the plan, and how will it be handled?",
            "What are the meaningful checkpoints?",
            "What tasks need to be completed?",
            "What needs to happen first?",
            "What must be resolved before implementation can proceed safely?",
            "Define intent",
            "Draft product spec",
            "Document architecture decisions",
            "Break work into implementation tasks",
            "Define quality gates",
            "Acceptance criteria are complete.",
            "Tests cover the changed behavior.",
            "Documentation reflects the final behavior.",
            "Risks and tradeoffs are recorded.",
            "Release readiness is reviewed.",
            "What must be true before this work ships?",
            "What issues, regressions, or risks were found?",
            "What changed after review?",
            "What should users or operators know?",
        ]
        combined = "\n".join(
            (REPO_ROOT / relative_path).read_text(encoding="utf-8")
            for relative_path in artifact_paths
        )

        for phrase in generated_placeholder_phrases:
            self.assertNotIn(phrase, combined)

    def test_feature_status_lifecycle_bundle_has_no_todo_placeholders(self) -> None:
        artifact_paths = [
            "specs/features/feature-status-lifecycle.md",
            "execution/features/feature-status-lifecycle.md",
            "quality/features/feature-status-lifecycle.md",
            "specs/features/status-validation-summary.md",
            "execution/features/status-validation-summary.md",
            "quality/features/status-validation-summary.md",
            "specs/features/feature-task-export.md",
            "execution/features/feature-task-export.md",
            "quality/features/feature-task-export.md",
            "specs/features/feature-readiness-gate.md",
            "execution/features/feature-readiness-gate.md",
            "quality/features/feature-readiness-gate.md",
            "specs/features/feature-handoff-packet.md",
            "execution/features/feature-handoff-packet.md",
            "quality/features/feature-handoff-packet.md",
            "specs/features/status-feature-summaries.md",
            "execution/features/status-feature-summaries.md",
            "quality/features/status-feature-summaries.md",
            "specs/features/feature-transition-policy.md",
            "execution/features/feature-transition-policy.md",
            "quality/features/feature-transition-policy.md",
        ]
        combined = "\n".join(
            (REPO_ROOT / relative_path).read_text(encoding="utf-8")
            for relative_path in artifact_paths
        )

        self.assertNotIn("TODO", combined)

    def test_feature_readiness_gate_dogfood_bundle_passes_its_gate(self) -> None:
        report = build_feature_ready_report(REPO_ROOT, "feature-readiness-gate")

        self.assertTrue(report.ready)
        self.assertEqual(report.summary["fail"], 0)

    def test_status_feature_summaries_dogfood_bundle_passes_its_gate(self) -> None:
        report = build_feature_ready_report(REPO_ROOT, "status-feature-summaries")

        self.assertTrue(report.ready)
        self.assertEqual(report.summary["fail"], 0)

    def test_feature_transition_policy_dogfood_bundle_passes_its_gate(self) -> None:
        report = build_feature_ready_report(REPO_ROOT, "feature-transition-policy")

        self.assertTrue(report.ready)
        self.assertEqual(report.status, "validated")
        self.assertEqual(report.summary["fail"], 0)
