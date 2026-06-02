# Codex For OSS Application Draft

Status date: 2026-06-02.

This draft should not be submitted until the repository is public and has maintenance or usage evidence.

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
AI Asset Pipeline Steward helps maintainers turn ad-hoc AI-generated asset workflows into verified, public-safe pipelines with manifests, smoke gates, human/VLM review separation, and Codex repo skills. It targets repeatable maintenance work: review queues, batch gates, handoffs, and open-source extraction.
```

Interest:

- Codex Security: maybe, after the repo has public usage.
- API credits: yes, for maintainer workflow automation.

OpenAI Organization ID:

- Fill manually from https://platform.openai.com/settings/organization/general

How will you use API credits for your project? Maximum 500 characters.

```text
Use credits to test Codex-assisted maintainer workflows: PR review, manifest validation improvements, release checklist automation, synthetic fixture generation, and issue triage for AI asset pipeline maintainers.
```

Anything else we should know? Maximum 500 characters.

```text
The project is being built from repeated local maintenance workflows, but the public repo uses only synthetic fixtures and public-safe examples. The goal is to make AI asset pipeline maintenance more reproducible, reviewable, and safe for open-source contributors.
```

## Evidence Still Needed

- Public repo URL actually exists.
- CI passing on GitHub.
- First release.
- Issue/PR activity.
- Usage signal: stars, forks, feedback, external example, or integration.
- Clear maintainer history over time.

Track these in `docs/adoption-evidence.json` and review them with:

```bash
asset-pipeline-steward evidence .
```
