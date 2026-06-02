"""Validate public-safe AI asset pipeline manifests."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


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
    ".ps1",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

COMMUNITY_HEALTH_FILES = (
    "README.md",
    "REVIEW.md",
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
    ".github/ISSUE_TEMPLATE/feedback.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/workflows/ci.yml",
    ".github/dependabot.yml",
)

EXAMPLE_MANIFESTS = (
    "examples/fixture_manifest.json",
    "examples/model_inventory_manifest.json",
    "examples/review_queue_manifest.json",
    "examples/handoff_resume_manifest.json",
    "examples/end_to_end_maintainer_loop_manifest.json",
)

SCHEMA_FILE = "schemas/asset-pipeline-manifest.schema.json"
ADOPTION_EVIDENCE_FILE = "docs/adoption-evidence.json"
STARTER_ISSUES_FILE = "docs/starter-issues.json"
APPLICATION_FILE = "docs/codex-for-oss-application.json"
DEFAULT_PUBLIC_REPOSITORY = "BigDragonDog123/ai-asset-pipeline-steward"

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


def load_application_packet(root: Path) -> tuple[dict[str, Any] | None, list[Finding]]:
    path = root / APPLICATION_FILE
    if not path.exists():
        return None, [Finding("blocker", APPLICATION_FILE, "application packet is missing")]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return None, [
            Finding("blocker", APPLICATION_FILE, f"application packet is invalid: {error}")
        ]
    if not isinstance(data, dict):
        return None, [Finding("blocker", APPLICATION_FILE, "application packet root must be an object")]

    findings: list[Finding] = []
    fields = data.get("fields")
    limited_answers = data.get("limited_answers")
    if not isinstance(fields, list):
        findings.append(Finding("blocker", f"{APPLICATION_FILE}.fields", "fields must be a list"))
    if not isinstance(limited_answers, list):
        findings.append(
            Finding(
                "blocker",
                f"{APPLICATION_FILE}.limited_answers",
                "limited_answers must be a list",
            )
        )

    if isinstance(fields, list):
        for index, field in enumerate(fields):
            prefix = f"{APPLICATION_FILE}.fields[{index}]"
            if not isinstance(field, dict):
                findings.append(Finding("blocker", prefix, "field must be an object"))
                continue
            for key in ("label", "value"):
                if not isinstance(field.get(key), str) or not field.get(key, "").strip():
                    findings.append(Finding("blocker", f"{prefix}.{key}", "field value is required"))

    if isinstance(limited_answers, list):
        for index, answer in enumerate(limited_answers):
            prefix = f"{APPLICATION_FILE}.limited_answers[{index}]"
            if not isinstance(answer, dict):
                findings.append(Finding("blocker", prefix, "limited answer must be an object"))
                continue
            title = answer.get("title")
            value = answer.get("value")
            max_chars = answer.get("max_chars")
            if not isinstance(title, str) or not title.strip():
                findings.append(Finding("blocker", f"{prefix}.title", "answer title is required"))
            if not isinstance(value, str) or not value.strip():
                findings.append(Finding("blocker", f"{prefix}.value", "answer value is required"))
            if not isinstance(max_chars, int) or max_chars <= 0:
                findings.append(Finding("blocker", f"{prefix}.max_chars", "max_chars must be positive"))
            elif isinstance(value, str) and len(value) > max_chars:
                findings.append(
                    Finding(
                        "blocker",
                        f"{prefix}.value",
                        f"answer is {len(value)}/{max_chars} characters",
                    )
                )

    return data, findings


def format_application_report(
    packet: dict[str, Any] | None,
    findings: list[Finding],
    evidence_checks: list[ReadinessCheck],
) -> str:
    if packet is None:
        lines = ["# Codex For OSS Application Packet"]
        for finding in findings:
            lines.append(f"- {finding.severity.upper()} {finding.path}: {finding.message}")
        return "\n".join(lines)

    lines = [
        "# Codex For OSS Application Packet",
        "",
        f"Status date: {safe_text(packet.get('status_date'), 'unknown')}",
        "",
        "## Submission Gate",
        "",
    ]

    for finding in findings:
        lines.append(f"- {finding.severity.upper()} {finding.path}: {finding.message}")
    for check in evidence_checks:
        if check.status != "pass":
            lines.append(f"- {check.status.upper()} {check.name}: {check.message}")
    if not findings and all(check.status == "pass" for check in evidence_checks):
        lines.append("- PASS evidence: public evidence fields are populated")

    lines.extend(["", "## Form Fields", ""])
    for field in list_value(packet.get("fields")):
        if isinstance(field, dict):
            label = safe_text(field.get("label"), "unknown")
            value = safe_text(field.get("value"), "Fill manually")
            lines.append(f"- {label}: {value}")

    manual_fields = list_value(packet.get("manual_fields"))
    if manual_fields:
        lines.extend(["", "## Manual Fields", ""])
        for field in manual_fields:
            lines.append(f"- {field}")

    lines.extend(["", "## Limited Answers", ""])
    for answer in list_value(packet.get("limited_answers")):
        if not isinstance(answer, dict):
            continue
        title = safe_text(answer.get("title"), "unknown")
        value = safe_text(answer.get("value"), "")
        max_chars = int_value(answer.get("max_chars"))
        lines.extend(
            [
                f"### {title} ({len(value)}/{max_chars})",
                "",
                "```text",
                value,
                "```",
                "",
            ]
        )

    requirements = list_value(packet.get("do_not_submit_until"))
    if requirements:
        lines.extend(["## Do Not Submit Until", ""])
        for requirement in requirements:
            lines.append(f"- {requirement}")

    return "\n".join(lines).rstrip()


def build_submission_checks(
    root: Path,
    manual_ready: bool = False,
    check_git: bool = True,
) -> list[ReadinessCheck]:
    checks = build_readiness_checks(root, check_git=check_git)
    submission_checks: list[ReadinessCheck] = []

    for check in checks:
        if check.name == "evidence.external_feedback_urls" and check.status != "pass":
            submission_checks.append(
                ReadinessCheck(
                    "blocker",
                    check.name,
                    "at least one real public external feedback URL is required before submission",
                )
            )
        else:
            submission_checks.append(check)

    packet, findings = load_application_packet(root)
    if findings:
        for finding in findings:
            submission_checks.append(
                ReadinessCheck(
                    "blocker",
                    finding.path,
                    finding.message,
                )
            )
    else:
        submission_checks.append(
            ReadinessCheck("pass", APPLICATION_FILE, "application packet is valid")
        )

    manual_fields = list_value(packet.get("manual_fields")) if packet else []
    if manual_fields:
        if manual_ready:
            submission_checks.append(
                ReadinessCheck(
                    "pass",
                    "application.manual_fields",
                    "manual personal fields are confirmed for official form entry only",
                )
            )
        else:
            submission_checks.append(
                ReadinessCheck(
                    "blocker",
                    "application.manual_fields",
                    (
                        "manual personal fields are not confirmed; use --manual-ready "
                        "only after first name, last name, ChatGPT email, and OpenAI "
                        "Organization ID are ready for the official form"
                    ),
                )
            )

    return submission_checks


def format_submission_report(checks: list[ReadinessCheck]) -> str:
    lines = ["# Codex For OSS Submission Gate"]
    for check in checks:
        lines.append(f"- {check.status.upper()} {check.name}: {check.message}")
    if has_readiness_blockers(checks):
        lines.extend(
            [
                "",
                "Result: NOT READY to submit.",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "Result: READY for manual official-form submission.",
                "Do not commit personal form values to this repository.",
            ]
        )
    return "\n".join(lines)


def build_codex_oss_status(root: Path, manual_ready: bool = False) -> dict[str, Any]:
    root = root.resolve()
    evidence, evidence_file_checks = load_adoption_evidence(root)
    readiness_checks = build_readiness_checks(root)
    submission_checks = build_submission_checks(root, manual_ready=manual_ready)

    evidence = evidence or {}
    external_feedback_urls = list_value(evidence.get("external_feedback_urls"))
    blockers = [
        {"name": check.name, "message": check.message}
        for check in submission_checks
        if check.status == "blocker"
    ]
    warnings = [
        {"name": check.name, "message": check.message}
        for check in submission_checks
        if check.status == "warn"
    ]
    recommendation = "ready_for_manual_submission" if not blockers else "growth_mode"

    if not external_feedback_urls:
        next_actions = [
            "Send the short request from docs/first-feedback-playbook.md to one real reviewer.",
            "Ask for a public issue, public comment, forum post, or other reviewer-accessible URL.",
            "Run asset-pipeline-steward feedback-candidates . and record real feedback with asset-pipeline-steward record-feedback <public-feedback-url>.",
            "Use asset-pipeline-steward feedback-response-playbook . to make one visible maintainer response, then rerun asset-pipeline-steward submission-ready . --manual-ready.",
        ]
    elif blockers:
        next_actions = [
            "Resolve the listed submission blockers.",
            "Rerun asset-pipeline-steward readiness . and asset-pipeline-steward submission-ready . --manual-ready.",
        ]
    else:
        next_actions = [
            "Open the official Codex for Open Source form.",
            "Fill personal fields manually; do not commit them to the repository.",
            "Submit only after confirming the latest GitHub Actions run on main is green.",
        ]

    return {
        "official_program": {
            "timing": "rolling_review",
            "fixed_public_deadline_observed": False,
            "source_urls": [
                "https://developers.openai.com/community/codex-for-oss",
                "https://openai.com/form/codex-for-oss/",
            ],
        },
        "repository_url": string_value(evidence.get("public_repository_url"))
        or f"https://github.com/{DEFAULT_PUBLIC_REPOSITORY}",
        "recommendation": recommendation,
        "manual_ready": manual_ready,
        "readiness_ok": not has_readiness_blockers(readiness_checks),
        "submission_ready": not has_readiness_blockers(submission_checks),
        "evidence_file_ok": not has_readiness_blockers(evidence_file_checks),
        "evidence_counts": {
            "external_feedback_urls": len(external_feedback_urls),
            "release_urls": len(list_value(evidence.get("release_urls"))),
            "ci_run_urls": len(list_value(evidence.get("ci_run_urls"))),
            "issue_urls": len(list_value(evidence.get("issue_urls"))),
            "pull_request_urls": len(list_value(evidence.get("pull_request_urls"))),
            "usage_example_urls": len(list_value(evidence.get("usage_example_urls"))),
            "stars": int_value(evidence.get("stars")),
            "forks": int_value(evidence.get("forks")),
        },
        "blockers": blockers,
        "warnings": warnings,
        "next_actions": next_actions,
    }


def format_codex_oss_status(status: dict[str, Any]) -> str:
    recommendation = string_value(status.get("recommendation"))
    recommendation_label = (
        "READY FOR MANUAL SUBMISSION"
        if recommendation == "ready_for_manual_submission"
        else "GROWTH MODE"
    )
    counts = status.get("evidence_counts")
    counts = counts if isinstance(counts, dict) else {}
    lines = [
        "# Codex For OSS Status",
        "",
        f"Decision: {recommendation_label}",
        f"Repository: {status['repository_url']}",
        "Official timing: rolling review; no fixed public deadline recorded in the verified program snapshot.",
        "",
        "## Evidence Counts",
        "",
        f"- External feedback URLs: {counts.get('external_feedback_urls', 0)}",
        f"- Release URLs: {counts.get('release_urls', 0)}",
        f"- CI run URLs: {counts.get('ci_run_urls', 0)}",
        f"- Issue URLs: {counts.get('issue_urls', 0)}",
        f"- Pull request URLs: {counts.get('pull_request_urls', 0)}",
        f"- Usage example URLs: {counts.get('usage_example_urls', 0)}",
        f"- Stars: {counts.get('stars', 0)}",
        f"- Forks: {counts.get('forks', 0)}",
        "",
        "## Blockers",
        "",
    ]
    blockers = list_or_empty(status.get("blockers"))
    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker['name']}: {blocker['message']}")
    else:
        lines.append("- none")

    lines.extend(["", "## Warnings", ""])
    warnings = list_or_empty(status.get("warnings"))
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning['name']}: {warning['message']}")
    else:
        lines.append("- none")

    lines.extend(["", "## Next Actions", ""])
    for action in list_or_empty(status.get("next_actions")):
        lines.append(f"- {action}")

    return "\n".join(lines)


def build_next_human_action(root: Path, manual_ready: bool = False) -> dict[str, Any]:
    root = root.resolve()
    status = build_codex_oss_status(root, manual_ready=manual_ready)
    counts = status.get("evidence_counts")
    counts = counts if isinstance(counts, dict) else {}
    external_feedback_count = int_value(counts.get("external_feedback_urls"))
    repo_url = string_value(status.get("repository_url")) or public_repository_url(root)

    if external_feedback_count == 0:
        reviewer_request = build_reviewer_request(root)
        phase = "collect_external_feedback"
        primary_action = (
            "Send the reviewer request to one real non-maintainer reviewer and ask "
            "for one public feedback issue or comment."
        )
        why = (
            "The final submission gate is still blocked until at least one public, "
            "non-maintainer feedback URL is recorded."
        )
        manual_steps = [
            "Run asset-pipeline-steward reviewer-request .",
            "Copy the Chinese Short DM or English Short DM to one real reviewer.",
            "Ask for one concrete blocker, unclear field, missing validation rule, or fit concern.",
            "Ask the reviewer to use the public feedback form and avoid private paths, logs, credentials, model files, and non-public media.",
            "After feedback appears, run asset-pipeline-steward feedback-candidates .",
            "Record only reviewed public-safe feedback with asset-pipeline-steward record-feedback <public-feedback-url>.",
        ]
        commands = [
            "asset-pipeline-steward reviewer-request .",
            "asset-pipeline-steward feedback-candidates .",
            "asset-pipeline-steward record-feedback <public-feedback-url>",
            "asset-pipeline-steward feedback-response-playbook .",
            "asset-pipeline-steward submission-ready . --manual-ready",
        ]
        do_not = [
            "Do not submit the official Codex for OSS form yet.",
            "Do not record maintainer-authored comments as external feedback.",
            "Do not paste private DMs, screenshots, logs, credentials, or contact details into the repository.",
        ]
        copy_message = reviewer_request["chinese_short_dm"]
    elif status["recommendation"] != "ready_for_manual_submission":
        phase = "clear_submission_blockers"
        primary_action = "Resolve the remaining submission blockers before opening the official form."
        why = "External feedback exists, but at least one readiness or manual-field blocker remains."
        manual_steps = [
            "Review the blockers printed by asset-pipeline-steward codex-oss-status . --manual-ready.",
            "Turn the feedback into one visible maintainer response with asset-pipeline-steward feedback-response-playbook .",
            "Rerun readiness and submission-ready after the response is shipped.",
        ]
        commands = [
            "asset-pipeline-steward feedback-response-playbook .",
            "asset-pipeline-steward readiness .",
            "asset-pipeline-steward codex-oss-status . --manual-ready",
            "asset-pipeline-steward submission-ready . --manual-ready",
        ]
        do_not = [
            "Do not submit while blockers remain.",
            "Do not commit personal form fields or confirmation emails.",
        ]
        copy_message = ""
    else:
        phase = "ready_for_manual_submission"
        primary_action = "Verify latest CI, then fill the official form manually."
        why = "The local submission gate is clear; final personal fields still belong only in the official form."
        manual_steps = [
            "Run asset-pipeline-steward latest-ci . and confirm the latest main run is successful.",
            "Open the official Codex for OSS form.",
            "Fill first name, last name, ChatGPT email, and OpenAI Organization ID manually.",
            "Submit only after reviewing the public evidence packet one last time.",
        ]
        commands = [
            "asset-pipeline-steward latest-ci .",
            "asset-pipeline-steward submission-ready . --manual-ready",
            "asset-pipeline-steward application .",
        ]
        do_not = [
            "Do not commit personal form fields, Organization ID, or application confirmation emails.",
        ]
        copy_message = ""

    return {
        "repository_url": repo_url,
        "phase": phase,
        "primary_action": primary_action,
        "why": why,
        "evidence_counts": counts,
        "blockers": list_or_empty(status.get("blockers")),
        "manual_steps": manual_steps,
        "copy_message": copy_message,
        "commands": commands,
        "links": {
            "review_landing": public_blob_url(root, "REVIEW.md"),
            "reviewer_request_pack": public_blob_url(root, "docs/reviewer-request-pack.md"),
            "feedback_form": f"{repo_url}/issues/new?template=feedback.yml",
            "feedback_issue": f"{repo_url}/issues/8",
            "submission_runbook": public_blob_url(root, "docs/codex-for-oss-submission-runbook.md"),
        },
        "do_not": do_not,
    }


def format_next_human_action(action: dict[str, Any]) -> str:
    counts = action.get("evidence_counts")
    counts = counts if isinstance(counts, dict) else {}
    lines = [
        "# Next Human Action",
        "",
        f"Repository: {action['repository_url']}",
        f"Phase: {action['phase']}",
        "",
        "## Primary Action",
        "",
        str(action["primary_action"]),
        "",
        "## Why",
        "",
        str(action["why"]),
        "",
        "## Evidence Counts",
        "",
        f"- External feedback URLs: {counts.get('external_feedback_urls', 0)}",
        f"- Stars: {counts.get('stars', 0)}",
        f"- Forks: {counts.get('forks', 0)}",
        "",
        "## Manual Steps",
        "",
    ]
    for index, step in enumerate(list_or_empty(action.get("manual_steps")), start=1):
        lines.append(f"{index}. {step}")

    copy_message = string_value(action.get("copy_message"))
    if copy_message:
        lines.extend(["", "## Copy This Message", "", "```text", copy_message, "```"])

    lines.extend(["", "## Commands", "", "```bash"])
    lines.extend(list_or_empty(action.get("commands")))
    lines.extend(["```", "", "## Links", ""])
    for label, url in action["links"].items():
        lines.append(f"- {label}: {url}")

    lines.extend(["", "## Do Not", ""])
    for item in list_or_empty(action.get("do_not")):
        lines.append(f"- {item}")

    blockers = list_or_empty(action.get("blockers"))
    if blockers:
        lines.extend(["", "## Current Blockers", ""])
        for blocker in blockers:
            lines.append(f"- {blocker['name']}: {blocker['message']}")

    return "\n".join(lines)


def infer_public_repository(root: Path) -> str:
    data, _checks = load_adoption_evidence(root)
    repo_url = string_value(data.get("public_repository_url")) if data else ""
    match = re.search(r"github\.com/([^/\s]+)/([^/\s#?]+)", repo_url)
    if match:
        return f"{match.group(1)}/{match.group(2).removesuffix('.git')}"
    return DEFAULT_PUBLIC_REPOSITORY


def fetch_github_json(url: str) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai-asset-pipeline-steward",
    }
    github_access_value = os.getenv("GITHUB_TOKEN")
    if github_access_value:
        headers["Authorization"] = f"Bearer {github_access_value}"
    request = Request(
        url,
        headers=headers,
    )
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def github_api_error_message(scope: str, error: HTTPError) -> str:
    message = f"{scope} failed: HTTP {error.code}"
    if error.code in {403, 429}:
        message += (
            "; GitHub may be rate-limiting unauthenticated requests. "
            "Set GITHUB_TOKEN to a token with public repository read access and rerun."
        )
    return message


def collect_public_evidence(
    root: Path,
    fetcher: Any = fetch_github_json,
) -> tuple[dict[str, Any], list[Finding]]:
    repository = infer_public_repository(root)
    api_root = f"https://api.github.com/repos/{repository}"
    findings: list[Finding] = []

    try:
        repo = fetcher(api_root)
    except HTTPError as error:
        return {}, [
            Finding(
                "blocker",
                repository,
                github_api_error_message("GitHub repository API", error),
            )
        ]
    except (OSError, URLError, json.JSONDecodeError) as error:
        return {}, [
            Finding("blocker", repository, f"GitHub repository API failed: {error}")
        ]

    if not isinstance(repo, dict):
        return {}, [
            Finding("blocker", repository, "GitHub repository response was not an object")
        ]

    evidence: dict[str, Any] = {
        "status_date": dt.date.today().isoformat(),
        "public_repository_url": string_value(repo.get("html_url")),
        "ci_run_urls": [],
        "release_urls": [],
        "issue_urls": [],
        "pull_request_urls": [],
        "external_feedback_urls": [],
        "usage_example_urls": [],
        "stars": int_value(repo.get("stargazers_count")),
        "forks": int_value(repo.get("forks_count")),
        "notes": [
            "Generated from public GitHub API data.",
            "Review before copying into docs/adoption-evidence.json.",
            "Add external feedback and usage examples manually when available.",
        ],
    }

    optional_endpoints = (
        (
            "actions/runs?per_page=5",
            "workflow_runs",
            "ci_run_urls",
            extract_workflow_run_urls,
        ),
        ("releases?per_page=5", None, "release_urls", extract_html_urls),
        ("issues?state=all&per_page=20", None, "issue_urls", extract_issue_urls),
        (
            "issues?state=all&per_page=20",
            None,
            "pull_request_urls",
            extract_pull_request_urls,
        ),
    )
    cache: dict[str, Any] = {}
    for endpoint, root_key, evidence_key, extractor in optional_endpoints:
        url = f"{api_root}/{endpoint}"
        try:
            if endpoint not in cache:
                cache[endpoint] = fetcher(url)
            payload = cache[endpoint]
            if root_key and isinstance(payload, dict):
                payload = payload.get(root_key, [])
            evidence[evidence_key] = extractor(payload)
        except HTTPError as error:
            findings.append(
                Finding("warn", endpoint, github_api_error_message("GitHub API", error))
            )
        except (OSError, URLError, json.JSONDecodeError) as error:
            findings.append(Finding("warn", endpoint, f"GitHub API failed: {error}"))

    return evidence, findings


def check_latest_main_ci(
    root: Path,
    fetcher: Any | None = None,
) -> tuple[dict[str, Any], list[Finding]]:
    fetcher = fetcher or fetch_github_json
    repository = infer_public_repository(root)
    api_root = f"https://api.github.com/repos/{repository}"
    findings: list[Finding] = []

    try:
        repo = fetcher(api_root)
    except HTTPError as error:
        return {}, [
            Finding(
                "blocker",
                repository,
                github_api_error_message("GitHub repository API", error),
            )
        ]
    except (OSError, URLError, json.JSONDecodeError) as error:
        return {}, [
            Finding("blocker", repository, f"GitHub repository API failed: {error}")
        ]

    if not isinstance(repo, dict):
        return {}, [
            Finding("blocker", repository, "GitHub repository response was not an object")
        ]

    branch = string_value(repo.get("default_branch")) or "main"
    result: dict[str, Any] = {
        "repository": repository,
        "repository_url": string_value(repo.get("html_url")),
        "branch": branch,
        "head_sha": "",
        "head_url": "",
        "workflow_run_url": "",
        "workflow_name": "",
        "status": "",
        "conclusion": "",
    }

    try:
        commit = fetcher(f"{api_root}/commits/{branch}")
    except HTTPError as error:
        return result, [
            Finding("blocker", "latest-ci.commit", github_api_error_message("GitHub commit API", error))
        ]
    except (OSError, URLError, json.JSONDecodeError) as error:
        return result, [
            Finding("blocker", "latest-ci.commit", f"GitHub commit API failed: {error}")
        ]

    if not isinstance(commit, dict):
        return result, [
            Finding("blocker", "latest-ci.commit", "GitHub commit response was not an object")
        ]

    head_sha = string_value(commit.get("sha"))
    result["head_sha"] = head_sha
    result["head_url"] = string_value(commit.get("html_url"))
    if not head_sha:
        return result, [
            Finding("blocker", "latest-ci.commit", "latest branch commit SHA is missing")
        ]

    try:
        runs_payload = fetcher(
            f"{api_root}/actions/runs?branch={branch}&event=push&per_page=10"
        )
    except HTTPError as error:
        return result, [
            Finding("blocker", "latest-ci.runs", github_api_error_message("GitHub Actions API", error))
        ]
    except (OSError, URLError, json.JSONDecodeError) as error:
        return result, [
            Finding("blocker", "latest-ci.runs", f"GitHub Actions API failed: {error}")
        ]

    workflow_runs: list[Any] = []
    if isinstance(runs_payload, dict):
        workflow_runs = list_or_empty(runs_payload.get("workflow_runs"))
    if not workflow_runs:
        return result, [
            Finding("blocker", "latest-ci.runs", "no GitHub Actions push runs found")
        ]

    matching_run = next(
        (
            run
            for run in workflow_runs
            if isinstance(run, dict) and string_value(run.get("head_sha")) == head_sha
        ),
        None,
    )
    if not isinstance(matching_run, dict):
        return result, [
            Finding(
                "blocker",
                "latest-ci.runs",
                "no GitHub Actions push run found for the latest branch commit",
                head_sha,
            )
        ]

    result.update(
        {
            "workflow_run_url": string_value(matching_run.get("html_url")),
            "workflow_name": string_value(matching_run.get("name")),
            "status": string_value(matching_run.get("status")),
            "conclusion": string_value(matching_run.get("conclusion")),
        }
    )

    if result["status"] != "completed":
        findings.append(
            Finding(
                "blocker",
                "latest-ci.status",
                "latest branch workflow run is not completed",
                result["status"],
            )
        )
    elif result["conclusion"] != "success":
        findings.append(
            Finding(
                "blocker",
                "latest-ci.conclusion",
                "latest branch workflow run did not succeed",
                result["conclusion"],
            )
        )

    return result, findings


def format_latest_ci_report(status: dict[str, Any], findings: list[Finding]) -> str:
    lines = ["# Latest Main CI", ""]
    if status:
        lines.extend(
            [
                f"- Repository: {status.get('repository', '')}",
                f"- Branch: {status.get('branch', '')}",
                f"- Head SHA: {status.get('head_sha', '')}",
                f"- Head URL: {status.get('head_url', '')}",
                f"- Workflow: {status.get('workflow_name', '')}",
                f"- Workflow run: {status.get('workflow_run_url', '')}",
                f"- Status: {status.get('status', '')}",
                f"- Conclusion: {status.get('conclusion', '')}",
                "",
            ]
        )
    for finding in findings:
        lines.append(f"- {finding.severity.upper()} {finding.path}: {finding.message}")
    if not findings:
        lines.append("Result: PASS latest main GitHub Actions run is green.")
    else:
        lines.append("Result: NOT READY until latest main GitHub Actions run is green.")
    return "\n".join(lines)


def unique_string_values(*groups: Any) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for item in list_value(group):
            if not isinstance(item, str):
                continue
            value = item.strip()
            if value and value not in seen:
                values.append(value)
                seen.add(value)
    return values


def merge_public_evidence(
    existing: dict[str, Any], collected: dict[str, Any]
) -> dict[str, Any]:
    merged = dict(existing)
    for key in ("public_repository_url", "status_date"):
        value = string_value(collected.get(key))
        if value:
            merged[key] = value
    for key in ("stars", "forks"):
        if isinstance(collected.get(key), int):
            merged[key] = collected[key]
    for key in ("ci_run_urls", "release_urls", "issue_urls", "pull_request_urls"):
        merged[key] = unique_string_values(collected.get(key), existing.get(key))
    for key in ("external_feedback_urls", "usage_example_urls", "notes"):
        merged[key] = unique_string_values(existing.get(key), collected.get(key))
    return merged


def validate_external_feedback_url(feedback_url: str) -> list[Finding]:
    findings: list[Finding] = []
    parsed = urlparse(feedback_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return [
            Finding(
                "blocker",
                "external_feedback_url",
                "feedback URL must be an absolute http(s) URL",
                feedback_url,
            )
        ]

    host = parsed.netloc.lower()
    if host in {"localhost", "127.0.0.1"} or host.startswith("127."):
        findings.append(
            Finding("blocker", "external_feedback_url", "feedback URL is not public", feedback_url)
        )
    if "private-user-images.githubusercontent.com" in host:
        findings.append(
            Finding(
                "blocker",
                "external_feedback_url",
                "private GitHub attachment URLs are not public evidence",
                feedback_url,
            )
        )
    if any(pattern.search(feedback_url) for pattern in PRIVATE_PATH_PATTERNS):
        findings.append(
            Finding(
                "blocker",
                "external_feedback_url",
                "feedback URL appears to contain a private local path",
                feedback_url,
            )
        )
    if parsed.query and re.search(
        r"(?i)(api[_-]?key|auth[_-]?token|password|private_key|secret|token|signature|sig)=",
        parsed.query,
    ):
        findings.append(
            Finding(
                "blocker",
                "external_feedback_url",
                "feedback URL query appears to contain a secret or signed token",
                feedback_url,
            )
        )
    for label, pattern in HIGH_CONFIDENCE_CONTENT_PATTERNS:
        if pattern.search(feedback_url):
            findings.append(
                Finding(
                    "blocker",
                    "external_feedback_url",
                    f"feedback URL appears to contain {label}",
                    feedback_url,
                )
            )
    return findings


def github_feedback_api_url(feedback_url: str) -> str | None:
    parsed = urlparse(feedback_url)
    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != "github.com":
        return None

    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 4 or parts[2] not in {"issues", "pull"} or not parts[3].isdigit():
        return None

    owner, repo, kind, number = parts[:4]
    if parsed.fragment.startswith("issuecomment-"):
        comment_id = parsed.fragment.removeprefix("issuecomment-")
        if comment_id.isdigit():
            return f"https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}"
    if kind == "issues":
        return f"https://api.github.com/repos/{owner}/{repo}/issues/{number}"
    return None


def parse_github_issue_url(issue_url: str) -> tuple[str, str, int] | None:
    parsed = urlparse(issue_url)
    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != "github.com":
        return None
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 4 or parts[2] != "issues" or not parts[3].isdigit():
        return None
    return parts[0], parts[1], int(parts[3])


def infer_feedback_tracker_url(root: Path) -> str:
    data, _checks = load_adoption_evidence(root)
    if data:
        for url in list_value(data.get("issue_urls")):
            if isinstance(url, str) and "/issues/8" in url:
                return url
        for url in list_value(data.get("issue_urls")):
            if isinstance(url, str) and "/issues/" in url:
                return url
    repository = infer_public_repository(root)
    return f"https://github.com/{repository}/issues/8"


def find_feedback_candidates(
    root: Path,
    issue_url: str | None = None,
    fetcher: Any = fetch_github_json,
) -> tuple[list[dict[str, str]], list[Finding]]:
    root = root.resolve()
    tracker_url = issue_url.strip() if issue_url else infer_feedback_tracker_url(root)
    parsed = parse_github_issue_url(tracker_url)
    if parsed is None:
        return [], [
            Finding(
                "blocker",
                "feedback_tracker_url",
                "feedback candidate scan requires a GitHub issue URL",
                tracker_url,
            )
        ]

    owner, repo, issue_number = parsed
    maintainer_login = infer_public_repository(root).split("/", 1)[0]
    api_url = (
        f"https://api.github.com/repos/{owner}/{repo}/issues/"
        f"{issue_number}/comments?per_page=100"
    )
    try:
        payload = fetcher(api_url)
    except HTTPError as error:
        return [], [
            Finding(
                "blocker",
                "feedback_candidates",
                github_api_error_message("GitHub comments API", error),
            )
        ]
    except (OSError, URLError, json.JSONDecodeError) as error:
        return [], [
            Finding("blocker", "feedback_candidates", f"GitHub comments API failed: {error}")
        ]

    if not isinstance(payload, list):
        return [], [
            Finding(
                "blocker",
                "feedback_candidates",
                "GitHub comments response was not a list",
            )
        ]

    candidates: list[dict[str, str]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        user = item.get("user")
        login = string_value(user.get("login")) if isinstance(user, dict) else ""
        url = string_value(item.get("html_url"))
        body = string_value(item.get("body"))
        if not login or not url or login.lower() == maintainer_login.lower():
            continue
        if has_blockers(validate_external_feedback_url(url)):
            continue
        excerpt = body.replace("\r", " ").replace("\n", " ").strip()
        if len(excerpt) > 140:
            excerpt = excerpt[:137].rstrip() + "..."
        candidates.append({"url": url, "author": login, "excerpt": excerpt})

    return candidates, []


def check_external_feedback_author(
    feedback_url: str,
    maintainer_login: str,
    fetcher: Any = fetch_github_json,
) -> list[Finding]:
    api_url = github_feedback_api_url(feedback_url)
    if api_url is None:
        return [
            Finding(
                "warn",
                "external_feedback_url.author",
                "feedback author cannot be automatically verified for this URL",
            )
        ]

    try:
        payload = fetcher(api_url)
    except HTTPError as error:
        return [
            Finding(
                "blocker",
                "external_feedback_url.author",
                github_api_error_message("GitHub feedback author check", error),
            )
        ]
    except (OSError, URLError, json.JSONDecodeError) as error:
        return [
            Finding(
                "blocker",
                "external_feedback_url.author",
                f"GitHub feedback author check failed: {error}",
            )
        ]

    if not isinstance(payload, dict):
        return [
            Finding(
                "blocker",
                "external_feedback_url.author",
                "GitHub feedback response was not an object",
            )
        ]
    user = payload.get("user")
    login = string_value(user.get("login")) if isinstance(user, dict) else ""
    if not login:
        return [
            Finding(
                "blocker",
                "external_feedback_url.author",
                "GitHub feedback response did not include an author",
            )
        ]
    if login.lower() == maintainer_login.lower():
        return [
            Finding(
                "blocker",
                "external_feedback_url.author",
                "feedback URL is authored by the maintainer, not an external reviewer",
                login,
            )
        ]
    return []


def record_external_feedback(
    root: Path,
    feedback_url: str,
    fetcher: Any = fetch_github_json,
) -> tuple[dict[str, Any], list[Finding]]:
    root = root.resolve()
    data, checks = load_adoption_evidence(root)
    findings = [
        Finding(check.status, check.name, check.message)
        for check in checks
        if check.status == "blocker"
    ]
    if data is None:
        return {}, findings

    url = feedback_url.strip()
    findings.extend(validate_external_feedback_url(url))
    maintainer_login = infer_public_repository(root).split("/", 1)[0]
    findings.extend(check_external_feedback_author(url, maintainer_login, fetcher))
    if has_blockers(findings):
        return data, findings

    public_evidence, public_findings = collect_public_evidence(root, fetcher)
    if public_evidence:
        data = merge_public_evidence(data, public_evidence)
    for finding in public_findings:
        severity = "warn" if finding.severity == "blocker" else finding.severity
        findings.append(Finding(severity, finding.path, finding.message, finding.value))

    existing_urls = [
        item.strip()
        for item in list_value(data.get("external_feedback_urls"))
        if isinstance(item, str) and item.strip()
    ]
    if url not in existing_urls:
        existing_urls.append(url)
    data["external_feedback_urls"] = existing_urls
    data["status_date"] = dt.date.today().isoformat()

    notes = [
        item
        for item in list_value(data.get("notes"))
        if isinstance(item, str) and item.strip()
    ]
    note = "External feedback URLs must stay public-safe and reviewer-accessible."
    if note not in notes:
        notes.append(note)
    data["notes"] = notes

    path = root / ADOPTION_EVIDENCE_FILE
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data, findings


def extract_html_urls(payload: Any) -> list[str]:
    if not isinstance(payload, list):
        return []
    urls: list[str] = []
    for item in payload:
        if isinstance(item, dict):
            url = string_value(item.get("html_url"))
            if url:
                urls.append(url)
    return urls


def extract_workflow_run_urls(payload: Any) -> list[str]:
    return extract_html_urls(payload)


def extract_issue_urls(payload: Any) -> list[str]:
    if not isinstance(payload, list):
        return []
    urls: list[str] = []
    for item in payload:
        if isinstance(item, dict) and "pull_request" not in item:
            url = string_value(item.get("html_url"))
            if url:
                urls.append(url)
    return urls


def extract_pull_request_urls(payload: Any) -> list[str]:
    if not isinstance(payload, list):
        return []
    urls: list[str] = []
    for item in payload:
        if isinstance(item, dict) and "pull_request" in item:
            url = string_value(item.get("html_url"))
            if url:
                urls.append(url)
    return urls


def format_public_evidence_report(
    evidence: dict[str, Any], findings: list[Finding]
) -> str:
    if not evidence:
        lines = ["# Public Evidence Collection"]
        for finding in findings:
            lines.append(f"- {finding.severity.upper()} {finding.path}: {finding.message}")
        return "\n".join(lines)

    lines = [
        "# Public Evidence Collection",
        "",
        f"Repository: {evidence.get('public_repository_url') or 'unknown'}",
        f"Stars: {evidence.get('stars', 0)}",
        f"Forks: {evidence.get('forks', 0)}",
        "",
        "Copy reviewed values into `docs/adoption-evidence.json`:",
        "",
        "```json",
        json.dumps(evidence, indent=2, sort_keys=True),
        "```",
    ]
    if findings:
        lines.extend(["", "Warnings:"])
        for finding in findings:
            lines.append(
                f"- {finding.severity.upper()} {finding.path}: {finding.message}"
            )
    return "\n".join(lines)


def format_record_feedback_report(
    evidence: dict[str, Any], findings: list[Finding], feedback_url: str
) -> str:
    lines = ["# External Feedback Recording", ""]
    for finding in findings:
        lines.append(f"- {finding.severity.upper()} {finding.path}: {finding.message}")
    if has_blockers(findings):
        lines.extend(["", "No evidence file changes were written."])
    else:
        urls = list_value(evidence.get("external_feedback_urls"))
        lines.extend(
            [
                f"- RECORDED external feedback URL: {feedback_url}",
                f"- Total external feedback URLs: {len(urls)}",
                f"- Stars: {evidence.get('stars', 0)}",
                f"- Forks: {evidence.get('forks', 0)}",
                f"- CI run URLs: {len(list_value(evidence.get('ci_run_urls')))}",
                "",
                "Next checks:",
                "",
                "```bash",
                "asset-pipeline-steward evidence .",
                "asset-pipeline-steward readiness .",
                "asset-pipeline-steward application .",
                "```",
            ]
        )
    return "\n".join(lines)


def format_feedback_candidates_report(
    candidates: list[dict[str, str]], findings: list[Finding]
) -> str:
    lines = ["# External Feedback Candidates", ""]
    for finding in findings:
        lines.append(f"- {finding.severity.upper()} {finding.path}: {finding.message}")
    if findings:
        return "\n".join(lines)
    if not candidates:
        lines.append("- No non-maintainer feedback comments found yet.")
        lines.extend(
            [
                "",
                "Next action: share `docs/feedback-outreach-kit.md` and wait for a real reviewer.",
            ]
        )
        return "\n".join(lines)

    for candidate in candidates:
        lines.append(f"- {candidate['url']}")
        lines.append(f"  - author: {candidate['author']}")
        if candidate.get("excerpt"):
            lines.append(f"  - excerpt: {candidate['excerpt']}")
    lines.extend(
        [
            "",
            "Record a reviewed candidate with:",
            "",
            "```bash",
            "asset-pipeline-steward record-feedback <candidate-url>",
            "```",
        ]
    )
    return "\n".join(lines)


def public_repository_url(root: Path) -> str:
    data, _checks = load_adoption_evidence(root)
    repo_url = string_value(data.get("public_repository_url")) if data else ""
    if repo_url:
        return repo_url.rstrip("/")
    return f"https://github.com/{DEFAULT_PUBLIC_REPOSITORY}"


def public_blob_url(root: Path, path: str) -> str:
    return f"{public_repository_url(root)}/blob/main/{path}"


def build_reviewer_checklist(root: Path) -> dict[str, Any]:
    repo_url = public_repository_url(root)
    feedback_form = f"{repo_url}/issues/new?template=feedback.yml"
    review_landing = public_blob_url(root, "REVIEW.md")
    return {
        "repository_url": repo_url,
        "review_paths": [
            {
                "name": "10-minute skim",
                "steps": [
                    f"Read {review_landing}",
                    f"Skim {public_blob_url(root, 'docs/reviewer-brief.md')}",
                    f"Skim {public_blob_url(root, 'examples/handoff_resume_manifest.json')}",
                    "Leave one concrete feedback issue",
                ],
            },
            {
                "name": "20-minute quickstart",
                "steps": [
                    "Run `python -m pip install -e .`",
                    "Run `asset-pipeline-steward repo-scan .`",
                    "Run `asset-pipeline-steward readiness .`",
                    "Run `asset-pipeline-steward report examples/handoff_resume_manifest.json`",
                    "Leave what worked and what was unclear",
                ],
            },
            {
                "name": "40-minute maintainer review",
                "steps": [
                    f"Read {public_blob_url(root, 'docs/end-to-end-maintainer-loop.md')}",
                    "Compare the manifest shape against one real workflow without sharing private data",
                    "Identify one missing field, validation rule, report section, or handoff rule",
                    "Leave a public feedback issue or public comment",
                ],
            },
        ],
        "useful_feedback": [
            "unclear field",
            "missing validation rule",
            "weak report output",
            "adoption blocker",
            "reason this does not fit a real workflow",
        ],
        "public_safety": [
            "Do not include private paths",
            "Do not include logs, credentials, tokens, or `.env` contents",
            "Do not include model files, generated private media, or non-public samples",
        ],
        "evidence_recording": [
            "The feedback form asks reviewers to confirm that the public issue URL may be recorded as external feedback evidence.",
            "Record only reviewed public-safe URLs from someone other than the maintainer.",
        ],
        "feedback_form": feedback_form,
        "maintainer_follow_up": [
            "asset-pipeline-steward feedback-candidates .",
            "asset-pipeline-steward record-feedback <public-feedback-url>",
            "asset-pipeline-steward evidence .",
        ],
    }


def format_reviewer_checklist(checklist: dict[str, Any]) -> str:
    lines = [
        "# Reviewer Checklist",
        "",
        f"Repository: {checklist['repository_url']}",
        "",
        "## Review Paths",
    ]
    for path in checklist["review_paths"]:
        lines.extend(["", f"### {path['name']}", ""])
        for step in path["steps"]:
            lines.append(f"- {step}")

    lines.extend(["", "## Useful Feedback", ""])
    for item in checklist["useful_feedback"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Public Safety", ""])
    for item in checklist["public_safety"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Evidence Recording", ""])
    for item in checklist["evidence_recording"]:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Feedback Form",
            "",
            str(checklist["feedback_form"]),
            "",
            "## Maintainer Follow-Up",
            "",
            "```bash",
        ]
    )
    lines.extend(checklist["maintainer_follow_up"])
    lines.append("```")
    return "\n".join(lines)


def build_first_feedback_playbook(root: Path) -> dict[str, Any]:
    repo_url = public_repository_url(root)
    feedback_form = f"{repo_url}/issues/new?template=feedback.yml"
    review_landing = public_blob_url(root, "REVIEW.md")
    reviewer_brief = public_blob_url(root, "docs/reviewer-brief.md")
    reviewer_checklist = public_blob_url(root, "docs/reviewer-checklist.md")
    outreach_kit = public_blob_url(root, "docs/feedback-outreach-kit.md")
    return {
        "repository_url": repo_url,
        "goal": "Collect one public, non-maintainer feedback URL that can be recorded in external_feedback_urls.",
        "reviewer_profiles": [
            {
                "profile": "AI asset workflow maintainer",
                "ask": "10-minute skim of reviewer brief and handoff example",
                "best_feedback": "one unclear field, missing rule, or adoption blocker",
            },
            {
                "profile": "Dataset, benchmark, or review-queue maintainer",
                "ask": "20-minute quickstart and one report command",
                "best_feedback": "whether manifest/report output fits a real maintenance workflow",
            },
            {
                "profile": "Open-source maintainer using CI, releases, or issue triage",
                "ask": "40-minute maintainer review of the end-to-end loop",
                "best_feedback": "what would make the workflow easier to review, release, or hand off",
            },
        ],
        "send_sequence": [
            "Send the short request to one reviewer profile only.",
            "Ask for a public issue or public comment, not private praise.",
            "Wait for a concrete critique before recording evidence.",
        ],
        "short_request": (
            "I published a small public-safe toolkit for AI asset pipeline maintenance: "
            f"{repo_url}\n\n"
            "Could you give it a 10-minute skim and leave one public feedback issue? "
            "The useful answer is one concrete adoption blocker, unclear field, or missing rule.\n\n"
            f"Start here: {review_landing}\n"
            f"Feedback form: {feedback_form}\n\n"
            "Please do not include private paths, logs, credentials, model files, or non-public media."
        ),
        "public_links": {
            "review_landing": review_landing,
            "reviewer_brief": reviewer_brief,
            "reviewer_checklist": reviewer_checklist,
            "outreach_kit": outreach_kit,
            "feedback_form": feedback_form,
        },
        "valid_feedback_rules": [
            "author is not the maintainer",
            "URL is public or reviewer-accessible",
            "content discusses this repository or workflow",
            "reviewer confirms the public issue URL may be recorded as external feedback evidence",
            "content does not expose private paths, credentials, logs, model files, or non-public media",
        ],
        "api_recovery": (
            "If GitHub returns a rate-limit 403 while scanning candidates or checking authors, "
            "set GITHUB_TOKEN to a token with public repository read access and rerun. "
            "Do not commit the token."
        ),
        "maintainer_follow_up": [
            "asset-pipeline-steward feedback-candidates .",
            "asset-pipeline-steward record-feedback <public-feedback-url>",
            "asset-pipeline-steward feedback-response-playbook .",
            "asset-pipeline-steward evidence .",
            "asset-pipeline-steward submission-ready . --manual-ready",
        ],
    }


def format_first_feedback_playbook(playbook: dict[str, Any]) -> str:
    lines = [
        "# First Feedback Playbook",
        "",
        f"Repository: {playbook['repository_url']}",
        "",
        "## Goal",
        "",
        str(playbook["goal"]),
        "",
        "## Reviewer Profiles",
    ]
    for reviewer in playbook["reviewer_profiles"]:
        lines.extend(
            [
                "",
                f"### {reviewer['profile']}",
                "",
                f"- Ask: {reviewer['ask']}",
                f"- Best feedback: {reviewer['best_feedback']}",
            ]
        )

    lines.extend(["", "## Send Sequence", ""])
    for step in playbook["send_sequence"]:
        lines.append(f"- {step}")

    lines.extend(["", "## Short Request", "", "```text", playbook["short_request"], "```"])

    lines.extend(["", "## Public Links", ""])
    for label, url in playbook["public_links"].items():
        lines.append(f"- {label}: {url}")

    lines.extend(["", "## Valid Feedback Rules", ""])
    for rule in playbook["valid_feedback_rules"]:
        lines.append(f"- {rule}")

    lines.extend(["", "## API Recovery", "", str(playbook["api_recovery"])])

    lines.extend(["", "## Maintainer Follow-Up", "", "```bash"])
    lines.extend(playbook["maintainer_follow_up"])
    lines.append("```")
    return "\n".join(lines)


def build_public_usage_note(root: Path) -> dict[str, Any]:
    repo_url = public_repository_url(root)
    review_landing = public_blob_url(root, "REVIEW.md")
    terminal_examples = public_blob_url(root, "docs/terminal-examples.md")
    end_to_end = public_blob_url(root, "docs/end-to-end-maintainer-loop.md")
    feedback_form = f"{repo_url}/issues/new?template=feedback.yml"
    return {
        "repository_url": repo_url,
        "goal": (
            "Publish a public-safe usage note that invites concrete external feedback "
            "without counting maintainer-authored text as adoption evidence."
        ),
        "short_note": (
            "I published AI Asset Pipeline Steward, a small public-safe toolkit for turning "
            "local AI asset workflows into repeatable maintainer records:\n"
            f"{repo_url}\n\n"
            "It validates synthetic/public-safe manifests, separates human review from "
            "automated observations, and keeps batch or review handoffs resumable.\n\n"
            "If this overlaps with your workflow, the fastest review path is here:\n"
            f"{review_landing}\n\n"
            "Useful feedback is one concrete blocker, unclear field, missing validation "
            "rule, or reason it does not fit your workflow."
        ),
        "long_note": (
            "AI Asset Pipeline Steward is a public-safe starter kit for maintainers who "
            "need to turn local AI image, audio, video, dataset, benchmark, or review "
            "queues into repeatable records.\n\n"
            "The current alpha focuses on synthetic manifests, public-safety scanning, "
            "model/workflow readiness, human-vs-automated review signals, decision gates, "
            "and handoffs another maintainer or coding agent can resume.\n\n"
            "Try the terminal examples or skim the end-to-end maintainer loop, then leave "
            "one public feedback issue with a concrete adoption blocker or missing rule."
        ),
        "links": {
            "review_landing": review_landing,
            "terminal_examples": terminal_examples,
            "end_to_end_loop": end_to_end,
            "feedback_form": feedback_form,
        },
        "public_safety": [
            "Do not include private paths, logs, credentials, model files, generated private media, or non-public samples.",
            "Do not paste private DMs, screenshots, or contact details into the repository.",
            "Treat this maintainer-authored note as outreach material, not external adoption evidence.",
        ],
        "after_posting": [
            "Wait for a public response or feedback issue from someone other than the maintainer.",
            "Run asset-pipeline-steward feedback-candidates .",
            "Record only reviewed public-safe URLs with asset-pipeline-steward record-feedback <public-feedback-url>.",
            "Run asset-pipeline-steward feedback-response-playbook . and turn one concrete critique into a visible issue, docs change, validation rule, release note, or roadmap decision.",
        ],
    }


def format_public_usage_note(note: dict[str, Any]) -> str:
    lines = [
        "# Public Usage Note",
        "",
        f"Repository: {note['repository_url']}",
        "",
        "## Goal",
        "",
        str(note["goal"]),
        "",
        "## Short Note",
        "",
        "```text",
        str(note["short_note"]),
        "```",
        "",
        "## Longer Note",
        "",
        "```text",
        str(note["long_note"]),
        "```",
        "",
        "## Links",
        "",
    ]
    for label, url in note["links"].items():
        lines.append(f"- {label}: {url}")

    lines.extend(["", "## Public Safety", ""])
    for item in note["public_safety"]:
        lines.append(f"- {item}")

    lines.extend(["", "## After Posting", ""])
    for item in note["after_posting"]:
        lines.append(f"- {item}")

    return "\n".join(lines)


def build_reviewer_request(root: Path) -> dict[str, Any]:
    repo_url = public_repository_url(root)
    review_landing = public_blob_url(root, "REVIEW.md")
    reviewer_brief = public_blob_url(root, "docs/reviewer-brief.md")
    reviewer_checklist = public_blob_url(root, "docs/reviewer-checklist.md")
    terminal_examples = public_blob_url(root, "docs/terminal-examples.md")
    feedback_form = f"{repo_url}/issues/new?template=feedback.yml"
    return {
        "repository_url": repo_url,
        "goal": (
            "Send one concrete public-safe request to a real reviewer and ask for "
            "a public feedback issue or comment from someone other than the maintainer."
        ),
        "english_short_dm": (
            "I published a small public-safe toolkit for AI asset pipeline maintenance:\n"
            f"{repo_url}\n\n"
            "Could you give it a 10-minute skim and leave one public feedback issue? "
            "The useful answer is one concrete blocker, unclear field, missing validation "
            "rule, or reason it does not fit your workflow.\n\n"
            f"Start here: {review_landing}\n"
            f"Feedback form: {feedback_form}\n\n"
            "Please do not include private paths, logs, credentials, model files, or non-public media."
        ),
        "chinese_short_dm": (
            "我做了一个公开安全的小工具，用来把本地 AI 素材、模型评测、人工审核这类流程，"
            "整理成可复现、可交接、可公开的维护记录：\n"
            f"{repo_url}\n\n"
            "你方便花 10 分钟看一下 reviewer brief 或 example，然后留一个公开 feedback issue 吗？"
            "不用夸，最好指出哪里不清楚、缺哪个字段/校验规则、有什么采用阻碍，或者为什么不适合你的流程。\n\n"
            f"Review landing: {review_landing}\n"
            f"Feedback form: {feedback_form}\n\n"
            "不要贴私人路径、日志、密钥、模型文件或非公开素材。"
        ),
        "chinese_public_post": (
            "我在征集一个开源小工具的真实反馈：AI Asset Pipeline Steward\n"
            f"{repo_url}\n\n"
            "它的目标是把本地 AI 素材生产、模型/工作流检查、人工审核、VLM 辅助观察、"
            "批量任务交接这些重复工作，抽成一个公开安全的维护流程。仓库只放合成示例，"
            "不包含模型权重、私人路径、日志、密钥或非公开素材。\n\n"
            "希望有做过 AI 图像/音视频/数据集/评测/审核流程的人帮忙看一眼：\n"
            "- 10 分钟：看 reviewer brief 和 handoff 示例\n"
            "- 20 分钟：跑 quickstart\n"
            "- 40 分钟：拿它和你自己的真实维护流程对照，但不要公开私人数据\n\n"
            "最有用的是具体批评：哪里不清楚、缺什么字段、缺什么校验规则、report 哪里不好用、"
            "有什么采用阻碍、为什么不适合你的流程。\n\n"
            f"Review landing: {review_landing}\n"
            f"Feedback form: {feedback_form}"
        ),
        "links": {
            "review_landing": review_landing,
            "reviewer_brief": reviewer_brief,
            "reviewer_checklist": reviewer_checklist,
            "terminal_examples": terminal_examples,
            "feedback_form": feedback_form,
        },
        "valid_feedback_rules": [
            "reviewer is not the repository maintainer",
            "feedback URL is public or reviewer-accessible",
            "feedback includes one concrete blocker, unclear field, missing rule, or fit concern",
            "feedback does not expose private paths, logs, credentials, model files, or non-public media",
            "reviewer confirms the public issue URL may be recorded as external feedback evidence",
        ],
        "after_feedback": [
            "asset-pipeline-steward feedback-candidates .",
            "asset-pipeline-steward record-feedback <public-feedback-url>",
            "asset-pipeline-steward feedback-response-playbook .",
            "asset-pipeline-steward evidence .",
            "asset-pipeline-steward submission-ready . --manual-ready",
        ],
    }


def format_reviewer_request(request: dict[str, Any]) -> str:
    lines = [
        "# Reviewer Request Pack",
        "",
        f"Repository: {request['repository_url']}",
        "",
        "## Goal",
        "",
        str(request["goal"]),
        "",
        "## English Short DM",
        "",
        "```text",
        str(request["english_short_dm"]),
        "```",
        "",
        "## Chinese Short DM",
        "",
        "```text",
        str(request["chinese_short_dm"]),
        "```",
        "",
        "## Chinese Public Post",
        "",
        "```text",
        str(request["chinese_public_post"]),
        "```",
        "",
        "## Links",
        "",
    ]
    for label, url in request["links"].items():
        lines.append(f"- {label}: {url}")

    lines.extend(["", "## Valid Feedback Rules", ""])
    for rule in request["valid_feedback_rules"]:
        lines.append(f"- {rule}")

    lines.extend(["", "## After Feedback", "", "```bash"])
    lines.extend(request["after_feedback"])
    lines.append("```")
    return "\n".join(lines)


def build_feedback_response_playbook(root: Path) -> dict[str, Any]:
    repo_url = public_repository_url(root)
    evidence_file = public_blob_url(root, "docs/adoption-evidence.json")
    growth_plan = public_blob_url(root, "docs/maintainer-growth-plan.md")
    submission_runbook = public_blob_url(root, "docs/codex-for-oss-submission-runbook.md")
    return {
        "repository_url": repo_url,
        "goal": (
            "Turn one real public, non-maintainer feedback URL into visible "
            "maintenance evidence before Codex for OSS submission."
        ),
        "response_rules": [
            "Do not quote or record private paths, credentials, logs, model files, or non-public media.",
            "Do not count maintainer-authored text as external feedback.",
            "Record the feedback URL only after checking that it is public-safe and reviewer-accessible.",
            "Respond publicly with either a shipped change, a linked issue, or a clear roadmap decision.",
            "Keep the response small enough that tests and repo-scan can verify it before submission.",
        ],
        "response_sequence": [
            "Screen the feedback for public-safety problems before quoting or linking it.",
            "Record the URL with asset-pipeline-steward record-feedback <public-feedback-url>.",
            "Classify the critique as docs clarification, validation rule, CLI ergonomics, roadmap decision, or out-of-scope.",
            "Open or update one public issue that links the feedback URL and states the maintainer decision.",
            "Ship the smallest docs, validation, test, or roadmap change that addresses the critique.",
            "Reply publicly with what changed, what will change later, or why the feedback is out of scope.",
            "Rerun evidence, readiness, codex-oss-status, and submission-ready before the official form.",
        ],
        "response_options": [
            {
                "type": "Docs clarification",
                "use_when": "the reviewer was blocked by unclear instructions or missing examples",
                "evidence": "docs diff, test if applicable, and public maintainer reply",
            },
            {
                "type": "Validation rule",
                "use_when": "the reviewer found a manifest field or safety rule that should be enforced",
                "evidence": "validator change, focused test, and public maintainer reply",
            },
            {
                "type": "CLI ergonomics",
                "use_when": "the reviewer found command output, next actions, or error recovery unclear",
                "evidence": "CLI output change, test, terminal example update, and public maintainer reply",
            },
            {
                "type": "Roadmap decision",
                "use_when": "the feedback is valid but too large for the current release",
                "evidence": "roadmap or issue update with scope, reason, and next milestone",
            },
            {
                "type": "Out-of-scope",
                "use_when": "the request would require private assets, large model files, or unsafe publishing",
                "evidence": "public reply explaining the boundary and any safe alternative",
            },
        ],
        "public_reply_template": (
            "Thanks for the concrete feedback. I recorded this as external feedback "
            "evidence because it is public-safe and not maintainer-authored.\n\n"
            "Maintainer response:\n"
            "- Decision: <docs clarification | validation rule | CLI ergonomics | roadmap decision | out-of-scope>\n"
            "- Action: <link issue, docs change, PR, release note, or roadmap item>\n"
            "- Verification: <tests/checks run>\n\n"
            "I avoided private paths, logs, credentials, model files, and non-public media."
        ),
        "commands": [
            "asset-pipeline-steward feedback-candidates .",
            "asset-pipeline-steward record-feedback <public-feedback-url>",
            "asset-pipeline-steward evidence .",
            "asset-pipeline-steward readiness .",
            "asset-pipeline-steward codex-oss-status . --manual-ready",
            "asset-pipeline-steward submission-ready . --manual-ready",
        ],
        "links": {
            "evidence_file": evidence_file,
            "growth_plan": growth_plan,
            "submission_runbook": submission_runbook,
        },
    }


def format_feedback_response_playbook(playbook: dict[str, Any]) -> str:
    lines = [
        "# Feedback Response Playbook",
        "",
        f"Repository: {playbook['repository_url']}",
        "",
        "## Goal",
        "",
        str(playbook["goal"]),
        "",
        "## Response Rules",
        "",
    ]
    for rule in playbook["response_rules"]:
        lines.append(f"- {rule}")

    lines.extend(["", "## Response Sequence", ""])
    for index, step in enumerate(playbook["response_sequence"], start=1):
        lines.append(f"{index}. {step}")

    lines.extend(["", "## Response Options", ""])
    for option in playbook["response_options"]:
        lines.extend(
            [
                f"### {option['type']}",
                "",
                f"- Use when: {option['use_when']}",
                f"- Evidence: {option['evidence']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Public Reply Template",
            "",
            "```text",
            str(playbook["public_reply_template"]),
            "```",
            "",
            "## Commands",
            "",
            "```bash",
        ]
    )
    lines.extend(playbook["commands"])
    lines.extend(["```", "", "## Links", ""])
    for label, url in playbook["links"].items():
        lines.append(f"- {label}: {url}")

    return "\n".join(lines)


def build_feedback_status_update(root: Path) -> dict[str, Any]:
    repo_url = public_repository_url(root)
    issue_url = f"{repo_url}/issues/8"
    feedback_form = f"{repo_url}/issues/new?template=feedback.yml"
    review_landing = public_blob_url(root, "REVIEW.md")
    first_feedback = public_blob_url(root, "docs/first-feedback-playbook.md")
    response_playbook = public_blob_url(root, "docs/feedback-response-playbook.md")
    terminal_examples = public_blob_url(root, "docs/terminal-examples.md")
    comment = (
        "Maintainer status update for the Codex for OSS growth path.\n\n"
        "Current status:\n"
        "- Still waiting for a real public feedback URL from someone other than the maintainer.\n"
        "- Maintainer-authored comments, docs, and command updates count as maintenance activity only, not external adoption evidence.\n"
        "- Public GitHub API checks may require `GITHUB_TOKEN` when unauthenticated requests are rate-limited.\n\n"
        "Reviewer entrypoints:\n"
        f"- Review landing: {review_landing}\n"
        f"- First feedback playbook: {first_feedback}\n"
        f"- Feedback response playbook: {response_playbook}\n"
        f"- Terminal examples: {terminal_examples}\n"
        f"- Feedback form: {feedback_form}\n\n"
        "Maintainer commands after feedback appears:\n\n"
        "```bash\n"
        "asset-pipeline-steward feedback-candidates .\n"
        "asset-pipeline-steward record-feedback <public-feedback-url>\n"
        "asset-pipeline-steward feedback-response-playbook .\n"
        "asset-pipeline-steward latest-ci .\n"
        "asset-pipeline-steward submission-ready . --manual-ready\n"
        "```\n\n"
        "This update is intentionally not recorded in `external_feedback_urls`."
    )
    return {
        "repository_url": repo_url,
        "issue_url": issue_url,
        "goal": (
            "Generate a public-safe maintainer status update that can be pasted into "
            "issue #8 when GitHub write access is unavailable."
        ),
        "comment": comment,
        "manual_steps": [
            f"Open {issue_url}",
            "Paste the comment draft as a maintainer update.",
            "Do not record the maintainer-authored comment as external feedback evidence.",
            "Wait for a public non-maintainer feedback URL before running record-feedback.",
            "Reprint this draft with asset-pipeline-steward feedback-status-update .",
        ],
        "links": {
            "review_landing": review_landing,
            "first_feedback_playbook": first_feedback,
            "feedback_response_playbook": response_playbook,
            "terminal_examples": terminal_examples,
            "feedback_form": feedback_form,
        },
    }


def format_feedback_status_update(update: dict[str, Any]) -> str:
    lines = [
        "# Feedback Status Update Draft",
        "",
        f"Issue: {update['issue_url']}",
        "",
        "## Goal",
        "",
        str(update["goal"]),
        "",
        "## Comment Draft",
        "",
        "````text",
        str(update["comment"]),
        "````",
        "",
        "## Manual Steps",
        "",
    ]
    for step in update["manual_steps"]:
        lines.append(f"- {step}")

    lines.extend(["", "## Links", ""])
    for label, url in update["links"].items():
        lines.append(f"- {label}: {url}")

    return "\n".join(lines)


def load_starter_issues(root: Path) -> tuple[list[dict[str, Any]], list[Finding]]:
    path = root / STARTER_ISSUES_FILE
    if not path.exists():
        return [], [Finding("blocker", STARTER_ISSUES_FILE, "starter issues file is missing")]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [], [Finding("blocker", STARTER_ISSUES_FILE, f"starter issues file is invalid: {error}")]
    if not isinstance(data, list):
        return [], [Finding("blocker", STARTER_ISSUES_FILE, "starter issues root must be a list")]

    findings: list[Finding] = []
    issues: list[dict[str, Any]] = []
    for index, issue in enumerate(data):
        path_prefix = f"{STARTER_ISSUES_FILE}[{index}]"
        if not isinstance(issue, dict):
            findings.append(Finding("blocker", path_prefix, "starter issue must be an object"))
            continue
        for key in ("title", "labels", "body"):
            if key not in issue:
                findings.append(Finding("blocker", f"{path_prefix}.{key}", "required issue field is missing"))
        if not isinstance(issue.get("title"), str) or not issue.get("title", "").strip():
            findings.append(Finding("blocker", f"{path_prefix}.title", "issue title is required"))
        if not isinstance(issue.get("labels"), list):
            findings.append(Finding("blocker", f"{path_prefix}.labels", "issue labels must be a list"))
        if not isinstance(issue.get("body"), str) or not issue.get("body", "").strip():
            findings.append(Finding("blocker", f"{path_prefix}.body", "issue body is required"))
        issues.append(issue)
    return issues, findings


def format_starter_issues_report(issues: list[dict[str, Any]], findings: list[Finding]) -> str:
    if findings:
        lines = ["Starter issue findings:"]
        for finding in findings:
            lines.append(f"- {finding.severity.upper()} {finding.path}: {finding.message}")
        return "\n".join(lines)

    lines = ["# Starter Issues"]
    for index, issue in enumerate(issues, start=1):
        labels = ", ".join(map(str, issue.get("labels", [])))
        lines.extend(
            [
                "",
                f"## {index}. {issue['title']}",
                "",
                f"Labels: {labels}",
                "",
                str(issue["body"]).strip(),
            ]
        )
    return "\n".join(lines)


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
        help=(
            "Manifest path, or command: validate/report/schema/repo-scan/readiness/"
            "evidence/collect-evidence/latest-ci/feedback-candidates/record-feedback/"
            "application/submission-ready/starter-issues/reviewer-checklist/"
            "first-feedback-playbook/reviewer-request/feedback-response-playbook/"
            "feedback-status-update/public-usage-note/codex-oss-status/"
            "next-human-action"
        ),
    )
    parser.add_argument("manifest", nargs="?", help="Path, feedback URL, or issue URL")
    parser.add_argument("extra", nargs="?", help="Feedback URL or issue URL")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    parser.add_argument(
        "--manual-ready",
        action="store_true",
        help="For submission-ready and codex-oss-status: confirm personal form fields are ready for manual entry",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command_or_manifest == "record-feedback":
        root, feedback_url = resolve_record_feedback_args(args.manifest, args.extra)
        evidence, findings = record_external_feedback(root, feedback_url)
        if args.json:
            payload = {
                "root": str(root),
                "ok": not has_blockers(findings),
                "evidence": evidence,
                "findings": [asdict(finding) for finding in findings],
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(format_record_feedback_report(evidence, findings, feedback_url))
        return 1 if has_blockers(findings) else 0

    if args.command_or_manifest == "feedback-candidates":
        root, issue_url = resolve_feedback_candidates_args(args.manifest, args.extra)
        candidates, findings = find_feedback_candidates(root, issue_url)
        if args.json:
            payload = {
                "root": str(root),
                "ok": not has_blockers(findings),
                "candidates": candidates,
                "findings": [asdict(finding) for finding in findings],
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(format_feedback_candidates_report(candidates, findings))
        return 1 if has_blockers(findings) else 0

    if args.extra is not None:
        raise SystemExit("unexpected extra argument")

    manifest_arg = Path(args.manifest) if args.manifest is not None else None
    command, manifest_path = resolve_command(args.command_or_manifest, manifest_arg)

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

    if command == "collect-evidence":
        root = manifest_path or Path(".")
        evidence, findings = collect_public_evidence(root)
        if args.json:
            payload = {
                "root": str(root),
                "ok": not has_blockers(findings),
                "evidence": evidence,
                "findings": [asdict(finding) for finding in findings],
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(format_public_evidence_report(evidence, findings))
        return 1 if has_blockers(findings) else 0

    if command == "latest-ci":
        root = manifest_path or Path(".")
        status, findings = check_latest_main_ci(root)
        if args.json:
            payload = {
                "root": str(root),
                "ok": not has_blockers(findings),
                "latest_ci": status,
                "findings": [asdict(finding) for finding in findings],
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(format_latest_ci_report(status, findings))
        return 1 if has_blockers(findings) else 0

    if command == "application":
        root = manifest_path or Path(".")
        packet, findings = load_application_packet(root)
        evidence_checks = check_adoption_evidence(root)
        if args.json:
            payload = {
                "root": str(root),
                "ok": not has_blockers(findings),
                "packet": packet or {},
                "findings": [asdict(finding) for finding in findings],
                "evidence_checks": [asdict(check) for check in evidence_checks],
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(format_application_report(packet, findings, evidence_checks))
        return 1 if has_blockers(findings) else 0

    if command == "submission-ready":
        root = manifest_path or Path(".")
        checks = build_submission_checks(root, manual_ready=args.manual_ready)
        if args.json:
            payload = {
                "root": str(root),
                "ok": not has_readiness_blockers(checks),
                "manual_ready": args.manual_ready,
                "checks": [asdict(check) for check in checks],
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(format_submission_report(checks))
        return 1 if has_readiness_blockers(checks) else 0

    if command == "codex-oss-status":
        root = manifest_path or Path(".")
        status = build_codex_oss_status(root, manual_ready=args.manual_ready)
        if args.json:
            payload = {
                "root": str(root),
                "ok": status["recommendation"] == "ready_for_manual_submission",
                "status": status,
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(format_codex_oss_status(status))
        return 0

    if command == "next-human-action":
        root = manifest_path or Path(".")
        action = build_next_human_action(root, manual_ready=args.manual_ready)
        if args.json:
            payload = {
                "root": str(root),
                "ok": action["phase"] == "ready_for_manual_submission",
                "next_human_action": action,
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(format_next_human_action(action))
        return 0

    if command == "starter-issues":
        root = manifest_path or Path(".")
        issues, findings = load_starter_issues(root)
        if args.json:
            payload = {
                "root": str(root),
                "ok": not has_blockers(findings),
                "issues": issues,
                "findings": [asdict(finding) for finding in findings],
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(format_starter_issues_report(issues, findings))
        return 1 if has_blockers(findings) else 0

    if command == "reviewer-checklist":
        root = manifest_path or Path(".")
        checklist = build_reviewer_checklist(root)
        if args.json:
            payload = {
                "root": str(root),
                "ok": True,
                "checklist": checklist,
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(format_reviewer_checklist(checklist))
        return 0

    if command == "first-feedback-playbook":
        root = manifest_path or Path(".")
        playbook = build_first_feedback_playbook(root)
        if args.json:
            payload = {
                "root": str(root),
                "ok": True,
                "playbook": playbook,
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(format_first_feedback_playbook(playbook))
        return 0

    if command == "reviewer-request":
        root = manifest_path or Path(".")
        request = build_reviewer_request(root)
        if args.json:
            payload = {
                "root": str(root),
                "ok": True,
                "reviewer_request": request,
            }
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
        else:
            print(format_reviewer_request(request))
        return 0

    if command == "feedback-response-playbook":
        root = manifest_path or Path(".")
        playbook = build_feedback_response_playbook(root)
        if args.json:
            payload = {
                "root": str(root),
                "ok": True,
                "playbook": playbook,
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(format_feedback_response_playbook(playbook))
        return 0

    if command == "feedback-status-update":
        root = manifest_path or Path(".")
        update = build_feedback_status_update(root)
        if args.json:
            payload = {
                "root": str(root),
                "ok": True,
                "status_update": update,
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(format_feedback_status_update(update))
        return 0

    if command == "public-usage-note":
        root = manifest_path or Path(".")
        note = build_public_usage_note(root)
        if args.json:
            payload = {
                "root": str(root),
                "ok": True,
                "usage_note": note,
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(format_public_usage_note(note))
        return 0

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
    if command_or_manifest == "collect-evidence":
        return command_or_manifest, manifest or Path(".")
    if command_or_manifest == "latest-ci":
        return command_or_manifest, manifest or Path(".")
    if command_or_manifest == "feedback-candidates":
        return command_or_manifest, manifest or Path(".")
    if command_or_manifest == "record-feedback":
        raise SystemExit("record-feedback requires a feedback URL")
    if command_or_manifest == "application":
        return command_or_manifest, manifest or Path(".")
    if command_or_manifest == "submission-ready":
        return command_or_manifest, manifest or Path(".")
    if command_or_manifest == "codex-oss-status":
        return command_or_manifest, manifest or Path(".")
    if command_or_manifest == "next-human-action":
        return command_or_manifest, manifest or Path(".")
    if command_or_manifest == "starter-issues":
        return command_or_manifest, manifest or Path(".")
    if command_or_manifest == "reviewer-checklist":
        return command_or_manifest, manifest or Path(".")
    if command_or_manifest == "first-feedback-playbook":
        return command_or_manifest, manifest or Path(".")
    if command_or_manifest == "reviewer-request":
        return command_or_manifest, manifest or Path(".")
    if command_or_manifest == "feedback-response-playbook":
        return command_or_manifest, manifest or Path(".")
    if command_or_manifest == "feedback-status-update":
        return command_or_manifest, manifest or Path(".")
    if command_or_manifest == "public-usage-note":
        return command_or_manifest, manifest or Path(".")
    if command_or_manifest in {"validate", "report"}:
        if manifest is None:
            raise SystemExit(f"{command_or_manifest} requires a manifest path")
        return command_or_manifest, manifest
    if manifest is not None:
        raise SystemExit("unexpected extra manifest path")
    return "validate", Path(command_or_manifest)


def resolve_record_feedback_args(
    manifest_or_url: str | None, feedback_url: str | None
) -> tuple[Path, str]:
    if manifest_or_url is None:
        raise SystemExit("record-feedback requires a feedback URL")
    if feedback_url is None:
        if manifest_or_url.startswith(("http://", "https://")):
            return Path("."), manifest_or_url
        raise SystemExit("record-feedback requires a feedback URL")
    return Path(manifest_or_url), feedback_url


def resolve_feedback_candidates_args(
    manifest_or_issue_url: str | None, issue_url: str | None
) -> tuple[Path, str | None]:
    if manifest_or_issue_url is None:
        return Path("."), None
    if issue_url is None:
        if manifest_or_issue_url.startswith(("http://", "https://")):
            return Path("."), manifest_or_issue_url
        return Path(manifest_or_issue_url), None
    return Path(manifest_or_issue_url), issue_url


if __name__ == "__main__":
    sys.exit(main())
