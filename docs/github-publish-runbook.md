# GitHub Publish Runbook

This runbook turns the local repository into a public GitHub repository.

## Current Local State

- Branch: `main`
- Initial commit: `2fcd67f`
- Suggested repository name: `ai-asset-pipeline-steward`
- Suggested visibility: public
- Suggested owner: `BigDragonDog123`

## Option A: GitHub Website

1. Open https://github.com/new
2. Repository name: `ai-asset-pipeline-steward`
3. Visibility: Public
4. Do not add README, license, or `.gitignore` in the GitHub form. They already exist locally.
5. Create repository.
6. In this local folder, run:

```bash
git remote add origin https://github.com/BigDragonDog123/ai-asset-pipeline-steward.git
git push -u origin main
```

If `origin` already exists, use:

```bash
git remote set-url origin https://github.com/BigDragonDog123/ai-asset-pipeline-steward.git
git push -u origin main
```

## Option B: GitHub CLI

If GitHub CLI is installed and authenticated:

```bash
gh repo create BigDragonDog123/ai-asset-pipeline-steward --public --source=. --remote=origin --push
```

## After Push

1. Open the repository on GitHub.
2. Check the Community Standards page.
3. Confirm CI runs on `main`.
4. Create these starter issues:
   - Add public-safe model inventory manifest example.
   - Add smoke-gate validation rules.
   - Add review-signal report command.
   - Add first release notes.
   - Draft Codex for OSS application after public activity.
5. Create release `v0.1.0`.
6. Fill `docs/adoption-evidence.json` with the public repo URL, CI run URL, release URL, and starter issue URLs.
7. Commit and push the updated adoption evidence file.

## Do Not Publish Yet If

- The repo contains private paths, secrets, model files, generated private outputs, caches, logs, or copyrighted samples.
- Tests fail.
- The GitHub account is not the intended public maintainer identity.
