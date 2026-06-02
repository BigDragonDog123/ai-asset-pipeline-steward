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
- Recorded CI evidence: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/actions/runs/26815129133`
- Open PRs: none, verified on 2026-06-02
- Open adoption task: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/8`
- Completed starter issues: #3 through #7
- Merged maintenance PRs: #1 and #2
- Usage examples: `docs/terminal-examples.md` and `examples/`
- Reviewer brief: `docs/reviewer-brief.md`
- Feedback request: `docs/public-feedback-request.md`

## Current Weaknesses

- No external feedback URL is recorded yet.
- Current public GitHub stars: 0.
- Current public forks: 0.
- The strongest application path is to collect at least one public comment, issue, forum post, social post, or downstream usage link from someone other than the maintainer before submitting.

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
AI Asset Pipeline Steward turns repeated local AI-asset maintenance into a public-safe OSS workflow: manifest validation, repo scanning, synthetic fixtures, CI, release, and starter issues. It helps maintainers verify model/workflow readiness, separate human and VLM review signals, preserve handoffs, and extract private workflows into reusable public examples.
```

How will you use API credits for your project? Maximum 500 characters:

```text
Use credits to build and test Codex maintainer automation: PR review for manifest/schema changes, issue triage, release checklist checks, evidence collection, synthetic fixture expansion, and security/public-safety scans. Credits would help verify real maintenance workflows instead of only static docs.
```

Anything else we should know? Maximum 500 characters:

```text
The repo is intentionally public-safe: no private paths, credentials, model weights, logs, caches, or non-public media. Current evidence includes passing CI, v0.1.0, starter issues, and usage examples; the next milestone is outside feedback and adoption.
```

## Submission Gate

Submit only when:

- latest GitHub Actions on `main` is green;
- `asset-pipeline-steward repo-scan .` passes;
- `asset-pipeline-steward readiness .` has no unexpected blocker;
- a real external feedback URL is recorded, or the weaker application is intentional;
- personal fields are filled in the official form only, not committed to this repository.
