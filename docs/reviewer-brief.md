# Reviewer Brief

This brief is for someone reviewing AI Asset Pipeline Steward for the first time.

## What This Project Is

AI Asset Pipeline Steward is a small public-safe toolkit for maintainers who need to turn local AI asset workflows into repeatable, reviewable, and publishable maintenance records.

It focuses on:

- public-safe manifest validation;
- model and workflow readiness checks before scaling;
- separated human and automated review signals;
- decision gates and resumable handoffs;
- synthetic examples that do not expose private paths, logs, model weights, credentials, or non-public media.

## What To Try First

For the shortest path, start with `REVIEW.md`.

From a fresh clone:

```bash
python -m pip install -e .
asset-pipeline-steward repo-scan .
asset-pipeline-steward readiness .
asset-pipeline-steward examples/handoff_resume_manifest.json
asset-pipeline-steward report examples/handoff_resume_manifest.json
```

Expected result:

- the repository scan passes;
- readiness has no blockers except intentionally tracked early adoption warnings;
- the handoff resume manifest validates;
- the report shows inventory, workflows, review signals, decision gate, and handoff sections.

## Useful Files To Skim

- `README.md`
- `docs/terminal-examples.md`
- `docs/end-to-end-maintainer-loop.md`
- `docs/public-extraction-tutorial.md`
- `examples/handoff_resume_manifest.json`
- `examples/end_to_end_maintainer_loop_manifest.json`
- `.agents/skills/ai-asset-pipeline-steward/SKILL.md`

## Feedback That Helps

Useful public feedback can be short. Good examples:

- "The quickstart worked, but the handoff fields were unclear because..."
- "The public extraction tutorial helped me understand keep/replace/exclude decisions."
- "I would need a validation rule for..."
- "This does not fit my workflow because..."

For direct review paths, use `docs/reviewer-checklist.md`. If you have more time or need shareable messages, use `docs/feedback-outreach-kit.md`.

The feedback form asks for the review path, what was tried, what seemed useful, and one concrete adoption blocker. That shape is intentional: specific critique is more useful than general approval.

## Public Safety

Do not include:

- private local paths;
- credentials, tokens, or `.env` contents;
- logs, browser profiles, caches, or generated private outputs;
- model weights or large binary artifacts;
- copyrighted or non-public media.

Use the feedback form:

```text
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml
```
