# Maintainer Growth Plan

Status date: 2026-06-02.

This plan tracks the next credible public signals for AI Asset Pipeline Steward. The goal is real maintenance evidence, not vanity metrics.

## Submission Timing

Verified on 2026-06-02: the Codex for Open Source pages describe rolling review, not a fixed public deadline. The repository should stay in growth mode until it has at least one real external feedback or adoption signal.

Do not rush a weak application just because the application packet is ready. Submit only when the evidence file and final submission gate agree that the public signal is strong enough.

## Current Baseline

- Public repository: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward`
- Release: `v0.1.0`
- CI: passing on `main`
- Completed starter issues: issues #3 through #7
- Usage examples: `docs/terminal-examples.md` and `examples/`
- Adoption evidence file: `docs/adoption-evidence.json`
- Maintainer activity: starter issues completed, Dependabot PRs #1 and #2 merged, end-to-end maintainer-loop example added, and submission gates implemented.
- Open adoption task: issue #8 tracks the first external feedback signal.
- Open growth task: issue #9 tracks the 30-day GitHub growth loop before Codex for OSS submission.
- Feedback form: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml`
- Share request: `docs/public-feedback-request.md`
- Outreach kit: `docs/feedback-outreach-kit.md`
- Reviewer brief: `docs/reviewer-brief.md`
- Application review packet: `docs/codex-for-oss-review-packet.md`
- Repository discovery: README badges plus GitHub topics for public-safe AI asset pipeline maintenance.

## Signal Rules

- Do not record fake stars, fake forks, or private feedback.
- Prefer public feedback that a reviewer can open.
- Record only URLs that do not expose private paths, logs, credentials, local media, or non-public samples.
- Treat self-authored issues and releases as maintenance evidence, not external adoption.

## Growth Mode Targets

Minimum target before applying:

- one public non-maintainer feedback URL recorded in `docs/adoption-evidence.json`;
- one visible maintenance response to that feedback, such as an issue, fix, docs clarification, or roadmap decision;
- latest CI green after the response;
- `asset-pipeline-steward submission-ready .` blocked only by personal fields before manual confirmation, and `asset-pipeline-steward submission-ready . --manual-ready` passing when personal fields are ready.

Stronger target before applying:

- two or more public feedback links from different people or venues;
- at least one public downstream usage note, tutorial, or integration idea;
- a small follow-up release after feedback-driven changes;
- README and reviewer brief updated to reflect the feedback.

## Next 30 Days

1. Ask one real user or maintainer to try the reviewer brief and leave public feedback through the feedback form.
2. Send one message from `docs/feedback-outreach-kit.md` to a likely reviewer.
3. Publish one short public usage note that links to the repo, terminal examples, and feedback form.
4. Scan with `asset-pipeline-steward feedback-candidates`, then record any real external feedback URL with `asset-pipeline-steward record-feedback`.
5. Turn the first concrete critique into a visible issue or small PR.
6. Ship one feedback-driven docs or validation improvement.
7. Consider a small `v0.1.1` release only after feedback produces a meaningful improvement.
8. Close issue #8 after the external feedback URL is recorded and evidence passes.
9. Review `docs/codex-for-oss-review-packet.md` to confirm the current evidence and remaining weaknesses.
10. Use `docs/codex-for-oss-submission-runbook.md` only after the growth target is met.
11. Re-run:

```bash
asset-pipeline-steward evidence .
asset-pipeline-steward readiness .
asset-pipeline-steward application .
asset-pipeline-steward submission-ready . --manual-ready
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
- `stars` and `forks`: current public GitHub values, refreshed by `asset-pipeline-steward record-feedback` when the GitHub API is available.
