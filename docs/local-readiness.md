# Local Readiness Check

Use the local readiness command before pushing, releasing, or preparing the Codex for OSS application:

```bash
asset-pipeline-steward readiness .
```

The command checks:

- required community health files;
- checked-in schema matches CLI-generated schema;
- all example manifests validate;
- repository public-safety scan passes;
- adoption evidence file exists and records public proof where available;
- git worktree exists, branch is `main`, worktree is clean, and `origin` is configured.

It also emits a warning that cannot be satisfied locally: the public GitHub repository, hosted CI run, release, and adoption evidence still need to be verified after push.

If the local checks pass but GitHub still shows no repository, follow `docs/github-publish-runbook.md`.
If the repository exists but Codex cannot see it through the GitHub connector, follow `docs/github-connector-setup.md`.

## JSON Output

```bash
asset-pipeline-steward readiness . --json
```

Use JSON output for automation or release scripts.

Use `asset-pipeline-steward evidence .` for a focused view of public adoption and maintainer evidence gaps.
