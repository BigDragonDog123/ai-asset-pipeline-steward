---
name: ai-asset-pipeline-steward
description: Use when managing AI-generated asset pipelines with model downloads, parameter verification, batch generation, VLM review, human rating, dataset curation, benchmark queues, or handoff reports.
---

# AI Asset Pipeline Steward

## Overview

Use this skill to keep AI-generated asset projects from turning into untracked one-off experiments. The central rule is: verify sources, parameters, workflow dependencies, and review criteria before scaling a batch.

This skill is intentionally domain-neutral. Local projects may involve generated media, model evaluations, review queues, workflow automation, or dataset preparation, but the reusable pattern is broader: asset inventory, model/workflow verification, staged execution, human review, machine-assist calibration, and clear handoff.

## When To Use

Use this when the task involves:

- Downloading, mirroring, hashing, or diagnosing model files.
- Verifying generation model parameters, workflow JSON, custom nodes, LoRAs, VAEs, text encoders, or image-reference dependencies.
- Running image-generation benchmarks, LoRA comparisons, prompt sweeps, or batch queues.
- Building or operating review galleries, rating exports, replacement tracking, or human-review workbenches.
- Using VLMs, taggers, or automated scorers to inspect generated assets.
- Curating datasets from frames, crops, scene groups, or low-count rescue queues.
- Writing audit reports, handoffs, next-batch gates, or maintenance status notes.

Do not use this for:

- One-off image prompt drafting.
- Purely visual UI work with no asset pipeline.
- Uploading private, copyrighted, restricted, or sensitive samples.
- Deleting, moving, or reorganizing user assets without explicit approval.

## Core Rules

1. Verify before scaling.
2. Human rating is ground truth; automated review is evidence.
3. A benchmark is invalid if model-family parameters are guessed or mixed.
4. Every long batch needs a manifest, progress tracking, and a stop/resume plan.
5. Every substantial run ends with a handoff that a new session can continue.
6. Public/open-source outputs must be scrubbed of private paths, copyrighted samples, restricted content, credentials, and large model files.

## Evidence-First Overlay

Before choosing parameters, scripts, models, workflows, review methods, or open-source packaging, run a compact evidence pass:

```text
Official source -> Mature practice -> Local evidence -> Decision -> Verification
```

Use this overlay as follows:

- Official source: model cards, release notes, workflow docs, API docs, schema docs, and first-party examples.
- Mature practice: maintainer examples, active open-source implementations, issue/PR discussions, and benchmark reports.
- Local evidence: manifests, previous reports, ratings, logs, handoffs, scripts, tests, and current dirty-worktree state.
- Decision: state whether the next action is `Adopt`, `Extend`, `Compose`, or `Build`.
- Verification: name the smoke test, CLI check, report, or review pass that will prove the step worked.

Do not invent parameters, review criteria, repository structure, or publishing claims when official or mature examples can be checked. If evidence is missing, mark the item `Unknown` and choose a reversible probe.

## Workflow

### 1. Inventory

List the current roots and assets before acting:

- Source folders and output folders.
- Models, LoRAs, VAEs, text encoders, custom nodes, and workflow files.
- Scripts, launch commands, prior reports, review data, and current queues.
- Generated ratings, VLM observations, benchmark tables, and handoff docs.

Classify each item as public-safe, private-local, sensitive, generated output, or external dependency. Do not assume local file names are safe to publish.

### 2. Source And Parameter Verification

Before running generation, verify:

- Model family and architecture.
- Official, maintainer-proven, or locally proven sampler, scheduler, CFG, steps, resolution, and prompt format.
- Required workflow nodes and model dependencies.
- Download completion and integrity.
- Whether a previous report already found a parameter mismatch or broken workflow.

If a parameter cannot be verified, run a small probe or mark it unknown. Do not silently use a generic default across unrelated model families.

### 3. Smoke Gate

Run the smallest useful test before a full batch:

- One model.
- One workflow.
- One to three outputs.
- Fixed output directory.
- Readable log.
- Clear pass/fail criteria.

If the smoke test fails, fix the source, workflow, dependency, or prompt before expanding.

### 4. Batch Queue

For batch execution, write or inspect a manifest that includes:

- Model, workflow, scenario, and prompt variables.
- Output path and naming convention.
- Seed policy and retry behavior.
- GPU/runtime constraints.
- Progress JSON or checkpoint file.
- Stop, resume, and cleanup expectations.

Prefer resumable scripts and explicit progress files over ad-hoc long-running commands.

### 5. Review And Calibration

Separate review signals:

- Human ratings decide quality gates.
- VLMs provide structured observations, not final truth.
- Taggers and color/statistical metrics are cheap features, not full quality judgments.
- Disagreement sets need manual review.

Ask VLMs for structured evidence such as identity, style, defects, color, composition, anatomy, text/OCR, prompt hints, and workflow hints. Feed the structured observations into the next iteration instead of relying on a single score.

### 6. Decision Gate

Before the next batch, write a short decision gate:

- What passed.
- What failed.
- What changed.
- What remains unknown.
- Whether to scale, rerun, pause, or change parameters.

The gate should be understandable to a fresh session without reading the full logs.

### 7. Handoff

Every substantial run should produce a handoff with:

- Goal and current status.
- Important paths and commands.
- Input assumptions.
- Output artifacts.
- Ratings or benchmark summary.
- Known failures and unresolved risks.
- Next recommended action.

## Open-Source Extraction Rules

When turning a local pipeline into a public repo:

- Replace local private paths with configurable environment variables.
- Replace private examples with synthetic fixtures.
- Exclude model files, generated sensitive outputs, copyrighted media, credentials, caches, and logs.
- Keep small scripts, generic workflow templates, test fixtures, and documentation.
- Include `README.md`, license, `CONTRIBUTING.md`, `SECURITY.md`, issue templates, PR template, tests, and an `AGENTS.md`.
- Add repo-local skills only when they teach reusable judgment that scripts cannot enforce.

## Common Mistakes

| Mistake | Correction |
|---|---|
| Running the full batch first | Start with an inventory and smoke gate |
| Treating VLM score as objective truth | Calibrate VLM observations against human ratings |
| Using one prompt/parameter set for all models | Verify per model family |
| Publishing local project files directly | Extract a clean public-safe subset |
| Writing reports nobody can resume from | End each run with paths, status, risks, and next action |
| Moving or deleting generated assets during cleanup | Ask explicit approval first |

## Pressure Scenarios

The skill should trigger and guide behavior for:

1. "I downloaded 12 models; check which ones are ready and run a benchmark."
2. "Use VLMs and taggers to score these generated assets and tell me the best candidates."
3. "Turn last month's asset pipeline and review work into an open-source GitHub project."
