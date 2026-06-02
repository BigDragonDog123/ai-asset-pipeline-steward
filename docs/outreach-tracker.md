# Outreach Tracker

Use this tracker during the 30-day growth loop. It should help collect real feedback without storing private contact data in the repository.

Do not record names, private emails, private chat handles, private DMs, private screenshots, private logs, or non-public comments here. Record only reviewer profile, outreach status, public-safe next action, and public feedback URL after feedback is posted.

## Status Values

- `planned`: reviewer profile identified, not contacted yet.
- `sent`: public-safe request sent outside this repository.
- `reviewing`: reviewer said they may look.
- `feedback-posted`: public feedback URL exists.
- `recorded`: feedback was reviewed and added to `docs/adoption-evidence.json`.
- `declined`: reviewer declined or the workflow did not fit.
- `stale`: no response after a reasonable follow-up window.

## Reviewer Slots

| Slot | Reviewer Profile | Review Path | Status | Public Feedback URL | Next Action |
|---|---|---|---|---|---|
| R1 | AI image/audio/video workflow maintainer | 10-minute skim | planned |  | Send short request from `docs/feedback-outreach-kit.md`. |
| R2 | Dataset, benchmark, or review-queue maintainer | 20-minute quickstart | planned |  | Send reviewer checklist and ask for one blocker. |
| R3 | Open-source maintainer using CI, releases, or issue triage | 40-minute maintainer review | planned |  | Ask whether report/handoff output would fit maintenance work. |

## Public Request Links

- Reviewer checklist: `docs/reviewer-checklist.md`
- Reviewer brief: `docs/reviewer-brief.md`
- Public feedback request: `docs/public-feedback-request.md`
- Outreach kit: `docs/feedback-outreach-kit.md`
- Feedback form: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml`

## After Feedback Appears

1. Confirm the author is not the maintainer.
2. Confirm the feedback URL is public and reviewer-accessible.
3. Confirm the reviewer allowed the public issue URL to be recorded as external feedback evidence.
4. Confirm the feedback does not expose private paths, credentials, logs, model files, or non-public media.
5. Record it:

```bash
asset-pipeline-steward record-feedback <public-feedback-url>
asset-pipeline-steward evidence .
```

6. Turn one concrete critique into a visible issue, docs clarification, validation change, or roadmap decision.
7. Update this tracker status to `recorded`.

## Submission Rule

Do not use this tracker itself as external adoption evidence. It is maintainer planning evidence. Only public URLs from non-maintainers should be recorded in `external_feedback_urls`.
