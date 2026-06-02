# First Feedback Playbook

Use this playbook to collect the first real public feedback signal for AI Asset Pipeline Steward.

The goal is not praise. The goal is one public, non-maintainer feedback URL that identifies a concrete usability gap, missing rule, unclear field, or adoption blocker.

Repository:

```text
https://github.com/BigDragonDog123/ai-asset-pipeline-steward
```

## Reviewer Profiles

### AI Asset Workflow Maintainer

- Ask: 10-minute skim of the reviewer brief and handoff example.
- Best feedback: one unclear field, missing rule, or adoption blocker.

### Dataset, Benchmark, Or Review-Queue Maintainer

- Ask: 20-minute quickstart and one report command.
- Best feedback: whether the manifest and report output fit a real maintenance workflow.

### Open-Source Maintainer

- Ask: 40-minute maintainer review of the end-to-end loop.
- Best feedback: what would make the workflow easier to review, release, or hand off.

## Send Sequence

1. Pick one reviewer profile.
2. Send the short request below.
3. Ask for a public issue or public comment, not private praise.
4. Wait for a concrete critique before recording evidence.
5. Record only a public-safe URL from someone other than the maintainer.

## Short Request

```text
I published a small public-safe toolkit for AI asset pipeline maintenance:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward

Could you give it a 10-minute skim and leave one public feedback issue? The useful answer is one concrete adoption blocker, unclear field, or missing rule.

Start here:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/REVIEW.md

Feedback form:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml

Please do not include private paths, logs, credentials, model files, or non-public media.
```

## Public Links

- Review landing: `REVIEW.md`
- Reviewer brief: `docs/reviewer-brief.md`
- Reviewer checklist: `docs/reviewer-checklist.md`
- Outreach kit: `docs/feedback-outreach-kit.md`
- Feedback form: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml`

## Valid Feedback Rules

A feedback URL counts only when:

- the author is not the maintainer;
- the URL is public or accessible to an application reviewer;
- the content discusses this repository or workflow;
- the reviewer confirms that the public issue URL may be recorded as external feedback evidence;
- the content does not expose private paths, credentials, logs, model files, or non-public media.

## Maintainer Follow-Up

After public feedback appears:

```bash
asset-pipeline-steward feedback-candidates .
asset-pipeline-steward record-feedback <public-feedback-url>
asset-pipeline-steward feedback-response-playbook .
asset-pipeline-steward evidence .
asset-pipeline-steward submission-ready . --manual-ready
```

If GitHub returns a rate-limit `403` while scanning candidates or checking authors, set `GITHUB_TOKEN` to a token with public repository read access and rerun the command. Do not commit the token.

The same playbook can be printed from a clone:

```bash
asset-pipeline-steward first-feedback-playbook .
```
