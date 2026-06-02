# AI Asset Pipeline Steward

[![CI](https://github.com/BigDragonDog123/ai-asset-pipeline-steward/actions/workflows/ci.yml/badge.svg)](https://github.com/BigDragonDog123/ai-asset-pipeline-steward/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/BigDragonDog123/ai-asset-pipeline-steward?sort=semver)](https://github.com/BigDragonDog123/ai-asset-pipeline-steward/releases)
[![License](https://img.shields.io/github/license/BigDragonDog123/ai-asset-pipeline-steward)](LICENSE)

AI Asset Pipeline Steward is a public-safe starter kit for maintaining AI-generated asset workflows without turning every experiment into an unrepeatable local script.

The project focuses on the boring parts that decide whether a creative or model-evaluation pipeline can be trusted:

- inventorying assets, workflows, dependencies, and review queues;
- checking model and workflow readiness before large runs;
- using small smoke gates before expensive batches;
- separating human review from automated observations;
- writing decision gates and handoffs that another maintainer can resume;
- extracting private local work into synthetic, publishable fixtures.

## Why This Exists

Many AI asset workflows start as local folders, one-off scripts, and ad-hoc reviews. That works for experiments, but it breaks down when the maintainer needs to compare models, rerun batches, explain review decisions, publish a clean repository, or let an agent continue the work safely.

This repository turns that repeated maintenance pattern into a small package, a repo-scoped Codex skill, and public documentation.

## For Reviewers

- Start with `docs/reviewer-brief.md`.
- Run the quickstart or skim `docs/terminal-examples.md`.
- Leave public feedback with the feedback issue form.

## Current Status

This is an alpha repository scaffold. It is intentionally small:

- a manifest validator for public-safe asset pipeline fixtures;
- a maintenance report command for handoffs and release notes;
- synthetic review, model-inventory, review-queue, and handoff-resume example manifests;
- a repo-local Codex skill at `.agents/skills/ai-asset-pipeline-steward`;
- GitHub community health files and CI;
- documentation for Codex for OSS readiness.

## Quickstart

```bash
python -m pip install -e .
asset-pipeline-steward schema
asset-pipeline-steward repo-scan .
asset-pipeline-steward readiness .
asset-pipeline-steward evidence .
asset-pipeline-steward application .
asset-pipeline-steward starter-issues .
asset-pipeline-steward examples/fixture_manifest.json
asset-pipeline-steward report examples/fixture_manifest.json
asset-pipeline-steward examples/model_inventory_manifest.json
asset-pipeline-steward examples/review_queue_manifest.json
asset-pipeline-steward examples/handoff_resume_manifest.json
python -m unittest discover -s tests
```

You can also run the validator without installing:

```bash
python -m asset_pipeline_steward.cli schema
python -m asset_pipeline_steward.cli repo-scan .
python -m asset_pipeline_steward.cli readiness .
python -m asset_pipeline_steward.cli evidence .
python -m asset_pipeline_steward.cli application .
python -m asset_pipeline_steward.cli starter-issues .
python -m asset_pipeline_steward.cli examples/fixture_manifest.json
python -m asset_pipeline_steward.cli report examples/fixture_manifest.json
```

## Manifest Shape

A public-safe manifest should include:

- `project`: name, description, status, and maintainer intent;
- `assets`: synthetic or publishable fixtures only;
- `models`: model references without bundling large model files;
- `workflows`: named workflow steps and preflight requirements;
- `review_signals`: human and automated review signals kept separate;
- `decision_gate`: what is ready, what is blocked, and what happens next.
- `handoff`: what a maintainer or agent needs to resume safely.

See `examples/fixture_manifest.json` for a minimal example.

See `examples/model_inventory_manifest.json` for a public-safe model inventory and smoke-gate example.

See `examples/review_queue_manifest.json` for a public-safe review queue and handoff example.

See `examples/handoff_resume_manifest.json` for a public-safe paused-batch resume example with progress, blockers, known unknowns, and next action fields.

## Validation Rules

The validator checks both public safety and basic maintainability:

- top-level manifest sections are present;
- project name, description, and status are not empty;
- workflow entries declare `name`, non-empty `steps`, and non-empty `preflight`;
- review signals include both `ground-truth` and `supporting-evidence` roles;
- decision gates include `status` and `next_action`;
- handoffs include `goal`, `current_status`, `next_action`, `blockers`, and `known_unknowns`;
- private paths, sensitive markers, and model weight file paths are blocked.

The JSON Schema lives at `schemas/asset-pipeline-manifest.schema.json` and can also be printed with `asset-pipeline-steward schema`.

## Codex Skill

Codex can load the repo-local skill from:

```text
.agents/skills/ai-asset-pipeline-steward/SKILL.md
```

Use it when a task involves AI-generated asset pipelines, model/workflow checks, VLM review, human rating, batch queues, dataset curation, or open-source extraction.

## Public Safety

This repository should never contain:

- credentials, tokens, `.env` files, or private keys;
- private local paths or user profile folders;
- generated outputs that cannot be published;
- copyrighted sample media;
- model weight files such as `.safetensors`, `.ckpt`, `.pt`, `.pth`, or `.onnx`;
- caches, logs, browser profiles, or large local artifacts.

Use synthetic fixtures when demonstrating behavior.

Run `asset-pipeline-steward repo-scan .` before publishing or opening a pull request.
Run `asset-pipeline-steward readiness .` before release or Codex for OSS application work.
Track public adoption and maintainer evidence in `docs/adoption-evidence.json`.

## Feedback

External feedback is especially useful while this project is early. If the workflow overlaps with your maintenance work, use the public feedback form:

```text
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml
```

See `docs/public-feedback-request.md` for a short request that can be shared with reviewers.
Use `docs/feedback-outreach-kit.md` for ready-to-send reviewer requests and evidence rules.
See `docs/reviewer-brief.md` for a one-page guide to what reviewers should try first.

## Codex For OSS Readiness

This project is being prepared as a candidate open-source direction. OpenAI's Codex for Open Source program asks for a public GitHub profile, a public repository, maintainer role, and evidence of usage, ecosystem importance, or active maintenance. This repository currently provides the structure and a plausible maintenance workflow, but it still needs public adoption evidence before a strong application.

See `docs/codex-for-oss-readiness.md`.
Use `docs/codex-for-oss-review-packet.md` for the current one-page application evidence summary.
Use `docs/codex-for-oss-submission-runbook.md` when the final external feedback URL and personal fields are ready.
Use `docs/github-publish-runbook.md` and `docs/github-connector-setup.md` for the GitHub publishing and ChatGPT/Codex connector steps.
Use `docs/maintainer-growth-plan.md` to track post-launch feedback, safe adoption signals, and next maintainer actions.
