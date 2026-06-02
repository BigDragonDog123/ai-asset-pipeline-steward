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


def build_maintenance_report(
    path: Path, data: dict[str, Any], findings: list[Finding]
) -> str:
    project = data.get("project", {})
    assets = list_or_empty(data.get("assets"))
    models = list_or_empty(data.get("models"))
    workflows = list_or_empty(data.get("workflows"))
    review_signals = list_or_empty(data.get("review_signals"))
    decision_gate = (
        data.get("decision_gate") if isinstance(data.get("decision_gate"), dict) else {}
    )

    lines = [
        "# Asset Pipeline Steward Report",
        "",
        f"Manifest: `{path}`",
        f"Project: {safe_text(project.get('name'), 'unknown')}",
        f"Status: {safe_text(project.get('status'), 'unknown')}",
        "",
        "## Inventory",
        "",
        f"- Assets: {len(assets)}",
        f"- Models: {len(models)}",
        f"- Workflows: {len(workflows)}",
        f"- Review signals: {len(review_signals)}",
        "",
        "## Workflows",
        "",
    ]

    if workflows:
        for workflow in workflows:
            if isinstance(workflow, dict):
                name = safe_text(workflow.get("name"), "unnamed workflow")
                preflight = ", ".join(map(str, workflow.get("preflight", [])))
                suffix = f" | preflight: {preflight}" if preflight else ""
                lines.append(f"- {name}{suffix}")
            else:
                lines.append(f"- {workflow}")
    else:
        lines.append("- None declared")

    lines.extend(["", "## Review Signals", ""])
    if review_signals:
        for signal in review_signals:
            if isinstance(signal, dict):
                name = safe_text(signal.get("name"), "unnamed signal")
                role = safe_text(signal.get("role"), "unspecified role")
                lines.append(f"- {name}: {role}")
            else:
                lines.append(f"- {signal}")
    else:
        lines.append("- None declared")

    lines.extend(
        [
            "",
            "## Decision Gate",
            "",
            f"- Status: {safe_text(decision_gate.get('status'), 'unknown')}",
            f"- Next action: {safe_text(decision_gate.get('next_action'), 'not specified')}",
        ]
    )

    unknowns = decision_gate.get("known_unknowns")
    if isinstance(unknowns, list) and unknowns:
        lines.append("- Known unknowns:")
        lines.extend(f"  - {unknown}" for unknown in unknowns)
    else:
        lines.append("- Known unknowns: none declared")

    lines.extend(["", "## Validation", ""])
    if findings:
        for finding in findings:
            lines.append(
                f"- {finding.severity.upper()} {finding.path}: {finding.message}"
            )
    else:
        lines.append("- Passed public-safety and schema checks.")

    return "\n".join(lines)


def list_or_empty(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def safe_text(value: Any, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


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
    parser.add_argument("command_or_manifest", help="Manifest path, or command: validate/report")
    parser.add_argument("manifest", nargs="?", type=Path, help="Path to manifest JSON")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command, manifest_path = resolve_command(args.command_or_manifest, args.manifest)

    try:
        manifest = load_manifest(manifest_path)
        findings = validate_manifest(manifest)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        manifest = {}
        findings = [Finding("blocker", "$", str(error))]

    if command == "report":
        print(build_maintenance_report(manifest_path, manifest, findings))
    elif args.json:
        payload = {
            "manifest": str(manifest_path),
            "ok": not has_blockers(findings),
            "findings": [asdict(finding) for finding in findings],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(format_human_report(manifest_path, findings))

    return 1 if has_blockers(findings) else 0


def resolve_command(command_or_manifest: str, manifest: Path | None) -> tuple[str, Path]:
    if command_or_manifest in {"validate", "report"}:
        if manifest is None:
            raise SystemExit(f"{command_or_manifest} requires a manifest path")
        return command_or_manifest, manifest
    if manifest is not None:
        raise SystemExit("unexpected extra manifest path")
    return "validate", Path(command_or_manifest)


if __name__ == "__main__":
    sys.exit(main())
