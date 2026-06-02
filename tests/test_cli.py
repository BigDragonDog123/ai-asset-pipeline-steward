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

from asset_pipeline_steward.cli import load_manifest, main, validate_manifest


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

    def test_cli_returns_nonzero_for_unsafe_manifest(self) -> None:
        manifest = load_manifest(ROOT / "examples" / "fixture_manifest.json")
        manifest["project"]["description"] = "contains token marker"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")

            with redirect_stdout(StringIO()):
                exit_code = main([str(path), "--json"])

        self.assertEqual(1, exit_code)


if __name__ == "__main__":
    unittest.main()
