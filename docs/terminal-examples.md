# Terminal Examples

These examples use only the synthetic fixture manifest.

## Scan Repository Public Safety

```bash
asset-pipeline-steward repo-scan .
```

Expected output:

```text
OK: repo scan passed high-confidence public-safety checks for .
```

## Check Local OSS Readiness

```bash
asset-pipeline-steward readiness .
```

Expected output includes local pass checks plus a warning that public GitHub repository, CI run, release, and adoption evidence must be verified after push.

## Report Adoption Evidence Gaps

```bash
asset-pipeline-steward evidence .
```

Expected output before public launch includes warnings for missing public repo URL, release, CI run, issues, feedback, usage examples, stars, and forks.

## Print Reviewer Checklist

Reviewers can also read the static checklist at `docs/reviewer-checklist.md`.

```bash
asset-pipeline-steward reviewer-checklist .
```

Expected output includes 10-minute, 20-minute, and 40-minute review paths; public-safety reminders; the feedback form link; and maintainer follow-up commands for recording reviewed public feedback.

## Print First Feedback Playbook

Use this when the next action is collecting the first public non-maintainer feedback URL.

```bash
asset-pipeline-steward first-feedback-playbook .
```

Expected output includes reviewer profiles, the short request to send, public links, valid-feedback rules, and maintainer follow-up commands.

## Print Public Usage Note

Use this when preparing a public post that invites concrete feedback without counting maintainer-authored text as external adoption evidence.

```bash
asset-pipeline-steward public-usage-note .
```

Expected output includes a short note, a longer note, public links, public-safety rules, and after-posting steps for recording real external feedback.

## Print Feedback Response Playbook

Use this after a real public feedback URL appears and before treating it as Codex for OSS application evidence.

```bash
asset-pipeline-steward feedback-response-playbook .
```

Expected output includes public-safety rules, a response sequence, response options, a public reply template, and final gate commands. The goal is visible maintenance evidence: a recorded feedback URL plus a public maintainer response through an issue, docs change, validation rule, release note, or roadmap decision.

## Collect Public GitHub Evidence

Use this after the repository exists on GitHub:

```bash
asset-pipeline-steward collect-evidence .
```

Expected output includes a JSON block with the public repository URL, recent CI run URLs, release URLs, issue URLs, pull request URLs, stars, and forks. Before the repository is public, this command reports a blocker.
If GitHub returns a rate-limit `403`, set `GITHUB_TOKEN` to a token with public repository read access and rerun the command.

## Record External Feedback

Scan the feedback tracker for non-maintainer comment candidates:

```bash
asset-pipeline-steward feedback-candidates .
```

Expected behavior: prints public candidate URLs from issue #8 comments when someone other than the maintainer has commented. Maintainer comments are ignored.
If GitHub returns a rate-limit `403`, set `GITHUB_TOKEN` to a token with public repository read access and rerun the command.

Use this after someone other than the maintainer leaves a public feedback link:

```bash
asset-pipeline-steward record-feedback https://example.com/public-feedback-url
```

Expected behavior: updates `docs/adoption-evidence.json` with the feedback URL and refreshes public GitHub metrics when the API is available, unless the URL is not public-safe or is a GitHub issue/comment authored by the maintainer.
If the author check or public metric refresh hits a GitHub API `403`, rerun with `GITHUB_TOKEN` set before submitting the final application.

You can also pass an explicit repository root:

```bash
asset-pipeline-steward record-feedback . https://example.com/public-feedback-url
```

## Render Application Packet

```bash
asset-pipeline-steward application .
```

Expected output includes draft Codex for OSS form fields, 500-character answer checks, manual fields still needed, and submission-gate warnings for missing public evidence.

## Check Final Submission Gate

```bash
asset-pipeline-steward submission-ready .
```

Expected output reports whether the repository is ready for official-form submission. It treats missing external feedback and unconfirmed manual personal fields as blockers.

After a real external feedback URL is recorded and the personal fields are ready for manual entry in the official form, run:

```bash
asset-pipeline-steward submission-ready . --manual-ready
```

Do not commit first name, last name, ChatGPT email, OpenAI Organization ID, or application confirmation emails.

## Check Codex For OSS Growth Status

Use this when you want the current application posture without reading every evidence document:

```bash
asset-pipeline-steward codex-oss-status . --manual-ready
```

