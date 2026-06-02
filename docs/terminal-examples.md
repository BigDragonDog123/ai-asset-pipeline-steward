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

## Collect Public GitHub Evidence

Use this after the repository exists on GitHub:

```bash
asset-pipeline-steward collect-evidence .
```

Expected output includes a JSON block with the public repository URL, recent CI run URLs, release URLs, issue URLs, pull request URLs, stars, and forks. Before the repository is public, this command reports a blocker.
If GitHub returns a rate-limit `403`, set `GITHUB_TOKEN` to a token with public repository read access and rerun the command.

## Render Application Packet

```bash
asset-pipeline-steward application .
```

Expected output includes draft Codex for OSS form fields, 500-character answer checks, manual fields still needed, and submission-gate warnings for missing public evidence.

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
