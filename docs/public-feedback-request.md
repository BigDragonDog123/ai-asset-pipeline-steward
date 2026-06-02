# Public Feedback Request

AI Asset Pipeline Steward needs one or more public feedback links from people other than the maintainer. Use this page when asking someone to try the repo, skim the examples, or leave a short issue.

For the shortest reviewer-facing path, use `REVIEW.md`. For the shortest public post draft, use `docs/public-usage-note.md`. For the shortest maintainer action plan, use `docs/first-feedback-playbook.md`. For longer English/Chinese messages, review paths, and evidence rules, use `docs/feedback-outreach-kit.md`. For a direct checklist, use `docs/reviewer-checklist.md`.

To print the concise first-feedback plan from the CLI, run:

```bash
asset-pipeline-steward first-feedback-playbook .
```

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

I would value external feedback on whether the manifest checks, report output, and handoff examples are understandable enough for another maintainer to use. The feedback form asks for one concrete adoption blocker or missing rule.

Useful links:
- Review landing: https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/REVIEW.md
- Public usage note: https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/docs/public-usage-note.md
- Quickstart: https://github.com/BigDragonDog123/ai-asset-pipeline-steward#quickstart
- Reviewer checklist: https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/docs/reviewer-checklist.md
- Terminal examples: https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/docs/terminal-examples.md
- Reviewer brief: https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/docs/reviewer-brief.md
- Feedback form: https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml

If you clone the repo, `asset-pipeline-steward reviewer-checklist .` prints 10-minute, 20-minute, and 40-minute review paths.
```

The feedback form asks reviewers to confirm that the public issue URL may be recorded as external feedback evidence. Do not copy private feedback, DMs, screenshots, or contact details into the repository.

## Recording Feedback

After a public feedback link exists:

1. Scan for non-maintainer feedback candidates:

```bash
asset-pipeline-steward feedback-candidates .
```

2. Record the reviewed URL:

```bash
asset-pipeline-steward record-feedback https://example.com/public-feedback-url
```

3. If the command prints a warning, manually review current public GitHub metrics before submitting.
4. Re-run:

```bash
asset-pipeline-steward evidence .
asset-pipeline-steward readiness .
asset-pipeline-steward application .
```

5. Close issue #8 once external feedback passes the evidence check.

Use `docs/outreach-tracker.md` to track reviewer slots and status without storing private contact details.
