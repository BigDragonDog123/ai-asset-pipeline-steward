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
- Applications are reviewed on a rolling basis; selection is not guaranteed.

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
| Public-safe project scope | In progress | The repo frames the work as AI asset pipeline stewardship rather than private local content. |
| Reusable Codex skill | In progress | `.agents/skills/ai-asset-pipeline-steward/SKILL.md` exists for repo-scoped use. |
| Runnable code | In progress | `asset-pipeline-steward` validates public-safe manifests. |
| Tests | In progress | `tests/test_cli.py` covers manifest validation, schema output, repo-scan, readiness checks, and unsafe path/model cases. |
| Community health files | In progress | README, license, contribution, security, conduct, issue/PR templates, CI added locally. |
| Local readiness checks | In progress | `asset-pipeline-steward readiness .` checks community files, schema, examples, repo-scan, git branch/status, and origin remote. |
| Adoption evidence tracking | In progress | `docs/adoption-evidence.json`, `asset-pipeline-steward evidence .`, and `asset-pipeline-steward collect-evidence .` track public repo URL, CI, release, issues, feedback, usage, stars, and forks. |
| Application packet | In progress | `docs/codex-for-oss-application.json` and `asset-pipeline-steward application .` render draft form fields and check answer length limits. |
| Public repository | Missing | The workspace has not yet been pushed to GitHub. |
| GitHub connector authorization | Missing | Codex detects user `BigDragonDog123`, but no GitHub App installations or repositories are visible to the connector. |
| Public adoption | Missing | No stars, downloads, releases, external users, or issue/PR history yet. |
| Maintainer activity evidence | Missing | Needs commits, releases, issues, changelog, roadmap, and real maintenance history. |

## Application Strength

Verified:

- The official program accepts applications from active maintainers of public open-source projects.
- The application asks for public GitHub identity, public repo URL, maintainer role, and qualification evidence.

Inferred:

- A clean repository with tests, community files, agent skills, and a maintainer workflow is necessary but not sufficient.
- The best near-term strategy is to build credible maintenance history before applying.

Unknown:

- The exact selection threshold.
- Whether this repository will be considered ecosystem-important without external adoption.
- Whether skill-focused repos alone are favored unless tied to a widely used project.

## Next Milestones

1. Create the public GitHub repository and push `main`.
2. Add a short roadmap and first release.
3. Turn at least one local repeated workflow into a public-safe example manifest or tutorial.
4. Add screenshots or terminal examples that show the validator and skill in action.
5. Install/configure the ChatGPT/Codex GitHub app so Codex can see the repository.
6. Run `asset-pipeline-steward readiness .` after the repo is pushed.
7. Run `asset-pipeline-steward collect-evidence .` and fill `docs/adoption-evidence.json` with public URLs as CI, releases, issues, and usage appear.
8. Use issues to track roadmap items and maintenance tasks.
9. Gather adoption evidence: stars, forks, external feedback, usage examples, or integration into a real public workflow.
10. Render `asset-pipeline-steward application .` and submit only after the public repo has credible activity.

## Draft Application Notes

Repository role:

- Primary maintainer.

Why the repository qualifies, draft under 500 characters:

- "AI Asset Pipeline Steward helps maintainers turn ad-hoc AI-generated asset workflows into verified, public-safe pipelines with manifests, smoke gates, human/VLM review separation, and Codex repo skills. The project targets repeatable maintenance work: review queues, batch gates, handoffs, and open-source extraction."

API credit usage, draft under 500 characters:

- "Use credits to test Codex-assisted maintainer workflows: PR review, manifest validation improvements, release checklist automation, synthetic fixture generation, and issue triage for AI asset pipeline maintainers."
