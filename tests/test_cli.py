from __future__ import annotations

import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from asset_pipeline_steward.cli import (
    build_readiness_checks,
    build_evidence_report,
    build_maintenance_report,
    build_manifest_schema,
    build_submission_checks,
    collect_public_evidence,
    find_feedback_candidates,
    format_application_report,
    format_public_evidence_report,
    has_readiness_blockers,
    load_application_packet,
    load_starter_issues,
    load_manifest,
    main,
    record_external_feedback,
    scan_repository,
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

    def test_handoff_requires_summary_fields(self) -> None:
        for required_field in ("goal", "current_status", "next_action"):
            with self.subTest(required_field=required_field):
                manifest = load_manifest(ROOT / "examples" / "fixture_manifest.json")
                manifest["handoff"].pop(required_field)

                findings = validate_manifest(manifest)

                self.assertTrue(
                    any(f"handoff.{required_field}" == finding.path for finding in findings)
                )

    def test_handoff_requires_blocker_list(self) -> None:
        for required_list in ("blockers", "known_unknowns"):
            with self.subTest(required_list=required_list):
                manifest = load_manifest(ROOT / "examples" / "fixture_manifest.json")
                manifest["handoff"][required_list] = "none"

                findings = validate_manifest(manifest)

                self.assertTrue(
                    any(f"handoff.{required_list}" == finding.path for finding in findings)
                )

    def test_model_inventory_manifest_passes(self) -> None:
        manifest = load_manifest(ROOT / "examples" / "model_inventory_manifest.json")

        findings = validate_manifest(manifest)

        self.assertEqual([], findings)

    def test_handoff_resume_manifest_passes(self) -> None:
        manifest = load_manifest(ROOT / "examples" / "handoff_resume_manifest.json")

        findings = validate_manifest(manifest)

        self.assertEqual([], findings)
        self.assertIn("progress", manifest["handoff"])
        self.assertTrue(manifest["handoff"]["blockers"])
        self.assertTrue(manifest["handoff"]["known_unknowns"])
        self.assertTrue(manifest["handoff"]["next_action"])

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

    def test_repo_scan_current_repo_passes(self) -> None:
        findings = scan_repository(ROOT)

        self.assertEqual([], findings)

    def test_repo_scan_blocks_sensitive_file_and_api_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / ".env"
            fake_key = "s" + "k-" + "a" * 40
            path.write_text("API_KEY=" + fake_key, encoding="utf-8")

            findings = scan_repository(Path(tmpdir))

        self.assertTrue(any(".env" == finding.path for finding in findings))
        self.assertTrue(any("API key" in finding.message for finding in findings))

    def test_repo_scan_blocks_model_weight_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "example.safetensors"
            path.write_text("placeholder", encoding="utf-8")

            findings = scan_repository(Path(tmpdir))

        self.assertTrue(any("model weight" in finding.message for finding in findings))

    def test_repo_scan_command_returns_zero_for_current_repo(self) -> None:
        with redirect_stdout(StringIO()) as output:
            exit_code = main(["repo-scan", str(ROOT)])

        self.assertEqual(0, exit_code)
        self.assertIn("repo scan passed", output.getvalue())

    def test_readiness_checks_without_git_have_no_blockers(self) -> None:
        checks = build_readiness_checks(ROOT, check_git=False)

        self.assertFalse(has_readiness_blockers(checks))
        self.assertTrue(any(check.name == "repo-scan" for check in checks))
        self.assertTrue(any(check.name == "docs/adoption-evidence.json" for check in checks))

    def test_readiness_detects_missing_required_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            checks = build_readiness_checks(Path(tmpdir), check_git=False)

        self.assertTrue(has_readiness_blockers(checks))
        self.assertTrue(any(check.name == "README.md" for check in checks))

    def test_readiness_command_prints_json(self) -> None:
        with redirect_stdout(StringIO()) as output:
            exit_code = main(["readiness", str(ROOT), "--json"])

        payload = json.loads(output.getvalue())

        self.assertIn(exit_code, {0, 1})
        self.assertIn("checks", payload)
        self.assertTrue(any(check["name"] == "repo-scan" for check in payload["checks"]))

    def test_evidence_report_reads_evidence_file(self) -> None:
        checks, report = build_evidence_report(ROOT)

        self.assertFalse(has_readiness_blockers(checks))
        self.assertIn("# Adoption Evidence", report)
        self.assertTrue(any(check.name == "evidence.release_urls" for check in checks))

    def test_evidence_command_prints_json(self) -> None:
        with redirect_stdout(StringIO()) as output:
            exit_code = main(["evidence", str(ROOT), "--json"])

        payload = json.loads(output.getvalue())

        self.assertEqual(0, exit_code)
        self.assertIn("checks", payload)
        self.assertTrue(any(check["name"] == "evidence.issue_urls" for check in payload["checks"]))

    def test_collect_public_evidence_with_fake_github_api(self) -> None:
        def fake_fetcher(url: str) -> object:
            if url.endswith("/BigDragonDog123/ai-asset-pipeline-steward"):
                return {
                    "html_url": "https://github.com/BigDragonDog123/ai-asset-pipeline-steward",
                    "stargazers_count": 7,
                    "forks_count": 2,
                }
            if "actions/runs" in url:
                return {
                    "workflow_runs": [
                        {
                            "html_url": (
                                "https://github.com/BigDragonDog123/"
                                "ai-asset-pipeline-steward/actions/runs/1"
                            )
                        }
                    ]
                }
            if "releases" in url:
                return [
                    {
                        "html_url": (
                            "https://github.com/BigDragonDog123/"
                            "ai-asset-pipeline-steward/releases/tag/v0.1.0"
                        )
                    }
                ]
            if "issues" in url:
                return [
                    {
                        "html_url": (
                            "https://github.com/BigDragonDog123/"
                            "ai-asset-pipeline-steward/issues/1"
                        )
                    },
                    {
                        "html_url": (
                            "https://github.com/BigDragonDog123/"
                            "ai-asset-pipeline-steward/pull/2"
                        ),
                        "pull_request": {},
                    },
                ]
            raise AssertionError(url)

        evidence, findings = collect_public_evidence(ROOT, fake_fetcher)

        self.assertEqual([], findings)
        self.assertEqual(7, evidence["stars"])
        self.assertEqual(2, evidence["forks"])
        self.assertEqual(1, len(evidence["ci_run_urls"]))
        self.assertEqual(1, len(evidence["release_urls"]))
        self.assertEqual(1, len(evidence["issue_urls"]))
        self.assertEqual(1, len(evidence["pull_request_urls"]))
        self.assertIn("docs/adoption-evidence.json", format_public_evidence_report(evidence, []))

    def test_collect_public_evidence_blocks_missing_repo(self) -> None:
        def fake_fetcher(_url: str) -> object:
            raise HTTPError(_url, 404, "Not Found", None, None)

        evidence, findings = collect_public_evidence(ROOT, fake_fetcher)

        self.assertEqual({}, evidence)
        self.assertTrue(any(finding.severity == "blocker" for finding in findings))

    def test_record_external_feedback_adds_non_maintainer_github_issue(self) -> None:
        def fake_fetcher(url: str) -> object:
            if url.endswith("/issues/9"):
                return {"user": {"login": "external-reviewer"}}
            if url.endswith("/BigDragonDog123/ai-asset-pipeline-steward"):
                return {
                    "html_url": "https://github.com/BigDragonDog123/ai-asset-pipeline-steward",
                    "stargazers_count": 3,
                    "forks_count": 1,
                }
            if "actions/runs" in url:
                return {
                    "workflow_runs": [
                        {
                            "html_url": (
                                "https://github.com/BigDragonDog123/"
                                "ai-asset-pipeline-steward/actions/runs/99"
                            )
                        }
                    ]
                }
            if "releases" in url:
                return [
                    {
                        "html_url": (
                            "https://github.com/BigDragonDog123/"
                            "ai-asset-pipeline-steward/releases/tag/v0.1.0"
                        )
                    }
                ]
            if "issues" in url:
                return [
                    {
                        "html_url": (
                            "https://github.com/BigDragonDog123/"
                            "ai-asset-pipeline-steward/issues/9"
                        )
                    }
                ]
            raise AssertionError(url)

        with tempfile.TemporaryDirectory() as tmpdir:
            docs = Path(tmpdir) / "docs"
            docs.mkdir()
            evidence_path = docs / "adoption-evidence.json"
            evidence_path.write_text(
                json.dumps(
                    {
                        "status_date": "2026-06-02",
                        "public_repository_url": (
                            "https://github.com/BigDragonDog123/"
                            "ai-asset-pipeline-steward"
                        ),
                        "external_feedback_urls": [],
                        "notes": [],
                    }
                ),
                encoding="utf-8",
            )

            url = "https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/9"
            evidence, findings = record_external_feedback(Path(tmpdir), url, fake_fetcher)

            self.assertFalse(any(finding.severity == "blocker" for finding in findings))
            self.assertIn(url, evidence["external_feedback_urls"])
            self.assertEqual(3, evidence["stars"])
            self.assertEqual(1, evidence["forks"])
            self.assertIn(
                "https://github.com/BigDragonDog123/ai-asset-pipeline-steward/actions/runs/99",
                evidence["ci_run_urls"],
            )
            written = json.loads(evidence_path.read_text(encoding="utf-8"))
            self.assertIn(url, written["external_feedback_urls"])
            self.assertEqual(3, written["stars"])
            self.assertEqual(1, written["forks"])

    def test_record_external_feedback_blocks_maintainer_github_comment(self) -> None:
        def fake_fetcher(url: str) -> object:
            self.assertIn("/issues/comments/4601738454", url)
            return {"user": {"login": "BigDragonDog123"}}

        with tempfile.TemporaryDirectory() as tmpdir:
            docs = Path(tmpdir) / "docs"
            docs.mkdir()
            evidence_path = docs / "adoption-evidence.json"
            evidence_path.write_text(
                json.dumps(
                    {
                        "status_date": "2026-06-02",
                        "public_repository_url": (
                            "https://github.com/BigDragonDog123/"
                            "ai-asset-pipeline-steward"
                        ),
                        "external_feedback_urls": [],
                    }
                ),
                encoding="utf-8",
            )

            url = (
                "https://github.com/BigDragonDog123/ai-asset-pipeline-steward/"
                "issues/8#issuecomment-4601738454"
            )
            evidence, findings = record_external_feedback(Path(tmpdir), url, fake_fetcher)

            self.assertTrue(any(finding.severity == "blocker" for finding in findings))
            self.assertNotIn(url, evidence["external_feedback_urls"])
            written = json.loads(evidence_path.read_text(encoding="utf-8"))
            self.assertEqual([], written["external_feedback_urls"])

    def test_feedback_candidates_include_non_maintainer_comments(self) -> None:
        def fake_fetcher(url: str) -> object:
            self.assertIn("/issues/8/comments", url)
            return [
                {
                    "html_url": (
                        "https://github.com/BigDragonDog123/ai-asset-pipeline-steward/"
                        "issues/8#issuecomment-1"
                    ),
                    "body": "The quickstart worked, but the handoff fields were unclear.",
                    "user": {"login": "external-reviewer"},
                },
                {
                    "html_url": (
                        "https://github.com/BigDragonDog123/ai-asset-pipeline-steward/"
                        "issues/8#issuecomment-2"
                    ),
                    "body": "Maintainer status note.",
                    "user": {"login": "BigDragonDog123"},
                },
            ]

        candidates, findings = find_feedback_candidates(
            ROOT,
            "https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/8",
            fake_fetcher,
        )

        self.assertEqual([], findings)
        self.assertEqual(1, len(candidates))
        self.assertEqual("external-reviewer", candidates[0]["author"])
        self.assertIn("issuecomment-1", candidates[0]["url"])

    def test_feedback_candidates_reject_non_github_issue_url(self) -> None:
        candidates, findings = find_feedback_candidates(
            ROOT,
            "https://example.com/not-a-github-issue",
            lambda _url: [],
        )

        self.assertEqual([], candidates)
        self.assertTrue(any(finding.severity == "blocker" for finding in findings))

    def test_record_feedback_command_requires_feedback_url(self) -> None:
        with self.assertRaises(SystemExit):
            main(["record-feedback", str(ROOT)])

    def test_application_packet_loads_and_respects_limits(self) -> None:
        packet, findings = load_application_packet(ROOT)

        self.assertEqual([], findings)
        self.assertIsNotNone(packet)
        assert packet is not None
        self.assertGreaterEqual(len(packet["limited_answers"]), 3)
        for answer in packet["limited_answers"]:
            self.assertLessEqual(len(answer["value"]), answer["max_chars"])

    def test_application_command_prints_packet(self) -> None:
        with redirect_stdout(StringIO()) as output:
            exit_code = main(["application", str(ROOT)])

        self.assertEqual(0, exit_code)
        self.assertIn("# Codex For OSS Application Packet", output.getvalue())
        self.assertIn("BigDragonDog123", output.getvalue())
        self.assertIn("Submission Gate", output.getvalue())

    def test_application_packet_blocks_over_limit_answer(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            docs = Path(tmpdir) / "docs"
            docs.mkdir()
            packet = {
                "status_date": "2026-06-02",
                "fields": [{"label": "GitHub username", "value": "BigDragonDog123"}],
                "limited_answers": [
                    {"title": "Why", "max_chars": 5, "value": "too long"}
                ],
            }
            (docs / "codex-for-oss-application.json").write_text(
                json.dumps(packet),
                encoding="utf-8",
            )

            packet, findings = load_application_packet(Path(tmpdir))

        self.assertIsNotNone(packet)
        self.assertTrue(any(finding.severity == "blocker" for finding in findings))
        self.assertIn("answer is", format_application_report(packet, findings, []))

    def test_submission_checks_block_until_feedback_and_manual_fields_ready(self) -> None:
        checks = build_submission_checks(ROOT, manual_ready=False)

        self.assertTrue(has_readiness_blockers(checks))
        self.assertTrue(
            any(
                check.name == "evidence.external_feedback_urls"
                and check.status == "blocker"
                for check in checks
            )
        )
        self.assertTrue(
            any(
                check.name == "application.manual_fields"
                and check.status == "blocker"
                for check in checks
            )
        )

    def test_submission_checks_manual_ready_only_clears_manual_blocker(self) -> None:
        checks = build_submission_checks(ROOT, manual_ready=True)

        self.assertTrue(has_readiness_blockers(checks))
        self.assertTrue(
            any(
                check.name == "application.manual_fields"
                and check.status == "pass"
                for check in checks
            )
        )
        self.assertTrue(
            any(
                check.name == "evidence.external_feedback_urls"
                and check.status == "blocker"
                for check in checks
            )
        )

    def test_submission_ready_command_reports_not_ready(self) -> None:
        with redirect_stdout(StringIO()) as output:
            exit_code = main(["submission-ready", str(ROOT)])

        self.assertEqual(1, exit_code)
        self.assertIn("NOT READY", output.getvalue())
        self.assertIn("application.manual_fields", output.getvalue())

    def test_starter_issues_file_loads(self) -> None:
        issues, findings = load_starter_issues(ROOT)

        self.assertEqual([], findings)
        self.assertGreaterEqual(len(issues), 5)
        self.assertIn("title", issues[0])

    def test_starter_issues_command_prints_markdown(self) -> None:
        with redirect_stdout(StringIO()) as output:
            exit_code = main(["starter-issues", str(ROOT)])

        self.assertEqual(0, exit_code)
        self.assertIn("# Starter Issues", output.getvalue())
        self.assertIn("Prepare v0.1.0 release", output.getvalue())

    def test_starter_issues_missing_file_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            issues, findings = load_starter_issues(Path(tmpdir))

        self.assertEqual([], issues)
        self.assertTrue(any(finding.severity == "blocker" for finding in findings))

    def test_reviewer_checklist_command_prints_review_paths(self) -> None:
        with redirect_stdout(StringIO()) as output:
            exit_code = main(["reviewer-checklist", str(ROOT)])

        self.assertEqual(0, exit_code)
        text = output.getvalue()
        self.assertIn("# Reviewer Checklist", text)
        self.assertIn("10-minute skim", text)
        self.assertIn("20-minute quickstart", text)
        self.assertIn("40-minute maintainer review", text)
        self.assertIn("issues/new?template=feedback.yml", text)
        self.assertIn("record-feedback <public-feedback-url>", text)

    def test_reviewer_checklist_command_prints_json(self) -> None:
        with redirect_stdout(StringIO()) as output:
            exit_code = main(["reviewer-checklist", str(ROOT), "--json"])

        self.assertEqual(0, exit_code)
        payload = json.loads(output.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual("10-minute skim", payload["checklist"]["review_paths"][0]["name"])
        self.assertIn("feedback_form", payload["checklist"])

    def test_reviewer_checklist_doc_exists(self) -> None:
        text = (ROOT / "docs" / "reviewer-checklist.md").read_text(encoding="utf-8")

        self.assertIn("# Reviewer Checklist", text)
        self.assertIn("10-Minute Skim", text)
        self.assertIn("20-Minute Quickstart", text)
        self.assertIn("40-Minute Maintainer Review", text)
        self.assertIn("issues/new?template=feedback.yml", text)

    def test_first_feedback_playbook_command_prints_action_plan(self) -> None:
        with redirect_stdout(StringIO()) as output:
            exit_code = main(["first-feedback-playbook", str(ROOT)])

        self.assertEqual(0, exit_code)
        text = output.getvalue()
        self.assertIn("# First Feedback Playbook", text)
        self.assertIn("Reviewer Profiles", text)
        self.assertIn("Short Request", text)
        self.assertIn("issues/new?template=feedback.yml", text)
        self.assertIn("feedback-candidates .", text)
        self.assertIn("record-feedback <public-feedback-url>", text)

    def test_first_feedback_playbook_command_prints_json(self) -> None:
        with redirect_stdout(StringIO()) as output:
            exit_code = main(["first-feedback-playbook", str(ROOT), "--json"])

        self.assertEqual(0, exit_code)
        payload = json.loads(output.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(
            "Collect one public, non-maintainer feedback URL that can be recorded in external_feedback_urls.",
            payload["playbook"]["goal"],
        )
        self.assertIn("short_request", payload["playbook"])

    def test_first_feedback_playbook_doc_exists(self) -> None:
        text = (ROOT / "docs" / "first-feedback-playbook.md").read_text(encoding="utf-8")

        self.assertIn("# First Feedback Playbook", text)
        self.assertIn("Reviewer Profiles", text)
        self.assertIn("Short Request", text)
        self.assertIn("asset-pipeline-steward first-feedback-playbook .", text)

    def test_outreach_tracker_doc_avoids_private_contact_data(self) -> None:
        text = (ROOT / "docs" / "outreach-tracker.md").read_text(encoding="utf-8")

        self.assertIn("# Outreach Tracker", text)
        self.assertIn("Do not record names", text)
        self.assertIn("Reviewer Slots", text)
        self.assertIn("external_feedback_urls", text)

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
        self.assertIn("- Current status: Manifest is ready for smoke-test demonstration.", report)
        self.assertIn("- Next action: Run validation and render a maintainer report.", report)
        self.assertIn("- Blockers: none declared", report)
        self.assertIn("- Known unknowns:", report)
        self.assertIn("The fixture does not include real model outputs.", report)

    def test_report_command_returns_zero_for_safe_manifest(self) -> None:
        path = ROOT / "examples" / "fixture_manifest.json"

        with redirect_stdout(StringIO()) as output:
            exit_code = main(["report", str(path)])

        self.assertEqual(0, exit_code)
        self.assertIn("Passed public-safety", output.getvalue())


if __name__ == "__main__":
    unittest.main()
