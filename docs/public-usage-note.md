# Public Usage Note

Use this note when posting publicly about AI Asset Pipeline Steward. It should invite real feedback without treating maintainer-authored text as external adoption evidence.

Repository:

```text
https://github.com/BigDragonDog123/ai-asset-pipeline-steward
```

## Short Note

```text
I published AI Asset Pipeline Steward, a small public-safe toolkit for turning local AI asset workflows into repeatable maintainer records:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward

It validates synthetic/public-safe manifests, separates human review from automated observations, and keeps batch or review handoffs resumable.

If this overlaps with your workflow, the fastest review path is here:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/REVIEW.md

Useful feedback is one concrete blocker, unclear field, missing validation rule, or reason it does not fit your workflow.
```

## Longer Note

```text
AI Asset Pipeline Steward is a public-safe starter kit for maintainers who need to turn local AI image, audio, video, dataset, benchmark, or review queues into repeatable records.

The current alpha focuses on synthetic manifests, public-safety scanning, model/workflow readiness, human-vs-automated review signals, decision gates, and handoffs another maintainer or coding agent can resume.

Try the terminal examples or skim the end-to-end maintainer loop, then leave one public feedback issue with a concrete adoption blocker or missing rule.
```

## Links

- Review landing: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/REVIEW.md`
- Terminal examples: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/docs/terminal-examples.md`
- End-to-end loop: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/docs/end-to-end-maintainer-loop.md`
- Feedback form: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml`

## Public Safety

- Do not include private paths, logs, credentials, model files, generated private media, or non-public samples.
- Do not paste private DMs, screenshots, or contact details into the repository.
- Treat this maintainer-authored note as outreach material, not external adoption evidence.

## After Posting

1. Wait for a public response or feedback issue from someone other than the maintainer.
2. Run `asset-pipeline-steward feedback-candidates .`.
3. Record only reviewed public-safe URLs with `asset-pipeline-steward record-feedback <public-feedback-url>`.
4. Run `asset-pipeline-steward feedback-response-playbook .` and turn one concrete critique into a visible issue, docs change, validation rule, release note, or roadmap decision.

The same note can be printed from a clone:

```bash
asset-pipeline-steward public-usage-note .
```
