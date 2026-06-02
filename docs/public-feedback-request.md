# Public Feedback Request

AI Asset Pipeline Steward needs one or more public feedback links from people other than the maintainer. Use this page when asking someone to try the repo, skim the examples, or leave a short issue.

## Short Request

```text
I published a small public-safe toolkit for AI asset pipeline maintenance:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward

It validates synthetic/public-safe manifests, separates human review from automated notes, and keeps handoffs resumable for maintainers and coding agents.

If this overlaps with your workflow, could you try the README quickstart or skim the examples and leave a short feedback issue?

Feedback form:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml
```

## Longer Request

```text
I am preparing AI Asset Pipeline Steward as a public open-source maintainer workflow:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward

The repo is intentionally public-safe. It does not include model weights, private paths, logs, credentials, or non-public media. The examples are synthetic fixtures for review queues, model inventory, and resumable handoffs.

I would value external feedback on whether the manifest checks, report output, and handoff examples are understandable enough for another maintainer to use.

Useful links:
- Quickstart: https://github.com/BigDragonDog123/ai-asset-pipeline-steward#quickstart
- Terminal examples: https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/docs/terminal-examples.md
- Feedback form: https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml
```

## Recording Feedback

After a public feedback link exists:

1. Add it to `external_feedback_urls` in `docs/adoption-evidence.json`.
2. Re-run:

```bash
asset-pipeline-steward evidence .
asset-pipeline-steward readiness .
asset-pipeline-steward application .
```

3. Close issue #8 once external feedback passes the evidence check.
