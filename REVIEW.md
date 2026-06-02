# Review This Project

AI Asset Pipeline Steward needs public feedback from people other than the maintainer. A useful review can be short: one concrete adoption blocker, unclear field, missing validation rule, or workflow mismatch is enough.

## 10-Minute Review

1. Read `docs/reviewer-brief.md`.
2. Skim `examples/handoff_resume_manifest.json`.
3. Leave one public feedback issue:

```text
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml
```

The feedback form asks you to confirm that the public issue URL may be recorded as external feedback evidence. That helps the maintainer use the feedback without copying private details.

## 20-Minute Review

From a fresh clone:

```bash
python -m pip install -e .
asset-pipeline-steward repo-scan .
asset-pipeline-steward readiness .
asset-pipeline-steward report examples/handoff_resume_manifest.json
```

Then leave what worked, what was unclear, and one concrete improvement request in the feedback issue form.

## 40-Minute Maintainer Review

1. Read `docs/end-to-end-maintainer-loop.md`.
2. Compare the manifest shape with a real workflow without sharing private data.
3. Identify one missing field, validation rule, report section, or handoff rule.
4. Leave public feedback with the feedback issue form.

## Public-Safety Rule

Do not include private paths, logs, credentials, tokens, model files, generated private media, or non-public samples in feedback.

## Useful Links

- Reviewer brief: `docs/reviewer-brief.md`
- Reviewer checklist: `docs/reviewer-checklist.md`
- Terminal examples: `docs/terminal-examples.md`
- Public feedback request: `docs/public-feedback-request.md`
- Feedback form: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml`
