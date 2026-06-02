# GitHub Publish Runbook

This runbook turns the local repository into a public GitHub repository.

## Current Local State

- Branch: `main`
- Initial commit: `2fcd67f`
- Suggested repository name: `ai-asset-pipeline-steward`
- Suggested visibility: public
- Suggested owner: `BigDragonDog123`
- Current external blocker: GitHub connector can identify `BigDragonDog123`, but no GitHub App installations or repositories are visible yet.

## Option A: GitHub Website

1. Open https://github.com/new.
2. Repository name: `ai-asset-pipeline-steward`
3. Visibility: Public
4. Do not add README, license, or `.gitignore` in the GitHub form. They already exist locally.
5. Create repository.
6. In this local folder, run:

```powershell
.\scripts\publish-after-github-repo.ps1 -Push
```

If you only want the script to open the prefilled GitHub creation page:

```powershell
.\scripts\publish-after-github-repo.ps1 -OpenGitHubCreatePage
```

## Option B: GitHub CLI

If GitHub CLI is installed and authenticated:

```bash
gh repo create BigDragonDog123/ai-asset-pipeline-steward --public --source=. --remote=origin --push
```

`gh` is not currently installed on this machine, so Option A is the current path.

## ChatGPT/Codex GitHub Authorization

After the repository exists, follow `docs/github-connector-setup.md`.

The important rule: the ChatGPT/Codex GitHub app must be installed and configured to access `BigDragonDog123/ai-asset-pipeline-steward`. Otherwise Codex cannot inspect the public repo through the connector even if the GitHub page exists.

## After Push

1. Open the repository on GitHub.
2. Check the Community Standards page.
3. Confirm CI runs on `main`.
4. Create these starter issues:
   ```bash
   asset-pipeline-steward starter-issues .
   ```
5. Preview starter issue and release creation:
   ```powershell
   .\scripts\create-post-publish-github-items.ps1
   ```
6. If the preview is correct, set `GITHUB_TOKEN` to a token with Issues and Contents write access, then run:
   ```powershell
   .\scripts\create-post-publish-github-items.ps1 -Execute
   ```
7. Run `asset-pipeline-steward collect-evidence .` and use the output as a reviewed starting point.
8. Fill `docs/adoption-evidence.json` with the public repo URL, CI run URL, release URL, and starter issue URLs.
9. Run `asset-pipeline-steward application .` and confirm the submission gate warnings are understood.
10. Commit and push the updated adoption evidence file.

## Do Not Publish Yet If

- The repo contains private paths, secrets, model files, generated private outputs, caches, logs, or copyrighted samples.
- Tests fail.
- The GitHub account is not the intended public maintainer identity.
