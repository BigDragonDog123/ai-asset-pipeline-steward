# Codex For OSS Submission Runbook

Status date: 2026-06-02.

Use this when the final external feedback signal and personal fields are ready. The official form is:

```text
https://openai.com/form/codex-for-oss/
```

For the current one-page evidence summary, use `docs/codex-for-oss-review-packet.md`.

Timing note verified on 2026-06-02: the official pages describe rolling review, not a fixed public deadline. Keep the repository in growth mode until at least one real external feedback or adoption signal is recorded.

Official form requirements verified on 2026-06-02:

- first name;
- last name;
- email associated with the ChatGPT account;
- public GitHub username;
- public GitHub repository URL;
- primary or core maintainer role;
- qualification answer, maximum 500 characters;
- interest in Codex Security and/or API credits;
- OpenAI Organization ID;
- API credits usage answer, maximum 500 characters;
- optional extra context, maximum 500 characters.

## Before Opening The Form

Run:

```bash
asset-pipeline-steward evidence .
asset-pipeline-steward readiness .
asset-pipeline-steward application .
asset-pipeline-steward submission-ready .
```

Submit only when:

- `external_feedback_urls` has at least one public URL;
- the feedback URL was recorded with `asset-pipeline-steward record-feedback` or reviewed against the same public-safety rules;
- current public GitHub metrics were refreshed by `record-feedback` or manually reviewed if GitHub API warnings appeared;
- first name, last name, ChatGPT email, and OpenAI Organization ID are known;
- the latest GitHub Actions run on `main` is green;
- `docs/adoption-evidence.json` contains the current public evidence.

After the external feedback URL is recorded and the personal fields are ready for manual entry, run:

```bash
asset-pipeline-steward submission-ready . --manual-ready
```

The command should report ready before opening the final form submission flow.

## Manual Values

Fill these yourself:

- First name: `<manual>`
- Last name: `<manual>`
- Email: `<ChatGPT account email>`
- OpenAI Organization ID: find it at `https://platform.openai.com/settings/organization/general`

Do not commit these personal values to the repository.

## Form Values

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

## Qualification Answer

Maximum 500 characters:

```text
AI Asset Pipeline Steward turns repeated local AI-asset maintenance into a public-safe OSS workflow: manifests, repo scans, synthetic fixtures, CI, release evidence, feedback intake, and final submission gates. It shows active maintainer work through issue triage, PR maintenance, an end-to-end review/handoff scenario, and tools for recording external adoption without leaking private data.
```

## API Credits Answer

Maximum 500 characters:

```text
Use credits to build Codex maintainer automation around real OSS workflows: review manifest/schema PRs, triage feedback issues, test release and submission gates, collect adoption evidence, expand synthetic fixtures, and run public-safety checks. Credits would let the project validate agent-assisted maintenance loops instead of only static documentation.
```

## Extra Context Answer

Maximum 500 characters:

```text
The repo is intentionally public-safe: no private paths, credentials, model weights, logs, caches, or non-public media. Current evidence includes green CI, v0.1.0, completed starter issues, merged maintenance PRs, an end-to-end maintainer-loop example, structured feedback intake, and strict gates that still block submission until external feedback is recorded.
```

If a real external feedback URL has been recorded, replace the final clause with:

```text
Current evidence includes green CI, v0.1.0, completed starter issues, merged maintenance PRs, the maintainer-loop example, structured feedback intake, and public external feedback recorded in docs/adoption-evidence.json.
```

## Supporting Evidence Links

- Repository: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward`
- Release: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/releases/tag/v0.1.0`
- Review packet: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/docs/codex-for-oss-review-packet.md`
- Feedback task: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/8`
- Terminal examples: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/docs/terminal-examples.md`
- Public feedback request: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/docs/public-feedback-request.md`
- Reviewer brief: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/docs/reviewer-brief.md`

## After Submission

Record the submission date privately. Do not commit personal form data, email, Organization ID, or application confirmation emails to this repository.
