# Codex For OSS Application Draft

Status date: 2026-06-02.

This draft is ready for manual form entry after personal fields are filled. The remaining strategic weakness is early public adoption: external feedback, stars, forks, or a public downstream use case would make the application stronger.

Machine-readable source:

```text
docs/codex-for-oss-application.json
```

Render and check the packet with:

```bash
asset-pipeline-steward application .
```

## Fields

First name:

- Fill manually.

Last name:

- Fill manually.

Email:

- Use the email associated with the ChatGPT account.

GitHub username:

- `BigDragonDog123`

GitHub repository URL:

- `https://github.com/BigDragonDog123/ai-asset-pipeline-steward`

Role:

- Primary maintainer.

Why does this repository qualify? Maximum 500 characters.

```text
AI Asset Pipeline Steward turns repeated local AI-asset maintenance into a public-safe OSS workflow: manifests, repo scans, synthetic fixtures, CI, release evidence, feedback intake, and final submission gates. It shows active maintainer work through issue triage, PR maintenance, an end-to-end review/handoff scenario, and tools for recording external adoption without leaking private data.
```

Interest:

- Codex Security: maybe, after the repo has public usage.
- API credits: yes, for maintainer workflow automation.

OpenAI Organization ID:

- Fill manually from https://platform.openai.com/settings/organization/general

How will you use API credits for your project? Maximum 500 characters.

```text
Use credits to build Codex maintainer automation around real OSS workflows: review manifest/schema PRs, triage feedback issues, test release and submission gates, collect adoption evidence, expand synthetic fixtures, and run public-safety checks. Credits would let the project validate agent-assisted maintenance loops instead of only static documentation.
```

Anything else we should know? Maximum 500 characters.

```text
The repo is intentionally public-safe: no private paths, credentials, model weights, logs, caches, or non-public media. Current evidence includes green CI, v0.1.0, completed starter issues, merged maintenance PRs, an end-to-end maintainer-loop example, structured feedback intake, and strict gates that still block submission until external feedback is recorded.
```

## Current Public Evidence

- Public repository: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward`
- Passing CI: tracked in `docs/adoption-evidence.json`
- First release: `v0.1.0`
- Completed starter issues: issues #3 through #7
- Merged maintenance PRs: #1 and #2
- Usage examples: `docs/terminal-examples.md` and `examples/`
- End-to-end maintainer loop: `docs/end-to-end-maintainer-loop.md`
- Structured feedback intake: `.github/ISSUE_TEMPLATE/feedback.yml` and issue #8

## Evidence Still Needed

- Usage signal: stars, forks, external feedback, external example, or integration.
- Clear maintainer history over time beyond initial setup.

Track these in `docs/adoption-evidence.json` and review them with:

```bash
asset-pipeline-steward application .
asset-pipeline-steward evidence .
```
