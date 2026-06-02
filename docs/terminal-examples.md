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
