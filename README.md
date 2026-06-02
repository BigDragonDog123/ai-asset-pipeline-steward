# AI Asset Pipeline Steward

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

## Current Status

This is an alpha repository scaffold. It is intentionally small:

- a manifest validator for public-safe asset pipeline fixtures;
- a synthetic example manifest;
- a repo-local Codex skill at `.agents/skills/ai-asset-pipeline-steward`;
- GitHub community health files and CI;
- documentation for Codex for OSS readiness.

## Quickstart

```bash
python -m pip install -e .
asset-pipeline-steward examples/fixture_manifest.json
python -m unittest discover -s tests
```

You can also run the validator without installing:

```bash
python -m asset_pipeline_steward.cli examples/fixture_manifest.json
```

## Manifest Shape

A public-safe manifest should include:

- `project`: name, description, status, and maintainer intent;
- `assets`: synthetic or publishable fixtures only;
- `models`: model references without bundling large model files;
- `workflows`: named workflow steps and preflight requirements;
- `review_signals`: human and automated review signals kept separate;
- `decision_gate`: what is ready, what is blocked, and what happens next.

See `examples/fixture_manifest.json` for a minimal example.

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

## Codex For OSS Readiness

This project is being prepared as a candidate open-source direction. OpenAI's Codex for Open Source program asks for a public GitHub profile, a public repository, maintainer role, and evidence of usage, ecosystem importance, or active maintenance. This repository currently provides the structure and a plausible maintenance workflow, but it still needs public adoption evidence before a strong application.

See `docs/codex-for-oss-readiness.md`.
