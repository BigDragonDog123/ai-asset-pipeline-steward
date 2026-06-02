# Reviewer Checklist

Use this checklist when reviewing AI Asset Pipeline Steward for the first time. Pick the smallest path that fits your time. Specific critique is more useful than general praise.

Repository:

```text
https://github.com/BigDragonDog123/ai-asset-pipeline-steward
```

## 10-Minute Skim

Use this if you only have time to read.

1. Read `docs/reviewer-brief.md`.
2. Skim `examples/handoff_resume_manifest.json`.
3. Check whether the handoff fields are understandable.
4. Leave one concrete feedback issue.

## 20-Minute Quickstart

Use this if you can clone the repository.

```bash
python -m pip install -e .
asset-pipeline-steward repo-scan .
asset-pipeline-steward readiness .
asset-pipeline-steward report examples/handoff_resume_manifest.json
```

Then leave feedback on:

- what worked;
- what was unclear;
- which field, validation rule, or report section would block adoption.

## 40-Minute Maintainer Review

Use this if you maintain an AI image, audio, video, dataset, benchmark, generated-asset review, or long-running agent workflow.

1. Read `docs/end-to-end-maintainer-loop.md`.
2. Compare the manifest shape against one real workflow without sharing private data.
3. Identify one missing field, validation rule, report section, or handoff rule.
4. Leave a public feedback issue or public comment.

## Useful Feedback

Good feedback includes one concrete item:

- unclear field;
- missing validation rule;
- weak report output;
- adoption blocker;
- reason this does not fit a real workflow.

## Public Safety

Do not include:

- private paths;
- logs, credentials, tokens, or `.env` contents;
- model files;
- generated private media;
- non-public samples.

## Feedback Form

```text
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml
```

## Maintainer Follow-Up

After public feedback appears, the maintainer should run:

```bash
asset-pipeline-steward feedback-candidates .
asset-pipeline-steward record-feedback <public-feedback-url>
asset-pipeline-steward evidence .
```

The same checklist can be printed from a clone:

```bash
asset-pipeline-steward reviewer-checklist .
```
