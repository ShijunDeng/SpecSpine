from pathlib import Path
from unittest import TestCase

from specspine.features import build_feature_ready_report, build_feature_tests_report
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
            "feature-pr-draft",
            "feature-test-packet",
            "feature-template-refresh",
            "feature-summary-filters",
            "feature-test-coverage-links",
            "feature-coverage-readiness",
            "feature-task-issue-drafts",
            "status-validation-warnings",
            "feature-summary-metadata",
            "quality-gate-definitions",
            "quality-gate-metadata",
            "adapter-lifecycle-mappings",
            "adapter-feature-handoff",
            "status-coverage-readiness-summaries",
            "adapter-handoff-artifacts",
            "adapter-handoff-structured-artifacts",
            "workspace-readiness-policy",
            "extended-feature-metadata",
            "feature-metadata-filters",
            "status-readiness-rollup",
            "coverage-debt-report",
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
        self.assertIn(("feature.status_consistency:feature-pr-draft", "pass"), checks)
        self.assertIn(("feature.status_consistency:feature-test-packet", "pass"), checks)
        self.assertIn(("feature.status_consistency:feature-summary-filters", "pass"), checks)
        self.assertIn(("feature.status_consistency:feature-test-coverage-links", "pass"), checks)
        self.assertIn(("feature.status_consistency:feature-coverage-readiness", "pass"), checks)
        self.assertIn(("feature.status_consistency:feature-task-issue-drafts", "pass"), checks)
        self.assertIn(("feature.status_consistency:status-validation-warnings", "pass"), checks)
        self.assertIn(("feature.status_consistency:feature-summary-metadata", "pass"), checks)
        self.assertIn(("feature.status_consistency:quality-gate-definitions", "pass"), checks)
        self.assertIn(("feature.status_consistency:quality-gate-metadata", "pass"), checks)
        self.assertIn(("feature.status_consistency:adapter-lifecycle-mappings", "pass"), checks)
        self.assertIn(("feature.status_consistency:adapter-feature-handoff", "pass"), checks)
        self.assertIn(("feature.status_consistency:status-coverage-readiness-summaries", "pass"), checks)
        self.assertIn(("feature.status_consistency:adapter-handoff-artifacts", "pass"), checks)
        self.assertIn(("feature.status_consistency:adapter-handoff-structured-artifacts", "pass"), checks)
        self.assertIn(("feature.status_consistency:workspace-readiness-policy", "pass"), checks)
        self.assertIn(("feature.status_consistency:extended-feature-metadata", "pass"), checks)
        self.assertIn(("feature.status_consistency:feature-metadata-filters", "pass"), checks)
        self.assertIn(("feature.status_consistency:status-readiness-rollup", "pass"), checks)
        self.assertIn(("feature.status_consistency:coverage-debt-report", "pass"), checks)
        for upstream in ("openspec", "speckit", "superpowers"):
            self.assertIn((f"fusion.adapter_boundary:{upstream}", "pass"), checks)

    def test_agents_file_preserves_project_rules(self) -> None:
        content = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

        required_snippets = [
            "PYTHONPATH=src python3 -m specspine status . --json --validate",
            "PYTHONPATH=src python3 -m specspine status . --json --validate --validation-warnings",
            "PYTHONPATH=src python3 -m specspine status . --json --validate --feature-summaries",
            "PYTHONPATH=src python3 -m specspine status . --json --validate --feature-summaries --feature-status validated --feature-ready yes --feature-sort slug",
            "PYTHONPATH=src python3 -m specspine status . --json --validate --feature-summaries --feature-require-coverage --feature-ready yes --feature-sort priority",
            "PYTHONPATH=src python3 -m specspine status . --json --feature-summaries --feature-project \"Native feature bundles\" --feature-sort effort",
            "PYTHONPATH=src python3 -m specspine policy . --json",
            "PYTHONPATH=src python3 -m specspine status . --json --feature-summaries --feature-policy --feature-ready yes",
            "PYTHONPATH=src python3 -m specspine status . --json --readiness-summary",
            "PYTHONPATH=src python3 -m specspine status . --json --readiness-summary --readiness-policy",
            "PYTHONPATH=src python3 -m specspine coverage debt . --json",
            "PYTHONPATH=src python3 -m specspine coverage debt . --json --policy",
            "PYTHONPATH=src python3 -m specspine gates . --json",
            "PYTHONPATH=src python3 -m specspine adapters lifecycle . --json",
            "PYTHONPATH=src python3 -m specspine validate . --fusion --features",
            "PYTHONPATH=src python3 -m unittest discover -s tests",
            "PYTHONPATH=src python3 -m specspine feature status <slug> . --json",
            "PYTHONPATH=src python3 -m specspine feature status <slug> . --set planned --enforce-transition --json",
            "PYTHONPATH=src python3 -m specspine feature handoff <slug> . --json",
            "PYTHONPATH=src python3 -m specspine feature tasks <slug> . --json",
            "PYTHONPATH=src python3 -m specspine feature task-issues <slug> . --json",
            "PYTHONPATH=src python3 -m specspine feature ready <slug> . --json",
            "PYTHONPATH=src python3 -m specspine feature ready <slug> . --json --require-coverage",
            "PYTHONPATH=src python3 -m specspine feature ready <slug> . --json --policy",
            "PYTHONPATH=src python3 -m specspine feature tests <slug> . --json",
            "PYTHONPATH=src python3 -m specspine feature pr <slug> . --json",
            "Keep feature specs, implementation tasks, and quality checks traceable",
            "Use `specspine gates . --json` to export quality gate definitions and optional severity/owner/CI metadata only",
            "Use `specspine adapters lifecycle . --json` to export adapter lifecycle definitions only",
            "prefer `--enforce-transition` when advancing lifecycle state",
            "Do not vendor upstream source code.",
            "Do not read or write GitHub tokens",
            "Use `--run-upstream` only when the user explicitly asks",
            "generated peer files include focused handoff, task issue drafts, tests, PR, ready, and validation guidance",
        ]
        for snippet in required_snippets:
            self.assertIn(snippet, content)

    def test_feature_handoff_documentation_describes_workflow(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        architecture = (REPO_ROOT / "docs" / "architecture.md").read_text(
            encoding="utf-8"
        )

        for snippet in (
            "specspine feature handoff <slug> [path] [--json] [--output FILE] [--force]",
            "composes the existing local feature status, trace, tasks, readiness, and release readiness evidence",
            "recommended commands",
            "handoff",
            "tasks",
            "task-issues",
            "trace",
            "tests",
            "ready",
            "pr",
            "validate . --fusion --features",
        ):
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, architecture)
        self.assertIn("A native feature handoff packet exporter", readme)
        self.assertIn("specspine feature handoff add-dark-mode . --json", readme)

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
            "specs/features/feature-pr-draft.md",
            "execution/features/feature-pr-draft.md",
            "quality/features/feature-pr-draft.md",
            "specs/features/feature-test-packet.md",
            "execution/features/feature-test-packet.md",
            "quality/features/feature-test-packet.md",
            "specs/features/feature-template-refresh.md",
            "execution/features/feature-template-refresh.md",
            "quality/features/feature-template-refresh.md",
            "specs/features/feature-summary-filters.md",
            "execution/features/feature-summary-filters.md",
            "quality/features/feature-summary-filters.md",
            "specs/features/feature-test-coverage-links.md",
            "execution/features/feature-test-coverage-links.md",
            "quality/features/feature-test-coverage-links.md",
            "specs/features/feature-coverage-readiness.md",
            "execution/features/feature-coverage-readiness.md",
            "quality/features/feature-coverage-readiness.md",
            "specs/features/feature-task-issue-drafts.md",
            "execution/features/feature-task-issue-drafts.md",
            "quality/features/feature-task-issue-drafts.md",
            "specs/features/status-validation-warnings.md",
            "execution/features/status-validation-warnings.md",
            "quality/features/status-validation-warnings.md",
            "specs/features/feature-summary-metadata.md",
            "execution/features/feature-summary-metadata.md",
            "quality/features/feature-summary-metadata.md",
            "specs/features/quality-gate-definitions.md",
            "execution/features/quality-gate-definitions.md",
            "quality/features/quality-gate-definitions.md",
            "specs/features/quality-gate-metadata.md",
            "execution/features/quality-gate-metadata.md",
            "quality/features/quality-gate-metadata.md",
            "specs/features/adapter-lifecycle-mappings.md",
            "execution/features/adapter-lifecycle-mappings.md",
            "quality/features/adapter-lifecycle-mappings.md",
            "specs/features/adapter-feature-handoff.md",
            "execution/features/adapter-feature-handoff.md",
            "quality/features/adapter-feature-handoff.md",
            "specs/features/status-coverage-readiness-summaries.md",
            "execution/features/status-coverage-readiness-summaries.md",
            "quality/features/status-coverage-readiness-summaries.md",
            "specs/features/adapter-handoff-artifacts.md",
            "execution/features/adapter-handoff-artifacts.md",
            "quality/features/adapter-handoff-artifacts.md",
            "specs/features/adapter-handoff-structured-artifacts.md",
            "execution/features/adapter-handoff-structured-artifacts.md",
            "quality/features/adapter-handoff-structured-artifacts.md",
            "specs/features/workspace-readiness-policy.md",
            "execution/features/workspace-readiness-policy.md",
            "quality/features/workspace-readiness-policy.md",
            "specs/features/extended-feature-metadata.md",
            "execution/features/extended-feature-metadata.md",
            "quality/features/extended-feature-metadata.md",
            "specs/features/feature-metadata-filters.md",
            "execution/features/feature-metadata-filters.md",
            "quality/features/feature-metadata-filters.md",
            "specs/features/status-readiness-rollup.md",
            "execution/features/status-readiness-rollup.md",
            "quality/features/status-readiness-rollup.md",
            "specs/features/coverage-debt-report.md",
            "execution/features/coverage-debt-report.md",
            "quality/features/coverage-debt-report.md",
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

    def test_feature_pr_draft_dogfood_bundle_passes_its_gate(self) -> None:
        report = build_feature_ready_report(REPO_ROOT, "feature-pr-draft")

        self.assertTrue(report.ready)
        self.assertEqual(report.status, "validated")
        self.assertEqual(report.summary["fail"], 0)

    def test_feature_test_packet_dogfood_bundle_passes_its_gate(self) -> None:
        report = build_feature_ready_report(REPO_ROOT, "feature-test-packet")

        self.assertTrue(report.ready)
        self.assertEqual(report.status, "validated")
        self.assertEqual(report.summary["fail"], 0)

    def test_feature_template_refresh_dogfood_bundle_passes_its_gate(self) -> None:
        report = build_feature_ready_report(REPO_ROOT, "feature-template-refresh")

        self.assertTrue(report.ready)
        self.assertEqual(report.status, "validated")
        self.assertEqual(report.summary["fail"], 0)

    def test_feature_summary_filters_dogfood_bundle_passes_its_gate(self) -> None:
        report = build_feature_ready_report(REPO_ROOT, "feature-summary-filters")

        self.assertTrue(report.ready)
        self.assertEqual(report.status, "validated")
        self.assertEqual(report.summary["fail"], 0)

    def test_feature_test_coverage_links_dogfood_bundle_passes_its_gate(self) -> None:
        report = build_feature_ready_report(REPO_ROOT, "feature-test-coverage-links")

        self.assertTrue(report.ready)
        self.assertEqual(report.status, "validated")
        self.assertEqual(report.summary["fail"], 0)

    def test_feature_coverage_readiness_dogfood_bundle_passes_default_and_coverage_gates(self) -> None:
        default_report = build_feature_ready_report(REPO_ROOT, "feature-coverage-readiness")
        coverage_report = build_feature_ready_report(
            REPO_ROOT,
            "feature-coverage-readiness",
            require_coverage=True,
        )

        self.assertTrue(default_report.ready)
        self.assertEqual(default_report.status, "validated")
        self.assertEqual(default_report.summary["fail"], 0)
        self.assertTrue(coverage_report.ready)
        self.assertEqual(coverage_report.status, "validated")
        self.assertTrue(coverage_report.coverage_required)
        self.assertEqual(coverage_report.summary["fail"], 0)
        self.assertIn(
            "feature.test_coverage",
            [check.id for check in coverage_report.checks],
        )

    def test_status_validation_warnings_dogfood_bundle_passes_its_gate(self) -> None:
        report = build_feature_ready_report(REPO_ROOT, "status-validation-warnings")

        self.assertTrue(report.ready)
        self.assertEqual(report.status, "validated")
        self.assertEqual(report.summary["fail"], 0)

    def test_feature_summary_metadata_dogfood_bundle_passes_its_gate(self) -> None:
        report = build_feature_ready_report(REPO_ROOT, "feature-summary-metadata")

        self.assertTrue(report.ready)
        self.assertEqual(report.status, "validated")
        self.assertEqual(report.summary["fail"], 0)

    def test_quality_gate_definitions_dogfood_bundle_passes_its_gate(self) -> None:
        report = build_feature_ready_report(REPO_ROOT, "quality-gate-definitions")

        self.assertTrue(report.ready)
        self.assertEqual(report.status, "validated")
        self.assertEqual(report.summary["fail"], 0)

    def test_quality_gate_metadata_dogfood_bundle_passes_default_and_coverage_gates(self) -> None:
        default_report = build_feature_ready_report(REPO_ROOT, "quality-gate-metadata")
        coverage_report = build_feature_ready_report(
            REPO_ROOT,
            "quality-gate-metadata",
            require_coverage=True,
        )

        self.assertTrue(default_report.ready)
        self.assertEqual(default_report.status, "validated")
        self.assertEqual(default_report.summary["fail"], 0)
        self.assertTrue(coverage_report.ready)
        self.assertEqual(coverage_report.status, "validated")
        self.assertTrue(coverage_report.coverage_required)
        self.assertEqual(coverage_report.summary["fail"], 0)

    def test_adapter_lifecycle_mappings_dogfood_bundle_passes_its_gate(self) -> None:
        report = build_feature_ready_report(REPO_ROOT, "adapter-lifecycle-mappings")

        self.assertTrue(report.ready)
        self.assertEqual(report.status, "validated")
        self.assertEqual(report.summary["fail"], 0)

    def test_adapter_feature_handoff_dogfood_bundle_passes_its_gate(self) -> None:
        report = build_feature_ready_report(REPO_ROOT, "adapter-feature-handoff")

        self.assertTrue(report.ready)
        self.assertEqual(report.status, "validated")
        self.assertEqual(report.summary["fail"], 0)

    def test_status_coverage_readiness_summaries_dogfood_bundle_passes_default_and_coverage_gates(self) -> None:
        default_report = build_feature_ready_report(
            REPO_ROOT,
            "status-coverage-readiness-summaries",
        )
        coverage_report = build_feature_ready_report(
            REPO_ROOT,
            "status-coverage-readiness-summaries",
            require_coverage=True,
        )

        self.assertTrue(default_report.ready)
        self.assertEqual(default_report.status, "validated")
        self.assertEqual(default_report.summary["fail"], 0)
        self.assertTrue(coverage_report.ready)
        self.assertEqual(coverage_report.status, "validated")
        self.assertTrue(coverage_report.coverage_required)
        self.assertEqual(coverage_report.summary["fail"], 0)

    def test_adapter_handoff_artifacts_dogfood_bundle_passes_default_and_coverage_gates(self) -> None:
        default_report = build_feature_ready_report(
            REPO_ROOT,
            "adapter-handoff-artifacts",
        )
        coverage_report = build_feature_ready_report(
            REPO_ROOT,
            "adapter-handoff-artifacts",
            require_coverage=True,
        )

        self.assertTrue(default_report.ready)
        self.assertEqual(default_report.status, "validated")
        self.assertEqual(default_report.summary["fail"], 0)
        self.assertTrue(coverage_report.ready)
        self.assertEqual(coverage_report.status, "validated")
        self.assertTrue(coverage_report.coverage_required)
        self.assertEqual(coverage_report.summary["fail"], 0)

    def test_adapter_handoff_structured_artifacts_dogfood_bundle_passes_default_and_coverage_gates(self) -> None:
        default_report = build_feature_ready_report(
            REPO_ROOT,
            "adapter-handoff-structured-artifacts",
        )
        coverage_report = build_feature_ready_report(
            REPO_ROOT,
            "adapter-handoff-structured-artifacts",
            require_coverage=True,
        )

        self.assertTrue(default_report.ready)
        self.assertEqual(default_report.status, "validated")
        self.assertEqual(default_report.summary["fail"], 0)
        self.assertTrue(coverage_report.ready)
        self.assertEqual(coverage_report.status, "validated")
        self.assertTrue(coverage_report.coverage_required)
        self.assertEqual(coverage_report.summary["fail"], 0)

    def test_workspace_readiness_policy_artifacts_are_present(self) -> None:
        self.assertTrue((REPO_ROOT / ".specspine" / "policy.yaml").exists())
        for relative_path in (
            "specs/features/workspace-readiness-policy.md",
            "execution/features/workspace-readiness-policy.md",
            "quality/features/workspace-readiness-policy.md",
        ):
            self.assertTrue((REPO_ROOT / relative_path).exists())

    def test_workspace_readiness_policy_dogfood_bundle_passes_default_coverage_and_policy_gates(self) -> None:
        default_report = build_feature_ready_report(
            REPO_ROOT,
            "workspace-readiness-policy",
        )
        coverage_report = build_feature_ready_report(
            REPO_ROOT,
            "workspace-readiness-policy",
            require_coverage=True,
        )
        policy_report = build_feature_ready_report(
            REPO_ROOT,
            "workspace-readiness-policy",
            require_coverage=True,
            policy_applied=True,
            coverage_required_by_policy=True,
            policy_source=str(REPO_ROOT / ".specspine" / "policy.yaml"),
        )

        self.assertTrue(default_report.ready)
        self.assertEqual(default_report.status, "validated")
        self.assertEqual(default_report.summary["fail"], 0)
        self.assertTrue(coverage_report.ready)
        self.assertTrue(coverage_report.coverage_required)
        self.assertEqual(coverage_report.summary["fail"], 0)
        self.assertTrue(policy_report.ready)
        self.assertTrue(policy_report.policy_applied)
        self.assertTrue(policy_report.coverage_required_by_policy)
        self.assertEqual(policy_report.summary["fail"], 0)

    def test_extended_feature_metadata_dogfood_bundle_passes_default_coverage_and_policy_gates(self) -> None:
        default_report = build_feature_ready_report(
            REPO_ROOT,
            "extended-feature-metadata",
        )
        coverage_report = build_feature_ready_report(
            REPO_ROOT,
            "extended-feature-metadata",
            require_coverage=True,
        )
        policy_report = build_feature_ready_report(
            REPO_ROOT,
            "extended-feature-metadata",
            policy_applied=True,
            coverage_required_by_policy=False,
            policy_source=str(REPO_ROOT / ".specspine" / "policy.yaml"),
        )

        self.assertTrue(default_report.ready)
        self.assertEqual(default_report.status, "validated")
        self.assertEqual(default_report.summary["fail"], 0)
        self.assertTrue(coverage_report.ready)
        self.assertTrue(coverage_report.coverage_required)
        self.assertEqual(coverage_report.summary["fail"], 0)
        self.assertTrue(policy_report.ready)
        self.assertTrue(policy_report.policy_applied)
        self.assertFalse(policy_report.coverage_required_by_policy)
        self.assertEqual(policy_report.summary["fail"], 0)

    def test_feature_metadata_filters_dogfood_bundle_passes_default_coverage_and_policy_gates(self) -> None:
        default_report = build_feature_ready_report(
            REPO_ROOT,
            "feature-metadata-filters",
        )
        coverage_report = build_feature_ready_report(
            REPO_ROOT,
            "feature-metadata-filters",
            require_coverage=True,
        )
        policy_report = build_feature_ready_report(
            REPO_ROOT,
            "feature-metadata-filters",
            policy_applied=True,
            coverage_required_by_policy=False,
            policy_source=str(REPO_ROOT / ".specspine" / "policy.yaml"),
        )

        self.assertTrue(default_report.ready)
        self.assertEqual(default_report.status, "validated")
        self.assertEqual(default_report.summary["fail"], 0)
        self.assertTrue(coverage_report.ready)
        self.assertTrue(coverage_report.coverage_required)
        self.assertEqual(coverage_report.summary["fail"], 0)
        self.assertTrue(policy_report.ready)
        self.assertTrue(policy_report.policy_applied)
        self.assertFalse(policy_report.coverage_required_by_policy)
        self.assertEqual(policy_report.summary["fail"], 0)

    def test_status_readiness_rollup_dogfood_bundle_passes_default_and_coverage_gates(self) -> None:
        default_report = build_feature_ready_report(
            REPO_ROOT,
            "status-readiness-rollup",
        )
        coverage_report = build_feature_ready_report(
            REPO_ROOT,
            "status-readiness-rollup",
            require_coverage=True,
        )

        self.assertTrue(default_report.ready)
        self.assertEqual(default_report.status, "validated")
        self.assertEqual(default_report.summary["fail"], 0)
        self.assertTrue(coverage_report.ready)
        self.assertEqual(coverage_report.status, "validated")
        self.assertTrue(coverage_report.coverage_required)
        self.assertEqual(coverage_report.summary["fail"], 0)

    def test_coverage_debt_report_dogfood_bundle_passes_default_and_coverage_gates(self) -> None:
        default_report = build_feature_ready_report(
            REPO_ROOT,
            "coverage-debt-report",
        )
        coverage_report = build_feature_ready_report(
            REPO_ROOT,
            "coverage-debt-report",
            require_coverage=True,
        )

        self.assertTrue(default_report.ready)
        self.assertEqual(default_report.status, "validated")
        self.assertEqual(default_report.summary["fail"], 0)
        self.assertTrue(coverage_report.ready)
        self.assertEqual(coverage_report.status, "validated")
        self.assertTrue(coverage_report.coverage_required)
        self.assertEqual(coverage_report.summary["fail"], 0)

    def test_feature_test_packet_dogfood_exports_test_cases(self) -> None:
        report = build_feature_tests_report(REPO_ROOT, "feature-test-packet")

        self.assertTrue(report.ready)
        self.assertTrue(report.test_cases)
        self.assertEqual(report.test_cases[0].id, "TC001")
        self.assertEqual(report.test_cases[0].acceptance_criterion_id, "AC001")
        self.assertEqual(report.missing_files, ())

    def test_feature_test_coverage_links_dogfood_exports_coverage(self) -> None:
        report = build_feature_tests_report(REPO_ROOT, "feature-test-coverage-links")

        self.assertTrue(report.ready)
        self.assertTrue(report.test_coverage)
        self.assertEqual(report.summary["test_coverage"], {"done": 2, "open": 0, "total": 2})
        self.assertTrue(all(link.target_exists for link in report.test_coverage))
        statuses = {
            test_case.acceptance_criterion_id: test_case.status
            for test_case in report.test_cases
        }
        self.assertEqual(statuses["AC005"], "covered")
        self.assertEqual(statuses["AC008"], "covered")
