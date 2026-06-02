# Codex For OSS Readiness

Status date: 2026-06-02.

This document maps the project to the public Codex for Open Source application requirements and identifies what is still missing.

## Official Requirements Observed

Verified from OpenAI's Codex for Open Source pages:

- Active open-source maintainers can apply.
- The GitHub username must be public.
- The GitHub repository URL must be public.
- Applicants must describe whether they are a primary or core maintainer.
- Applicants must explain why the repository qualifies, using signals such as stars, downloads, ecosystem importance, usage, or active maintenance.
- Selected maintainers may receive six months of ChatGPT Pro with Codex, API credits, and conditional Codex Security access.
- Applications are reviewed on a rolling basis; no fixed public deadline was observed on 2026-06-02, and selection is not guaranteed.

Sources:

- https://developers.openai.com/community/codex-for-oss
- https://openai.com/form/codex-for-oss/

## GitHub Community Health Targets

Verified from GitHub's public repository community profile guidance:

- `README.md`
- `LICENSE`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`

This repo also includes issue templates, a PR template, CI, Dependabot for GitHub Actions, and `AGENTS.md`.

Source:

- https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories

## Current Evidence

| Area | Status | Evidence |
|---|---|---|
| Public-safe project scope | Pass | The repo frames the work as AI asset pipeline stewardship rather than private local content, and `asset-pipeline-steward repo-scan .` passes. |
| Reusable Codex skill | Pass | `.agents/skills/ai-asset-pipeline-steward/SKILL.md` exists for repo-scoped use. |
| Runnable code | Pass | `asset-pipeline-steward` validates public-safe manifests and renders maintainer reports. |
| Tests | Pass | `tests/test_cli.py` covers manifest validation, schema output, repo-scan, readiness checks, unsafe path/model cases, evidence collection, and application packet rendering. |
| Community health files | Pass | README, license, contribution, security, conduct, issue/PR templates, CI, Dependabot, roadmap, changelog, and `AGENTS.md` are public. |
| Local readiness checks | Pass | `asset-pipeline-steward readiness .` passes without blockers on `main`. |
| Adoption evidence tracking | Pass | `docs/adoption-evidence.json`, `asset-pipeline-steward evidence .`, and `asset-pipeline-steward collect-evidence .` track public repo URL, CI, release, issues, feedback, usage, stars, and forks. |
| Application packet | Pass | `docs/codex-for-oss-application.json` and `asset-pipeline-steward application .` render draft form fields and check answer length limits. |
| Final submission gate | Early | `asset-pipeline-steward submission-ready .` blocks final submission until external feedback is recorded and personal form fields are confirmed for manual entry. |
| Public repository | Pass | `https://github.com/BigDragonDog123/ai-asset-pipeline-steward` is public. |
| GitHub connector authorization | Pass | Codex can fetch the repository by explicit full name and reports admin, maintain, push, triage, and pull permissions. |
| Public adoption | Early | Public evidence includes a release, CI, starter issues, usage examples, and Dependabot PRs. Stars, forks, downloads, and external feedback are still at early-stage values. |
| Maintainer activity evidence | Early | The repo now has commits, public CI, release, issues, changelog, roadmap, and evidence tracking; it still needs public feedback or third-party usage. |

## Application Strength

Verified:

- The official program accepts applications from active maintainers of public open-source projects.
- The application asks for public GitHub identity, public repo URL, maintainer role, and qualification evidence.

Inferred:

- A clean repository with tests, community files, agent skills, and a maintainer workflow is necessary but not sufficient.
- The best near-term strategy is to add at least one real external feedback or adoption signal before applying.

Unknown:

- The exact selection threshold.
- Whether this repository will be considered ecosystem-important without external adoption.
- Whether skill-focused repos alone are favored unless tied to a widely used project.
- Whether the rolling program will change or close before the repository reaches stronger adoption evidence.

## Next Milestones

1. Gather external adoption evidence: stars, forks, feedback, a public comment, a downstream example, or integration into a real public workflow.
2. Use `asset-pipeline-steward feedback-candidates .` to check issue #8 for non-maintainer feedback.
3. Record any real external feedback with `asset-pipeline-steward record-feedback <public-url>`.
4. Re-run `asset-pipeline-steward evidence .`, `asset-pipeline-steward readiness .`, `asset-pipeline-steward application .`, and `asset-pipeline-steward submission-ready . --manual-ready` before submitting.
5. Fill manual form fields: first name, last name, ChatGPT account email, and OpenAI Organization ID.

## Draft Application Notes

Repository role:

- Primary maintainer.

Why the repository qualifies, draft under 500 characters:

- "AI Asset Pipeline Steward turns repeated local AI-asset maintenance into a public-safe OSS workflow: manifests, repo scans, synthetic fixtures, CI, release evidence, feedback intake, and final submission gates. It shows active maintainer work through issue triage, PR maintenance, an end-to-end review/handoff scenario, and tools for recording external adoption without leaking private data."

API credit usage, draft under 500 characters:

- "Use credits to build Codex maintainer automation around real OSS workflows: review manifest/schema PRs, triage feedback issues, test release and submission gates, collect adoption evidence, expand synthetic fixtures, and run public-safety checks. Credits would let the project validate agent-assisted maintenance loops instead of only static documentation."