Expected output reports whether the project is still in growth mode or ready for manual submission, summarizes recorded public evidence counts, lists blockers and warnings, and prints the next maintainer actions. This command is a status report; `submission-ready` remains the final gate.

## Open Codex For OSS Submission Links

```powershell
.\scripts\open-codex-for-oss-application.ps1
```

Expected behavior: opens the official Codex for OSS form, OpenAI Organization ID settings, the GitHub repository, issue #8, and the feedback form. It does not write personal data or submit the form.

## Preview Post-Publish GitHub Writes

```powershell
.\scripts\create-post-publish-github-items.ps1
```

Expected output previews label, starter issue, and v0.1.0 release creation. Add `-Execute` only after the public repository exists and `GITHUB_TOKEN` is set.

## Create Repository With Token

```powershell
.\scripts\publish-after-github-repo.ps1 -CreateRepo -Push
```

Expected behavior: after `GITHUB_TOKEN` is set to a token that can create repositories, the script creates the public GitHub repository, confirms `origin`, and pushes `main`.

## Render Starter Issues

```bash
asset-pipeline-steward starter-issues .
```

Expected output includes five issue drafts with titles, labels, and acceptance criteria.

## Print The Manifest Schema

```bash
asset-pipeline-steward schema
```

Expected output:

```text
{
  "$defs": {
    ...
  },
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "AI Asset Pipeline Steward Manifest",
  "type": "object"
}
```

## Validate A Manifest

```bash
asset-pipeline-steward examples/fixture_manifest.json
```

Expected output:

```text
OK: examples/fixture_manifest.json passed public-safety and schema checks.
```

## Render A Maintainer Report

```bash
asset-pipeline-steward report examples/fixture_manifest.json
```

Expected sections:

```text
# Asset Pipeline Steward Report
## Inventory
## Workflows
## Review Signals
## Decision Gate
## Validation
```

Use this report as the starting point for handoffs, release notes, or issue triage summaries.

## Run The End-To-End Maintainer Loop

```bash
asset-pipeline-steward examples/end_to_end_maintainer_loop_manifest.json
asset-pipeline-steward report examples/end_to_end_maintainer_loop_manifest.json
```

Expected behavior: validation passes, then the report shows issue triage, review smoke gate, release/rerun decision, separated human and automated review signals, blockers, known unknowns, and a resumable handoff.

## Validate Model Inventory Preflight

```bash
asset-pipeline-steward examples/model_inventory_manifest.json
```

Expected output:

```text
OK: examples/model_inventory_manifest.json passed public-safety and schema checks.
```

## Render Model Inventory Report

```bash
asset-pipeline-steward report examples/model_inventory_manifest.json
```

Expected highlights:

```text
Project: synthetic-model-inventory
- Models: 2
- Workflows: 2
- maintainer-rating: ground-truth
- automated-artifact-notes: supporting-evidence
```

## Validate Review Queue Handoff

```bash
asset-pipeline-steward examples/review_queue_manifest.json
```

Expected output:

```text
OK: examples/review_queue_manifest.json passed public-safety and schema checks.
```

## Validate Handoff Resume Manifest

```bash
asset-pipeline-steward examples/handoff_resume_manifest.json
```

Expected output:

```text
OK: examples/handoff_resume_manifest.json passed public-safety and schema checks.
```

## Validate Handoff Completeness

Manifests must include handoff fields that let a maintainer or agent resume work safely:

- `goal`
- `current_status`
- `next_action`
- `blockers`
- `known_unknowns`

If a required handoff field is missing, validation reports a blocker:

```text
Findings for manifest.json:
- BLOCKER handoff.next_action: handoff field is required
```

## Render Review Queue Report

```bash
asset-pipeline-steward report examples/review_queue_manifest.json
```

Expected highlights:

```text
Project: synthetic-review-queue
- Assets: 3
## Handoff
- Goal: Demonstrate a public-safe review queue handoff.
```

## Render Handoff Resume Report

```bash
asset-pipeline-steward report examples/handoff_resume_manifest.json
```

Expected highlights:

```text
Project: synthetic-handoff-resume
- Assets: 3
## Handoff
- Current status: The batch is paused with progress, blocker, and next-action state recorded.
- Next action: Have a maintainer review resume-asset-003
- Blockers:
- Known unknowns:
```
