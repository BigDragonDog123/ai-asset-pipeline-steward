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
- git worktree exists, branch is `main`, worktree is clean, and `origin` is configured.

It also emits a warning that cannot be satisfied locally: the public GitHub repository, hosted CI run, release, and adoption evidence still need to be verified after push.

## JSON Output

```bash
asset-pipeline-steward readiness . --json
```

Use JSON output for automation or release scripts.
