# Agent Instructions

Use this repository as a public-safe open-source project. Keep work focused on reusable AI asset pipeline stewardship, not private local projects.

## Required Skills

- Use `evidence-first-workflow` before non-trivial design, implementation, tool choice, documentation, or Codex for OSS strategy work.
- Use `.agents/skills/ai-asset-pipeline-steward` for asset pipeline, model/workflow verification, batch queue, VLM review, human review, dataset curation, or public extraction tasks.

## Safety Rules

- Do not read or publish `.env`, token files, private keys, browser profiles, private logs, private media, or non-public generated outputs unless the user explicitly authorizes it and the task requires it.
- Do not add model weight files or large media artifacts to the repo.
- Use synthetic fixtures and configurable paths.
- Before public-facing changes, scan for private paths, credentials, non-public project names, and restricted samples.

## Commands

```bash
python -m unittest discover -s tests
python -m asset_pipeline_steward.cli repo-scan .
python -m asset_pipeline_steward.cli readiness .
python -m asset_pipeline_steward.cli evidence .
python -m asset_pipeline_steward.cli application .
python -m asset_pipeline_steward.cli codex-oss-status .
python -m asset_pipeline_steward.cli public-usage-note .
python -m asset_pipeline_steward.cli starter-issues .
python -m asset_pipeline_steward.cli examples/fixture_manifest.json
```

## Maintenance Style

- Prefer small, reviewable changes.
- Keep dependencies minimal.
- Explain whether a new approach is Adopt, Extend, Compose, or Build.
- Verify the specific completion claim before reporting done.
