# Adoption Evidence

Codex for OSS applications need credible public maintainer evidence. This repository tracks that evidence in:

```text
docs/adoption-evidence.json
```

Run:

```bash
asset-pipeline-steward evidence .
```

The command reports which public evidence has been recorded:

- public GitHub repository URL;
- hosted CI run URLs;
- release URLs;
- roadmap issue URLs;
- external feedback URLs;
- usage example URLs;
- stars and forks.

Warnings are expected before the repository is public. After push, fill the JSON file with public URLs and run:

```bash
asset-pipeline-steward collect-evidence .
asset-pipeline-steward readiness .
asset-pipeline-steward evidence .
```

`collect-evidence` reads the public GitHub API and prints a reviewed JSON starting point for `docs/adoption-evidence.json`. It does not modify files automatically.
If GitHub returns a rate-limit `403`, set `GITHUB_TOKEN` to a token with public repository read access and rerun the command.

Do not record private user data, private logs, credentials, or non-public samples.
