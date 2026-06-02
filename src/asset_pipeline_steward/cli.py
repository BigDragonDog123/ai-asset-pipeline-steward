"""Validate public-safe AI asset pipeline manifests."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


REQUIRED_TOP_LEVEL_KEYS = (
    "project",
    "assets",
    "models",
    "workflows",
    "review_signals",
    "decision_gate",
)

PRIVATE_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:\\"),
    re.compile(r"(^|[\"' ])~[/\\]"),
    re.compile(r"/Users/"),
    re.compile(r"\\Users\\"),
    re.compile(r"/AppData/|\\AppData\\", re.IGNORECASE),
)

SENSITIVE_MARKERS = (
    ".env",
    "api_key",
    "apikey",
    "auth_token",
    "password",
    "private_key",
    "secret",
    "token",
)

MODEL_WEIGHT_EXTENSIONS = (
    ".safetensors",
    ".ckpt",
    ".pt",
    ".pth",
    ".onnx",
    ".bin",
)


@dataclass(frozen=True)
class Finding:
    severity: str
    path: str
    message: str
    value: str | None = None


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("manifest root must be a JSON object")
    return data


def validate_manifest(data: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []

    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in data:
            findings.append(
                Finding("blocker", key, "missing required top-level key")
            )

    project = data.get("project")
    if not isinstance(project, dict):
        findings.append(Finding("blocker", "project", "project must be an object"))
    else:
        for key in ("name", "description", "status"):
            value = project.get(key)
            if not isinstance(value, str) or not value.strip():
                findings.append(
                    Finding("blocker", f"project.{key}", "required project field is empty")
                )

    for key in ("assets", "models", "workflows", "review_signals"):
        value = data.get(key)
        if value is not None and not isinstance(value, list):
            findings.append(Finding("blocker", key, "field must be a list"))

    decision_gate = data.get("decision_gate")
    if decision_gate is not None and not isinstance(decision_gate, dict):
        findings.append(Finding("blocker", "decision_gate", "field must be an object"))

    findings.extend(scan_public_safety(data))
    return findings


def scan_public_safety(data: Any) -> Iterable[Finding]:
    for path, value in iter_strings(data):
        lowered = value.lower()

        for pattern in PRIVATE_PATH_PATTERNS:
            if pattern.search(value):
                yield Finding(
                    "blocker",
                    path,
                    "private or absolute local path is not public-safe",
                    value,
                )
                break

        for marker in SENSITIVE_MARKERS:
            if marker in lowered:
                yield Finding(
                    "blocker",
                    path,
                    f"sensitive marker '{marker}' is not public-safe",
                    value,
                )
                break

        if looks_like_model_file(lowered):
            yield Finding(
                "blocker",
                path,
                "model weight file paths should not be committed to the public repo",
                value,
            )


def iter_strings(value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, nested in value.items():
            yield from iter_strings(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            yield from iter_strings(nested, f"{path}[{index}]")


def looks_like_model_file(value: str) -> bool:
    return any(value.endswith(extension) for extension in MODEL_WEIGHT_EXTENSIONS)


def has_blockers(findings: Iterable[Finding]) -> bool:
    return any(finding.severity == "blocker" for finding in findings)


def format_human_report(path: Path, findings: list[Finding]) -> str:
    if not findings:
        return f"OK: {path} passed public-safety and schema checks."

    lines = [f"Findings for {path}:"]
    for finding in findings:
        suffix = f" | value={finding.value!r}" if finding.value else ""
        lines.append(
            f"- {finding.severity.upper()} {finding.path}: {finding.message}{suffix}"
        )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a public-safe AI asset pipeline manifest."
    )
    parser.add_argument("manifest", type=Path, help="Path to manifest JSON")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        manifest = load_manifest(args.manifest)
        findings = validate_manifest(manifest)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        findings = [Finding("blocker", "$", str(error))]

    if args.json:
        payload = {
            "manifest": str(args.manifest),
            "ok": not has_blockers(findings),
            "findings": [asdict(finding) for finding in findings],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(format_human_report(args.manifest, findings))

    return 1 if has_blockers(findings) else 0


if __name__ == "__main__":
    sys.exit(main())
