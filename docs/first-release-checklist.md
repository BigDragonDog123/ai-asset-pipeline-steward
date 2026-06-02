# First Release Checklist

Use this after the repository has been pushed to GitHub.

## Preflight

- GitHub repository is public.
- Default branch is `main`.
- CI passes on GitHub.
- Community Standards page shows README, license, contributing guide, code of conduct, and security policy.
- No secrets, private paths, model files, logs, caches, or non-public samples are present.

## Local Fresh-Clone Check

From a fresh clone:

```bash
python -m pip install -e .
asset-pipeline-steward schema
asset-pipeline-steward repo-scan .
asset-pipeline-steward readiness .
asset-pipeline-steward evidence .
asset-pipeline-steward starter-issues .
asset-pipeline-steward examples/fixture_manifest.json
asset-pipeline-steward examples/model_inventory_manifest.json
asset-pipeline-steward examples/review_queue_manifest.json
asset-pipeline-steward report examples/fixture_manifest.json
asset-pipeline-steward report examples/model_inventory_manifest.json
asset-pipeline-steward report examples/review_queue_manifest.json
python -m unittest discover -s tests
```

## Release Notes

Title:

```text
v0.1.0 - Public scaffold
```

Body:

```text
Initial public release of AI Asset Pipeline Steward.

Highlights:
- Public-safe manifest validator.
- Maintainer report command.
- Synthetic review, model-inventory, and review-queue manifests.
- Maintainability checks for workflow preflight, review-signal roles, decision gates, and handoffs.
- Repo-scoped Codex skill for AI asset pipeline stewardship.
- GitHub community health files, CI, and Codex for OSS readiness docs.

This release uses only synthetic examples and does not include model files, private paths, credentials, logs, caches, or non-public media.
```

## After Release

- Open the starter issues in docs/starter-issues.md.
- Link the release in docs/codex-for-oss-readiness.md.
- Record public URLs in docs/adoption-evidence.json.
- Wait for at least some public activity before submitting the Codex for OSS form.
