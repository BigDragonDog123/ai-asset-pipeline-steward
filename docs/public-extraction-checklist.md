# Public Extraction Checklist

Use this checklist before moving any local AI asset workflow into the public repository.

## Keep

- Small scripts with generic behavior.
- Synthetic JSON fixtures.
- Public-safe documentation.
- Repo-scoped Codex skills.
- Tests that use synthetic data.
- Configuration examples without secrets.

## Replace

- Absolute local paths with environment variables or relative fixture paths.
- Private output examples with synthetic placeholders.
- Project-specific names with neutral labels.
- Long logs with short summaries.
- Real model references with external-reference-only metadata.

## Exclude

- Credentials, tokens, passwords, private keys, and `.env` files.
- Private local paths and user profile folders.
- Browser profiles, caches, checkpoints, logs, and temporary files.
- Model weight files and large binaries.
- Copyrighted or non-public sample media.
- Generated outputs that are not clearly publishable.

## Verification

Before publishing:

```bash
python -m unittest discover -s tests
asset-pipeline-steward repo-scan .
python -m asset_pipeline_steward.cli examples/fixture_manifest.json
rg -n "C:\\\\|E:\\\\|/Users/|AppData|token|secret|password|private_key|\\.env" .
```
