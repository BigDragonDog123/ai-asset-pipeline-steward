# Codex For OSS Review Packet

Status date: 2026-06-02.

Use this one-page packet before submitting the official Codex for Open Source form:

```text
https://openai.com/form/codex-for-oss/
```

## Official Fit

The official form asks for a public GitHub username, public repository URL, maintainer role, qualification summary, OpenAI Organization ID, and optional interest in Codex Security or API credits.

The program says applications are reviewed on a rolling basis and looks for active open-source maintainers with meaningful usage, broad adoption, clear ecosystem importance, and active maintenance work such as pull request review, issue triage, release management, security, and code quality.

## Current Public Evidence

- Repository: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward`
- Visibility: public
- Role: primary maintainer
- Release: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/releases/tag/v0.1.0`
- Recorded CI evidence: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/actions/runs/26829604231`
- Open PRs: none, verified on 2026-06-02
- Open adoption task: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/8`
- Completed starter issues: #3 through #7
- Merged maintenance PRs: #1 and #2
- Usage examples: `docs/terminal-examples.md` and `examples/`
- Public usage note: `docs/public-usage-note.md`
- End-to-end walkthrough: `docs/end-to-end-maintainer-loop.md`
- Review landing: `REVIEW.md`
- Reviewer brief: `docs/reviewer-brief.md`
- Feedback request: `docs/public-feedback-request.md`
- First feedback playbook: `docs/first-feedback-playbook.md`
- Feedback response playbook: `docs/feedback-response-playbook.md`
- Outreach kit: `docs/feedback-outreach-kit.md`
- Outreach tracker: `docs/outreach-tracker.md`
- Growth status command: `asset-pipeline-steward codex-oss-status . --manual-ready`

## Current Weaknesses

- No external feedback URL is recorded yet.
- Current public GitHub stars: 0.
- Current public forks: 0.
- The strongest application path is to collect at least one public comment, issue, forum post, social post, or downstream usage link from someone other than the maintainer before submitting.
- `docs/outreach-tracker.md` is planning evidence only; it must not be counted as external adoption.

## Public-Safety Statement

The repository is designed as a public-safe extraction of local AI asset maintenance work. It uses synthetic fixtures and excludes credentials, private paths, model weights, generated private media, logs, caches, browser profiles, and non-public samples.

Do not commit first name, last name, ChatGPT email, OpenAI Organization ID, application confirmation emails, or private feedback.

## Copy-Paste Form Values

GitHub username:

```text
BigDragonDog123
```

GitHub repository URL:

```text
https://github.com/BigDragonDog123/ai-asset-pipeline-steward
```

Role:

```text
Primary maintainer
```

Interest:

```text
API credits for my project
```

Codex Security:

```text
Maybe, after public usage evidence exists
```

Why does this repository qualify? Maximum 500 characters:

```text
AI Asset Pipeline Steward turns repeated local AI-asset maintenance into a public-safe OSS workflow: manifests, repo scans, synthetic fixtures, CI, release evidence, feedback intake, and final submission gates. It shows active maintainer work through issue triage, PR maintenance, an end-to-end review/handoff scenario, and tools for recording external adoption without leaking private data.
```

How will you use API credits for your project? Maximum 500 characters:

```text
Use credits to build Codex maintainer automation around real OSS workflows: review manifest/schema PRs, triage feedback issues, test release and submission gates, collect adoption evidence, expand synthetic fixtures, and run public-safety checks. Credits would let the project validate agent-assisted maintenance loops instead of only static documentation.
```

Anything else we should know? Maximum 500 characters:

```text
The repo is intentionally public-safe: no private paths, credentials, model weights, logs, caches, or non-public media. Current evidence includes green CI, v0.1.0, completed starter issues, merged maintenance PRs, an end-to-end maintainer-loop example, structured feedback intake, and strict gates that still block submission until external feedback is recorded.
```

## Submission Gate

Submit only when:

- latest GitHub Actions on `main` is green;
- `asset-pipeline-steward repo-scan .` passes;
- `asset-pipeline-steward readiness .` has no unexpected blocker;
- `asset-pipeline-steward codex-oss-status . --manual-ready` no longer reports growth mode;
- `asset-pipeline-steward submission-ready . --manual-ready` passes immediately before form entry;
- a real external feedback URL is recorded, or the weaker application is intentional;
- personal fields are filled in the official form only, not committed to this repository.
