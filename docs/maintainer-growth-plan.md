# Maintainer Growth Plan

Status date: 2026-06-02.

This plan tracks the next credible public signals for AI Asset Pipeline Steward. The goal is real maintenance evidence, not vanity metrics.

## Submission Timing

Verified on 2026-06-02: the Codex for Open Source pages describe rolling review, not a fixed public deadline. The repository should stay in growth mode until it has at least one real external feedback or adoption signal.

Do not rush a weak application just because the application packet is ready. Submit only when the evidence file and final submission gate agree that the public signal is strong enough.

## Current Baseline

- Public repository: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward`
- Release: `v0.1.0`
- CI: passing on `main`; latest verified public run is `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/actions/runs/26829719474`
- Completed starter issues: issues #3 through #7
- Usage examples: `docs/terminal-examples.md` and `examples/`
- Adoption evidence file: `docs/adoption-evidence.json`
- Maintainer activity: starter issues completed, Dependabot PRs #1 and #2 merged, end-to-end maintainer-loop example added, and submission gates implemented.
- Open adoption task: issue #8 tracks the first external feedback signal.
- Open growth task: issue #9 tracks the 30-day GitHub growth loop before Codex for OSS submission.
- Feedback form: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml`
- Share request: `docs/public-feedback-request.md`
- Outreach kit: `docs/feedback-outreach-kit.md`
- Outreach tracker: `docs/outreach-tracker.md`
- Reviewer brief: `docs/reviewer-brief.md`
- Application review packet: `docs/codex-for-oss-review-packet.md`
- Repository discovery: README badges plus GitHub topics for public-safe AI asset pipeline maintenance.

## Current Gate Snapshot

Verified on 2026-06-02:

- `python -m pytest -q` passes with 44 tests and 5 subtests.
- `python -m asset_pipeline_steward.cli repo-scan .` passes public-safety checks.
- `python -m asset_pipeline_steward.cli readiness .` passes required files, schemas, examples, repo scan, git branch, clean status, and remote checks.
- `python -m asset_pipeline_steward.cli evidence .` still warns that `external_feedback_urls` is `0/1`, with 0 stars and 0 forks.
- `python -m asset_pipeline_steward.cli feedback-candidates .` finds no non-maintainer feedback comments yet.
- `python -m asset_pipeline_steward.cli submission-ready . --manual-ready` remains intentionally blocked only because no real public external feedback URL has been recorded.

This means the repo is technically prepared for review, but the application should stay in growth mode until a public non-maintainer feedback URL exists.

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
3. Track only public-safe reviewer status in `docs/outreach-tracker.md`; do not record private contact details.
4. Publish one short public usage note that links to the repo, terminal examples, and feedback form.
5. Scan with `asset-pipeline-steward feedback-candidates`, then record any real external feedback URL with `asset-pipeline-steward record-feedback`.
6. Turn the first concrete critique into a visible issue or small PR.
7. Ship one feedback-driven docs or validation improvement.
8. Consider a small `v0.1.1` release only after feedback produces a meaningful improvement.
9. Close issue #8 after the external feedback URL is recorded and evidence passes.
10. Review `docs/codex-for-oss-review-packet.md` to confirm the current evidence and remaining weaknesses.
11. Use `docs/codex-for-oss-submission-runbook.md` only after the growth target is met.
12. Re-run:

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
