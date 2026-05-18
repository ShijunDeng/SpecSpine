import json
import os
import subprocess
import urllib.request
from contextlib import redirect_stderr, redirect_stdout
from hashlib import sha256
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from specspine.cli import main
from specspine.features import InvalidFeatureSlug
from specspine.provenance import (
    build_provenance_manifest,
    render_provenance_manifest_json,
    render_provenance_manifest_text,
)


def artifact_by_path(manifest, path: str) -> dict:
    for artifact in manifest.artifacts:
        if artifact["path"] == path:
            return artifact
    raise AssertionError(f"artifact not found: {path}")


def write_ready_feature(root: Path, slug: str = "audit-trail") -> None:
    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)
    (root / "tests" / "test_audit_trail.py").write_text(
        "# coverage target\n",
        encoding="utf-8",
    )
    (root / "specs" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Audit trail",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Acceptance Criteria",
                "",
                "- [x] Local audit evidence can be reviewed.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "execution" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Audit trail execution",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Tasks",
                "",
                "- [x] Implement the manifest builder.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "quality" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Audit trail quality",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Required Checks",
                "",
                "- [x] Manifest hashes were reviewed.",
                "",
                "## Test Coverage",
                "",
                "- [x] AC001 -> tests/test_audit_trail.py",
                "",
                "## Test Plan",
                "",
                "- Run focused provenance tests.",
                "",
                "## Release Readiness",
                "",
                "- [x] Evidence packet reviewed.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


class ProvenanceManifestTests(TestCase):
    def test_hashes_files_without_emitting_contents(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            secret_text = "do-not-emit-this-secret"
            (root / "evidence.txt").write_text(secret_text, encoding="utf-8")

            manifest = build_provenance_manifest(
                root,
                includes=("evidence.txt",),
            )

            artifact = artifact_by_path(manifest, "evidence.txt")
            self.assertTrue(artifact["exists"])
            self.assertEqual(artifact["kind"], "include")
            self.assertEqual(artifact["bytes"], len(secret_text.encode("utf-8")))
            self.assertEqual(
                artifact["sha256"],
                sha256(secret_text.encode("utf-8")).hexdigest(),
            )
            rendered = render_provenance_manifest_json(manifest)
            self.assertNotIn(secret_text, rendered)

    def test_missing_and_outside_root_includes_are_reported(self) -> None:
        with TemporaryDirectory() as workspace_tmp, TemporaryDirectory() as outside_tmp:
            root = Path(workspace_tmp)
            (root / "evidence-dir").mkdir()
            outside = Path(outside_tmp) / "outside.txt"
            outside.write_text("outside secret", encoding="utf-8")

            manifest = build_provenance_manifest(
                root,
                includes=("missing.txt", "evidence-dir", str(outside)),
            )

            missing = artifact_by_path(manifest, "missing.txt")
            self.assertFalse(missing["exists"])
            self.assertTrue(missing["inside_root"])
            self.assertEqual(missing["reason"], "missing")
            self.assertNotIn("sha256", missing)
            self.assertNotIn("bytes", missing)

            directory = artifact_by_path(manifest, "evidence-dir")
            self.assertTrue(directory["exists"])
            self.assertTrue(directory["inside_root"])
            self.assertEqual(directory["reason"], "not_file")
            self.assertNotIn("sha256", directory)
            self.assertNotIn("bytes", directory)

            outside_artifacts = [
                artifact
                for artifact in manifest.artifacts
                if artifact.get("requested_path") == str(outside)
            ]
            self.assertEqual(len(outside_artifacts), 1)
            artifact = outside_artifacts[0]
            self.assertTrue(artifact["exists"])
            self.assertFalse(artifact["inside_root"])
            self.assertEqual(artifact["reason"], "outside_root")
            self.assertNotIn("sha256", artifact)
            self.assertNotIn("bytes", artifact)

    def test_missing_feature_evidence_is_structured(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            manifest = build_provenance_manifest(root, feature="missing-feature")

            self.assertEqual(manifest.feature_id, "missing-feature")
            self.assertEqual(len(manifest.feature_evidence), 1)
            evidence = manifest.feature_evidence[0]
            self.assertFalse(evidence["has_native_files"])
            self.assertFalse(evidence["ready"])
            self.assertEqual(evidence["source_files"], [])
            self.assertEqual(
                set(evidence["missing_files"]),
                {
                    "specs/features/missing-feature.md",
                    "execution/features/missing-feature.md",
                    "quality/features/missing-feature.md",
                },
            )
            self.assertTrue(evidence["blocking_checks"])
            self.assertTrue(evidence["gaps"])

    def test_feature_mode_includes_peer_artifacts_and_evidence(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_ready_feature(root)

            manifest = build_provenance_manifest(root, feature="audit-trail")

            evidence = manifest.feature_evidence[0]
            self.assertTrue(evidence["coverage_required"])
            self.assertTrue(evidence["has_native_files"])
            self.assertTrue(evidence["ready"])
            self.assertEqual(evidence["blocking_checks"], [])
            self.assertEqual(evidence["gaps"], [])
            self.assertEqual(
                set(evidence["source_files"]),
                {
                    "specs/features/audit-trail.md",
                    "execution/features/audit-trail.md",
                    "quality/features/audit-trail.md",
                },
            )
            for relative_path in evidence["source_files"]:
                artifact = artifact_by_path(manifest, relative_path)
                self.assertIn("sha256", artifact)
                self.assertIn("bytes", artifact)

    def test_invalid_feature_slug_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            with self.assertRaises(InvalidFeatureSlug):
                build_provenance_manifest(Path(tmp), feature="Bad Slug")

    def test_cli_json_and_missing_feature_exit_codes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_ready_feature(root)
            evidence = root / "evidence.txt"
            evidence.write_text("do-not-emit-from-cli", encoding="utf-8")
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(
                    [
                        "provenance",
                        "manifest",
                        str(root),
                        "--json",
                        "--feature",
                        "audit-trail",
                        "--include",
                        "evidence.txt",
                    ]
                )

            self.assertEqual(code, 0, stderr.getvalue())
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["feature_id"], "audit-trail")
            self.assertEqual(payload["feature_evidence"][0]["has_native_files"], True)
            self.assertGreaterEqual(payload["summary"]["hashed_artifacts"], 1)
            self.assertNotIn("do-not-emit-from-cli", stdout.getvalue())

            missing_stdout = StringIO()
            with redirect_stdout(missing_stdout), redirect_stderr(StringIO()):
                missing_code = main(
                    [
                        "provenance",
                        "manifest",
                        str(root),
                        "--json",
                        "--feature",
                        "missing-feature",
                    ]
                )
            self.assertEqual(missing_code, 1)
            self.assertFalse(
                json.loads(missing_stdout.getvalue())["feature_evidence"][0][
                    "has_native_files"
                ]
            )

    def test_cli_invalid_slug_returns_two(self) -> None:
        with TemporaryDirectory() as tmp:
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(
                    ["provenance", "manifest", tmp, "--feature", "Bad Slug"]
                )

            self.assertEqual(code, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("Invalid feature slug", stderr.getvalue())

    def test_builder_is_local_only_and_renderers_are_pure(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "evidence.txt").write_text("local bytes", encoding="utf-8")

            with patch.object(
                subprocess,
                "run",
                side_effect=AssertionError("subprocess should not run"),
            ), patch.object(
                urllib.request,
                "urlopen",
                side_effect=AssertionError("network should not run"),
            ), patch.object(
                os,
                "getenv",
                side_effect=AssertionError("env should not be read"),
            ):
                manifest = build_provenance_manifest(
                    root,
                    includes=("evidence.txt",),
                )
                json_output = render_provenance_manifest_json(manifest)
                text_output = render_provenance_manifest_text(manifest)

            self.assertEqual(artifact_by_path(manifest, "evidence.txt")["exists"], True)
            self.assertIn('"feature_id": null', json_output)
            self.assertIn("advisory only", text_output)

    def test_json_and_text_renderers(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "evidence.txt").write_text("renderer bytes", encoding="utf-8")
            manifest = build_provenance_manifest(
                root,
                includes=("evidence.txt",),
            )

            json_output = render_provenance_manifest_json(manifest)
            text_output = render_provenance_manifest_text(manifest)

            payload = json.loads(json_output)
            self.assertEqual(payload["root"], str(root.resolve()))
            self.assertIn("artifacts", payload)
            self.assertIn("feature_evidence", payload)
            self.assertIn("summary", payload)
            self.assertIn("recommended_commands", payload)
            self.assertIn("safety_notes", payload)
            self.assertTrue(json_output.endswith("\n"))
            self.assertIn("Provenance manifest:", text_output)
            self.assertIn("Recommended commands:", text_output)
            self.assertIn("Safety notes:", text_output)
            self.assertIn("evidence.txt", text_output)
