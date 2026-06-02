# Terminal Examples

These examples use only the synthetic fixture manifest.

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
