from __future__ import annotations

import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from asset_pipeline_steward.cli import (
    build_maintenance_report,
    build_manifest_schema,
    load_manifest,
    main,
    validate_manifest,
)


class ManifestValidationTests(unittest.TestCase):
    def test_fixture_manifest_passes(self) -> None:
        manifest = load_manifest(ROOT / "examples" / "fixture_manifest.json")

        findings = validate_manifest(manifest)

        self.assertEqual([], findings)

    def test_private_path_is_blocked(self) -> None:
        manifest = load_manifest(ROOT / "examples" / "fixture_manifest.json")
        manifest["assets"][0]["path"] = r"C:\Users\example\private\asset.png"

        findings = validate_manifest(manifest)

        self.assertTrue(any(finding.severity == "blocker" for finding in findings))

    def test_model_weight_path_is_blocked(self) -> None:
        manifest = load_manifest(ROOT / "examples" / "fixture_manifest.json")
        manifest["models"][0]["path"] = "models/example.safetensors"

        findings = validate_manifest(manifest)

        self.assertTrue(
            any("model weight" in finding.message for finding in findings)
        )

    def test_workflow_requires_preflight(self) -> None:
        manifest = load_manifest(ROOT / "examples" / "fixture_manifest.json")
        manifest["workflows"][0].pop("preflight")

        findings = validate_manifest(manifest)

        self.assertTrue(any("preflight" in finding.path for finding in findings))

    def test_review_signals_require_ground_truth_and_supporting_evidence(self) -> None:
        manifest = load_manifest(ROOT / "examples" / "fixture_manifest.json")
        manifest["review_signals"] = [
            {
                "name": "automated-observation",
                "role": "supporting-evidence",
                "scale": "structured-notes",
            }
        ]

        findings = validate_manifest(manifest)

        self.assertTrue(any("ground-truth" in finding.message for finding in findings))

    def test_decision_gate_requires_next_action(self) -> None:
        manifest = load_manifest(ROOT / "examples" / "fixture_manifest.json")
        manifest["decision_gate"].pop("next_action")

        findings = validate_manifest(manifest)

        self.assertTrue(any("next_action" in finding.path for finding in findings))

    def test_handoff_requires_next_action(self) -> None:
        manifest = load_manifest(ROOT / "examples" / "fixture_manifest.json")
        manifest["handoff"].pop("next_action")

        findings = validate_manifest(manifest)

        self.assertTrue(any("handoff.next_action" == finding.path for finding in findings))

    def test_handoff_requires_blocker_list(self) -> None:
        manifest = load_manifest(ROOT / "examples" / "fixture_manifest.json")
        manifest["handoff"]["blockers"] = "none"

        findings = validate_manifest(manifest)

        self.assertTrue(any("handoff.blockers" == finding.path for finding in findings))

    def test_model_inventory_manifest_passes(self) -> None:
        manifest = load_manifest(ROOT / "examples" / "model_inventory_manifest.json")

        findings = validate_manifest(manifest)

        self.assertEqual([], findings)

    def test_schema_file_matches_generated_schema(self) -> None:
        schema_path = ROOT / "schemas" / "asset-pipeline-manifest.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))

        self.assertEqual(build_manifest_schema(), schema)

    def test_schema_command_prints_json_schema(self) -> None:
        with redirect_stdout(StringIO()) as output:
            exit_code = main(["schema"])

        schema = json.loads(output.getvalue())

        self.assertEqual(0, exit_code)
        self.assertEqual("AI Asset Pipeline Steward Manifest", schema["title"])
        self.assertIn("handoff", schema["required"])

    def test_cli_returns_nonzero_for_unsafe_manifest(self) -> None:
        manifest = load_manifest(ROOT / "examples" / "fixture_manifest.json")
        manifest["project"]["description"] = "contains token marker"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")

            with redirect_stdout(StringIO()):
                exit_code = main([str(path), "--json"])

        self.assertEqual(1, exit_code)

    def test_maintenance_report_summarizes_manifest(self) -> None:
        path = ROOT / "examples" / "fixture_manifest.json"
        manifest = load_manifest(path)

        report = build_maintenance_report(path, manifest, [])

        self.assertIn("# Asset Pipeline Steward Report", report)
        self.assertIn("Project: synthetic-review-demo", report)
        self.assertIn("- Assets: 1", report)
        self.assertIn("- review-smoke-gate", report)
        self.assertIn("- human-rating: ground-truth", report)
        self.assertIn("## Handoff", report)
        self.assertIn("- Goal: Validate the minimal public-safe review fixture.", report)

    def test_report_command_returns_zero_for_safe_manifest(self) -> None:
        path = ROOT / "examples" / "fixture_manifest.json"

        with redirect_stdout(StringIO()) as output:
            exit_code = main(["report", str(path)])

        self.assertEqual(0, exit_code)
        self.assertIn("Passed public-safety", output.getvalue())


if __name__ == "__main__":
    unittest.main()
