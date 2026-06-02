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
asset-pipeline-steward readiness .
asset-pipeline-steward evidence .
```

Do not record private user data, private logs, credentials, or non-public samples.
