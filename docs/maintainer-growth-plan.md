# Maintainer Growth Plan

Status date: 2026-06-02.

This plan tracks the next credible public signals for AI Asset Pipeline Steward. The goal is real maintenance evidence, not vanity metrics.

## Current Baseline

- Public repository: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward`
- Release: `v0.1.0`
- CI: passing on `main`
- Starter issues: issues #3 through #7
- Usage examples: `docs/terminal-examples.md` and `examples/`
- Adoption evidence file: `docs/adoption-evidence.json`

## Signal Rules

- Do not record fake stars, fake forks, or private feedback.
- Prefer public feedback that a reviewer can open.
- Record only URLs that do not expose private paths, logs, credentials, local media, or non-public samples.
- Treat self-authored issues and releases as maintenance evidence, not external adoption.

## Next Seven Days

1. Complete one small post-launch issue and close it with a linked commit.
2. Review Dependabot PRs and merge safe updates.
3. Ask one real user or maintainer to try the quickstart and leave public feedback.
4. Publish one short public usage note that links to the repo and terminal examples.
5. Add any real external feedback URL to `docs/adoption-evidence.json`.
6. Re-run:

```bash
asset-pipeline-steward evidence .
asset-pipeline-steward readiness .
asset-pipeline-steward application .
```

## Feedback Request Template

```text
I published a small public-safe tool for AI asset pipeline maintenance:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward

It validates synthetic/public-safe manifests, separates human review from automated notes, and keeps handoffs resumable for maintainers and coding agents.

If this overlaps with your workflow, could you try the quickstart or skim the examples and leave feedback in an issue or public comment?
```

## Record Evidence

After feedback appears, update `docs/adoption-evidence.json`:

- `external_feedback_urls`: public comments, issue links, forum posts, or social posts;
- `usage_example_urls`: public demos, downstream examples, or tutorials;
- `stars` and `forks`: current public GitHub values.
