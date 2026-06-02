# Public Extraction Tutorial

This tutorial shows how to turn a private local AI asset workflow into a public-safe manifest and maintainer report.

Use it when a workflow has useful structure but the original files, paths, outputs, logs, or model artifacts cannot be published.

## 1. Inventory The Local Workflow

Write down the reusable structure without copying private material:

- asset kinds and queue states;
- model references and verification status;
- workflow steps and preflight checks;
- human review signals;
- automated observations;
- decision gate;
- handoff state.

Do not copy private paths, model files, caches, logs, credentials, or non-public samples.

## 2. Classify Each Item

Use the extraction categories from `docs/public-extraction-checklist.md`:

- keep generic scripts and public-safe documentation;
- replace private samples with synthetic fixtures;
- exclude credentials, local paths, model weights, caches, logs, and non-public media.

| Local item | Public-safe decision | Example replacement |
|---|---|---|
| Private output image | Replace | `examples/synthetic/asset-001.placeholder` |
| Local model weight path | Exclude | External-reference-only model metadata |
| Private review notes | Replace | Neutral human-review state such as `queued` or `accepted` |
| Long local run log | Replace | Short decision gate summary |
| Reusable workflow shape | Keep | Named steps and preflight checks |

## 3. Create A Synthetic Manifest

Start from one of the examples:

```bash
examples/fixture_manifest.json
examples/model_inventory_manifest.json
examples/review_queue_manifest.json
examples/handoff_resume_manifest.json
```

Replace local facts with neutral synthetic labels. Keep the workflow shape, not the private content.
Do not include copyrighted samples, unpublished generated media, private user paths, credentials, caches, or model files.

## 4. Validate The Manifest

```bash
asset-pipeline-steward examples/review_queue_manifest.json
```

The validator checks public safety and maintainability:

- required top-level sections;
- workflow steps and preflight;
- separated human and automated review signals;
- decision gate status and next action;
- handoff goal, current status, next action, blockers, and known unknowns.

## 5. Render A Maintainer Report

```bash
asset-pipeline-steward report examples/review_queue_manifest.json
```

Use the report as a handoff, release note seed, or issue summary.

## 6. Publish Only The Public-Safe Subset

Before committing, run:

```bash
python -m unittest discover -s tests
asset-pipeline-steward repo-scan .
asset-pipeline-steward readiness .
asset-pipeline-steward examples/fixture_manifest.json
asset-pipeline-steward examples/model_inventory_manifest.json
asset-pipeline-steward examples/review_queue_manifest.json
asset-pipeline-steward examples/handoff_resume_manifest.json
```

Then use `docs/public-extraction-checklist.md` for any additional manual review.
