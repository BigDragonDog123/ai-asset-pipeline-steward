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
AI Asset Pipeline Steward turns repeated local AI-asset maintenance into a public-safe OSS workflow: manifest validation, repo scanning, synthetic fixtures, CI, release, and starter issues. It helps maintainers verify model/workflow readiness, separate human and VLM review signals, preserve handoffs, and extract private workflows into reusable public examples.
```

Interest:

- Codex Security: maybe, after the repo has public usage.
- API credits: yes, for maintainer workflow automation.

OpenAI Organization ID:

- Fill manually from https://platform.openai.com/settings/organization/general

How will you use API credits for your project? Maximum 500 characters.

```text
Use credits to build and test Codex maintainer automation: PR review for manifest/schema changes, issue triage, release checklist checks, evidence collection, synthetic fixture expansion, and security/public-safety scans. Credits would help verify real maintenance workflows instead of only static docs.
```

Anything else we should know? Maximum 500 characters.

```text
The repo is intentionally public-safe: no private paths, credentials, model weights, logs, caches, or non-public media. Current evidence includes passing CI, v0.1.0, starter issues, and usage examples; the next milestone is outside feedback and adoption.
```

## Current Public Evidence

- Public repository: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward`
- Passing CI: tracked in `docs/adoption-evidence.json`
- First release: `v0.1.0`
- Starter issues: issues #3 through #7
- Usage examples: `docs/terminal-examples.md` and `examples/`

## Evidence Still Needed

- Usage signal: stars, forks, external feedback, external example, or integration.
- Clear maintainer history over time beyond initial setup.

Track these in `docs/adoption-evidence.json` and review them with:

```bash
asset-pipeline-steward application .
asset-pipeline-steward evidence .
```
