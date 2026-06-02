"""Validate public-safe AI asset pipeline manifests."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
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
    "handoff",
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

REPO_EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    "htmlcov",
}

SENSITIVE_REPO_FILENAMES = {
    ".env",
    "id_ed25519",
    "id_rsa",
}

TEXT_FILE_EXTENSIONS = {
    "",
    ".cfg",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

COMMUNITY_HEALTH_FILES = (
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "AGENTS.md",
    "ROADMAP.md",
    "CHANGELOG.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/workflows/ci.yml",
    ".github/dependabot.yml",
)

EXAMPLE_MANIFESTS = (
    "examples/fixture_manifest.json",
    "examples/model_inventory_manifest.json",
    "examples/review_queue_manifest.json",
)

SCHEMA_FILE = "schemas/asset-pipeline-manifest.schema.json"
ADOPTION_EVIDENCE_FILE = "docs/adoption-evidence.json"

HIGH_CONFIDENCE_CONTENT_PATTERNS = (
    ("OpenAI-style API key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    (
        "secret assignment",
        re.compile(
            r"(?i)\b(api[_-]?key|auth[_-]?token|password|secret|token)\s*=\s*['\"]?[^'\"\s]{8,}"
        ),
    ),
    (
        "private Windows user path",
        re.compile(r"C:\\Users\\(?!example\b)[A-Za-z0-9_.-]+|C:/Users/(?!example\b)[A-Za-z0-9_.-]+"),
    ),
    (
        "private E drive path",
        re.compile(r"\b" + "E:" + r"\\[A-Za-z0-9_.-]|\b" + "E:" + r"/[A-Za-z0-9_.-]"),
    ),
)


SCHEMA_ID = (
    "https://raw.githubusercontent.com/BigDragonDog123/"
    "ai-asset-pipeline-steward/main/schemas/asset-pipeline-manifest.schema.json"
)


@dataclass(frozen=True)
class Finding:
    severity: str
    path: str
    message: str
    value: str | None = None


@dataclass(frozen=True)
class ReadinessCheck:
    status: str
    name: str
    message: str


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("manifest root must be a JSON object")
    return data


def build_manifest_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": SCHEMA_ID,
        "title": "AI Asset Pipeline Steward Manifest",
        "type": "object",
        "required": list(REQUIRED_TOP_LEVEL_KEYS),
        "properties": {
            "project": {
                "type": "object",
                "required": ["name", "description", "status"],
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "description": {"type": "string", "minLength": 1},
                    "status": {"type": "string", "minLength": 1},
                    "maintainer_intent": {"type": "string"},
                },
                "additionalProperties": True,
            },
            "assets": {
                "type": "array",
                "items": {"$ref": "#/$defs/asset"},
            },
            "models": {
                "type": "array",
                "items": {"$ref": "#/$defs/model"},
            },
            "workflows": {
                "type": "array",
                "items": {"$ref": "#/$defs/workflow"},
            },
            "review_signals": {
                "type": "array",
                "items": {"$ref": "#/$defs/review_signal"},
                "allOf": [
                    {
                        "contains": {
                            "type": "object",
                            "properties": {"role": {"const": "ground-truth"}},
                            "required": ["role"],
                        }
                    },
                    {
                        "contains": {
                            "type": "object",
                            "properties": {"role": {"const": "supporting-evidence"}},
                            "required": ["role"],
                        }
                    },
                ],
            },
            "decision_gate": {"$ref": "#/$defs/decision_gate"},
            "handoff": {"$ref": "#/$defs/handoff"},
        },
        "$defs": {
            "asset": {
                "type": "object",
                "required": ["id", "kind", "path", "source", "review_state"],
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "kind": {"type": "string", "minLength": 1},
                    "path": {"type": "string", "minLength": 1},
                    "source": {"type": "string", "minLength": 1},
                    "review_state": {"type": "string", "minLength": 1},
                },
                "additionalProperties": True,
            },
            "model": {
                "type": "object",
                "required": ["name", "source", "weights_included", "verification"],
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "source": {"type": "string", "minLength": 1},
                    "weights_included": {"type": "boolean"},
                    "verification": {"type": "string", "minLength": 1},
                },
                "additionalProperties": True,
            },
            "workflow": {
                "type": "object",
                "required": ["name", "steps", "preflight"],
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "steps": {
                        "type": "array",
                        "minItems": 1,
                        "items": {"type": "string", "minLength": 1},
                    },
                    "preflight": {
                        "type": "array",
                        "minItems": 1,
                        "items": {"type": "string", "minLength": 1},
                    },
                },
                "additionalProperties": True,
            },
            "review_signal": {
                "type": "object",
                "required": ["name", "role"],
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "role": {
                        "type": "string",
                        "enum": ["ground-truth", "supporting-evidence"],
                    },
                    "scale": {"type": "string"},
                },
                "additionalProperties": True,
            },
            "decision_gate": {
                "type": "object",
                "required": ["status", "next_action"],
                "properties": {
                    "status": {"type": "string", "minLength": 1},
                    "next_action": {"type": "string", "minLength": 1},
                    "known_unknowns": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "additionalProperties": True,
            },
            "handoff": {
                "type": "object",
                "required": [
                    "goal",
                    "current_status",
                    "next_action",
                    "blockers",
                    "known_unknowns",
                ],
                "properties": {
                    "goal": {"type": "string", "minLength": 1},
                    "current_status": {"type": "string", "minLength": 1},
                    "next_action": {"type": "string", "minLength": 1},
                    "blockers": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "known_unknowns": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "additionalProperties": True,
            },
        },
        "additionalProperties": True,
    }


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

    workflows = data.get("workflows")
    if isinstance(workflows, list):
        findings.extend(validate_workflows(workflows))

    review_signals = data.get("review_signals")
    if isinstance(review_signals, list):
        findings.extend(validate_review_signals(review_signals))

    decision_gate = data.get("decision_gate")
    if decision_gate is not None and not isinstance(decision_gate, dict):
        findings.append(Finding("blocker", "decision_gate", "field must be an object"))
    elif isinstance(decision_gate, dict):
        findings.extend(validate_decision_gate(decision_gate))

    handoff = data.get("handoff")
    if handoff is not None and not isinstance(handoff, dict):
        findings.append(Finding("blocker", "handoff", "field must be an object"))
    elif isinstance(handoff, dict):
        findings.extend(validate_handoff(handoff))

    findings.extend(scan_public_safety(data))
    return findings


def validate_workflows(workflows: list[Any]) -> Iterable[Finding]:
    for index, workflow in enumerate(workflows):
        path = f"workflows[{index}]"
        if not isinstance(workflow, dict):
            yield Finding("blocker", path, "workflow must be an object")
            continue

        name = workflow.get("name")
        if not isinstance(name, str) or not name.strip():
            yield Finding("blocker", f"{path}.name", "workflow name is required")

        steps = workflow.get("steps")
        if not isinstance(steps, list) or not steps:
            yield Finding("blocker", f"{path}.steps", "workflow steps must be a non-empty list")

        preflight = workflow.get("preflight")
        if not isinstance(preflight, list) or not preflight:
            yield Finding(
                "blocker",
                f"{path}.preflight",
                "workflow preflight must be a non-empty list",
            )


def validate_review_signals(review_signals: list[Any]) -> Iterable[Finding]:
    roles: set[str] = set()
    for index, signal in enumerate(review_signals):
        path = f"review_signals[{index}]"
        if not isinstance(signal, dict):
            yield Finding("blocker", path, "review signal must be an object")
            continue

        name = signal.get("name")
        role = signal.get("role")
        if not isinstance(name, str) or not name.strip():
            yield Finding("blocker", f"{path}.name", "review signal name is required")
        if not isinstance(role, str) or not role.strip():
            yield Finding("blocker", f"{path}.role", "review signal role is required")
        else:
            roles.add(role.strip())

    if review_signals and "ground-truth" not in roles:
        yield Finding(
            "blocker",
            "review_signals",
            "at least one review signal must have role 'ground-truth'",
        )
    if review_signals and "supporting-evidence" not in roles:
        yield Finding(
            "blocker",
            "review_signals",
            "at least one review signal must have role 'supporting-evidence'",
        )


def validate_decision_gate(decision_gate: dict[str, Any]) -> Iterable[Finding]:
    for key in ("status", "next_action"):
        value = decision_gate.get(key)
        if not isinstance(value, str) or not value.strip():
            yield Finding(
                "blocker",
                f"decision_gate.{key}",
                "decision gate field is required",
            )


def validate_handoff(handoff: dict[str, Any]) -> Iterable[Finding]:
    for key in ("goal", "current_status", "next_action"):
        value = handoff.get(key)
        if not isinstance(value, str) or not value.strip():
            yield Finding("blocker", f"handoff.{key}", "handoff field is required")

    for key in ("blockers", "known_unknowns"):
        value = handoff.get(key)
        if not isinstance(value, list):
            yield Finding("blocker", f"handoff.{key}", "handoff field must be a list")


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


def scan_repository(root: Path) -> list[Finding]:
    root = root.resolve()
    if not root.exists():
        return [Finding("blocker", str(root), "repo scan path does not exist")]

    findings: list[Finding] = []
    for path in iter_repo_files(root):
        rel_path = relative_display_path(root, path)
        lower_name = path.name.lower()

        if lower_name in SENSITIVE_REPO_FILENAMES or lower_name.startswith(".env."):
            findings.append(
                Finding("blocker", rel_path, "sensitive file name should not be public")
            )

        if path.suffix.lower() in MODEL_WEIGHT_EXTENSIONS:
            findings.append(
                Finding("blocker", rel_path, "model weight file should not be public")
            )

        content = read_text_for_scan(path)
        if content is None:
            continue

        for message, pattern in HIGH_CONFIDENCE_CONTENT_PATTERNS:
            match = pattern.search(content)
            if match:
                findings.append(
                    Finding("blocker", rel_path, f"{message} found in file content")
                )
                break

    return findings


def iter_repo_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        yield root
        return

    for path in root.rglob("*"):
        if path.is_dir() or should_skip_repo_path(path):
            continue
        yield path


def should_skip_repo_path(path: Path) -> bool:
    return any(
        part in REPO_EXCLUDED_DIRS or part.endswith(".egg-info") for part in path.parts
    )


def relative_display_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def read_text_for_scan(path: Path) -> str | None:
    if path.suffix.lower() not in TEXT_FILE_EXTENSIONS:
        return None
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) > 1_000_000 or b"\x00" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="ignore")


def format_repo_scan_report(root: Path, findings: list[Finding]) -> str:
    if not findings:
        return f"OK: repo scan passed high-confidence public-safety checks for {root}"

    lines = [f"Repo scan findings for {root}:"]
    for finding in findings:
        lines.append(f"- {finding.severity.upper()} {finding.path}: {finding.message}")
    return "\n".join(lines)


def build_readiness_checks(root: Path, check_git: bool = True) -> list[ReadinessCheck]:
    root = root.resolve()
    checks: list[ReadinessCheck] = []

    checks.extend(check_required_files(root))
    checks.extend(check_schema_file(root))
    checks.extend(check_example_manifests(root))
    checks.extend(check_repo_scan(root))
    checks.extend(check_adoption_evidence(root))
    if check_git:
        checks.extend(check_git_state(root))

    checks.append(
        ReadinessCheck(
            "warn",
            "public_repo",
            "public GitHub repository, CI run, release, and adoption evidence must be verified after push",
        )
    )
    return checks


def check_required_files(root: Path) -> list[ReadinessCheck]:
    checks: list[ReadinessCheck] = []
    for rel_path in COMMUNITY_HEALTH_FILES:
        path = root / rel_path
        if path.exists():
            checks.append(ReadinessCheck("pass", rel_path, "required file exists"))
        else:
            checks.append(ReadinessCheck("blocker", rel_path, "required file is missing"))
    return checks


def check_schema_file(root: Path) -> list[ReadinessCheck]:
    path = root / SCHEMA_FILE
    if not path.exists():
        return [ReadinessCheck("blocker", SCHEMA_FILE, "schema file is missing")]

    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [ReadinessCheck("blocker", SCHEMA_FILE, f"schema file is invalid: {error}")]

    if schema != build_manifest_schema():
        return [
            ReadinessCheck(
                "blocker",
                SCHEMA_FILE,
                "checked-in schema does not match CLI-generated schema",
            )
        ]
    return [ReadinessCheck("pass", SCHEMA_FILE, "schema matches CLI-generated schema")]


def check_example_manifests(root: Path) -> list[ReadinessCheck]:
    checks: list[ReadinessCheck] = []
    for rel_path in EXAMPLE_MANIFESTS:
        path = root / rel_path
        if not path.exists():
            checks.append(ReadinessCheck("blocker", rel_path, "example manifest is missing"))
            continue
        try:
            findings = validate_manifest(load_manifest(path))
        except (OSError, json.JSONDecodeError, ValueError) as error:
            checks.append(ReadinessCheck("blocker", rel_path, f"manifest load failed: {error}"))
            continue
        if findings:
            checks.append(
                ReadinessCheck(
                    "blocker",
                    rel_path,
                    f"manifest has {len(findings)} validation finding(s)",
                )
            )
        else:
            checks.append(ReadinessCheck("pass", rel_path, "example manifest validates"))
    return checks


def check_repo_scan(root: Path) -> list[ReadinessCheck]:
    findings = scan_repository(root)
    if findings:
        return [
            ReadinessCheck(
                "blocker",
                "repo-scan",
                f"repository scan has {len(findings)} public-safety finding(s)",
            )
        ]
    return [ReadinessCheck("pass", "repo-scan", "repository scan passes")]


def load_adoption_evidence(root: Path) -> tuple[dict[str, Any] | None, list[ReadinessCheck]]:
    path = root / ADOPTION_EVIDENCE_FILE
    if not path.exists():
        return None, [ReadinessCheck("blocker", ADOPTION_EVIDENCE_FILE, "adoption evidence file is missing")]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return None, [ReadinessCheck("blocker", ADOPTION_EVIDENCE_FILE, f"adoption evidence file is invalid: {error}")]
    if not isinstance(data, dict):
        return None, [ReadinessCheck("blocker", ADOPTION_EVIDENCE_FILE, "adoption evidence root must be an object")]
    return data, []


def check_adoption_evidence(root: Path) -> list[ReadinessCheck]:
    data, checks = load_adoption_evidence(root)
    if data is None:
        return checks

    checks.append(ReadinessCheck("pass", ADOPTION_EVIDENCE_FILE, "adoption evidence file exists"))

    repo_url = string_value(data.get("public_repository_url"))
    if "github.com" in repo_url:
        checks.append(ReadinessCheck("pass", "evidence.public_repository_url", repo_url))
    else:
        checks.append(ReadinessCheck("warn", "evidence.public_repository_url", "public GitHub URL is not recorded yet"))

    evidence_expectations = (
        ("release_urls", 1, "release URL"),
        ("ci_run_urls", 1, "GitHub CI run URL"),
        ("issue_urls", 3, "roadmap issue URL"),
        ("external_feedback_urls", 1, "external feedback URL"),
        ("usage_example_urls", 1, "usage example URL"),
    )
    for key, minimum, label in evidence_expectations:
        values = list_value(data.get(key))
        status = "pass" if len(values) >= minimum else "warn"
        checks.append(
            ReadinessCheck(
                status,
                f"evidence.{key}",
                f"{len(values)}/{minimum} {label}(s) recorded",
            )
        )

    stars = int_value(data.get("stars"))
    forks = int_value(data.get("forks"))
    checks.append(ReadinessCheck("pass" if stars > 0 else "warn", "evidence.stars", f"{stars} star(s) recorded"))
    checks.append(ReadinessCheck("pass" if forks > 0 else "warn", "evidence.forks", f"{forks} fork(s) recorded"))
    return checks


def string_value(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def int_value(value: Any) -> int:
    return value if isinstance(value, int) else 0


def check_git_state(root: Path) -> list[ReadinessCheck]:
    checks: list[ReadinessCheck] = []

    inside = run_git(root, ["rev-parse", "--is-inside-work-tree"])
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return [ReadinessCheck("blocker", "git", "not inside a git worktree")]
    checks.append(ReadinessCheck("pass", "git", "inside a git worktree"))

    branch = run_git(root, ["branch", "--show-current"])
    if branch.returncode == 0 and branch.stdout.strip() == "main":
        checks.append(ReadinessCheck("pass", "git.branch", "current branch is main"))
    else:
        checks.append(
            ReadinessCheck(
                "warn",
                "git.branch",
                f"current branch is {branch.stdout.strip() or 'unknown'}, expected main",
            )
        )

    status = run_git(root, ["status", "--porcelain"])
    if status.returncode == 0 and not status.stdout.strip():
        checks.append(ReadinessCheck("pass", "git.status", "worktree is clean"))
    else:
        checks.append(ReadinessCheck("blocker", "git.status", "worktree has uncommitted changes"))

    remote = run_git(root, ["remote", "get-url", "origin"])
    remote_url = remote.stdout.strip()
    if remote.returncode == 0 and "github.com" in remote_url:
        checks.append(ReadinessCheck("pass", "git.remote", f"origin is configured: {remote_url}"))
    elif remote.returncode == 0 and remote_url:
        checks.append(ReadinessCheck("warn", "git.remote", f"origin is not GitHub: {remote_url}"))
    else:
        checks.append(ReadinessCheck("blocker", "git.remote", "origin remote is missing"))

    return checks


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return subprocess.CompletedProcess(args=["git", *args], returncode=1, stderr=str(error))


def has_readiness_blockers(checks: Iterable[ReadinessCheck]) -> bool:
    return any(check.status == "blocker" for check in checks)


def format_readiness_report(checks: list[ReadinessCheck]) -> str:
    lines = ["# Codex For OSS Local Readiness"]
    for check in checks:
        lines.append(f"- {check.status.upper()} {check.name}: {check.message}")
    return "\n".join(lines)


def build_evidence_report(root: Path) -> tuple[list[ReadinessCheck], str]:
    checks = check_adoption_evidence(root.resolve())
    lines = ["# Adoption Evidence"]
    for check in checks:
        lines.append(f"- {check.status.upper()} {check.name}: {check.message}")
    return checks, "\n".join(lines)


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
    handoff = data.get("handoff") if isinstance(data.get("handoff"), dict) else {}

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

    lines.extend(["", "## Handoff", ""])
    lines.extend(
        [
            f"- Goal: {safe_text(handoff.get('goal'), 'unknown')}",
            f"- Current status: {safe_text(handoff.get('current_status'), 'unknown')}",
            f"- Next action: {safe_text(handoff.get('next_action'), 'not specified')}",
        ]
    )
    lines.extend(format_named_list("Blockers", handoff.get("blockers")))
    lines.extend(format_named_list("Known unknowns", handoff.get("known_unknowns")))

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


def format_named_list(label: str, value: Any) -> list[str]:
    if isinstance(value, list) and value:
        return [f"- {label}:"] + [f"  - {item}" for item in value]
    return [f"- {label}: none declared"]


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
    parser.add_argument(
        "command_or_manifest",
        help="Manifest path, or command: validate/report/schema/repo-scan/readiness/evidence",
    )
    parser.add_argument("manifest", nargs="?", type=Path, help="Path to manifest JSON")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command, manifest_path = resolve_command(args.command_or_manifest, args.manifest)

    if command == "schema":
        print(json.dumps(build_manifest_schema(), indent=2, sort_keys=True))
        return 0

    if command == "repo-scan":
        scan_root = manifest_path or Path(".")
        findings = scan_repository(scan_root)
        if args.json:
            payload = {
                "root": str(scan_root),
                "ok": not has_blockers(findings),
                "findings": [asdict(finding) for finding in findings],
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(format_repo_scan_report(scan_root, findings))
        return 1 if has_blockers(findings) else 0

    if command == "readiness":
        root = manifest_path or Path(".")
        checks = build_readiness_checks(root)
        if args.json:
            payload = {
                "root": str(root),
                "ok": not has_readiness_blockers(checks),
                "checks": [asdict(check) for check in checks],
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(format_readiness_report(checks))
        return 1 if has_readiness_blockers(checks) else 0

    if command == "evidence":
        root = manifest_path or Path(".")
        checks, report = build_evidence_report(root)
        if args.json:
            payload = {
                "root": str(root),
                "ok": not has_readiness_blockers(checks),
                "checks": [asdict(check) for check in checks],
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(report)
        return 1 if has_readiness_blockers(checks) else 0

    try:
        if manifest_path is None:
            raise ValueError("manifest path is required")
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


def resolve_command(
    command_or_manifest: str, manifest: Path | None
) -> tuple[str, Path | None]:
    if command_or_manifest == "schema":
        if manifest is not None:
            raise SystemExit("schema does not accept a manifest path")
        return command_or_manifest, None
    if command_or_manifest == "repo-scan":
        return command_or_manifest, manifest or Path(".")
    if command_or_manifest == "readiness":
        return command_or_manifest, manifest or Path(".")
    if command_or_manifest == "evidence":
        return command_or_manifest, manifest or Path(".")
    if command_or_manifest in {"validate", "report"}:
        if manifest is None:
            raise SystemExit(f"{command_or_manifest} requires a manifest path")
        return command_or_manifest, manifest
    if manifest is not None:
        raise SystemExit("unexpected extra manifest path")
    return "validate", Path(command_or_manifest)


if __name__ == "__main__":
    sys.exit(main())
