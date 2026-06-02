# GitHub Publish Runbook

This runbook turns the local repository into a public GitHub repository.

## Current Local State

- Branch: `main`
- Repository: `https://github.com/BigDragonDog123/ai-asset-pipeline-steward`
- Visibility: public
- Publication status: published and pushed
- First release: `v0.1.0`
- Starter issues: public issues #3 through #7
- Current strategic blocker: external adoption evidence is still early.

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

## Option B: GitHub API Token

If `GITHUB_TOKEN` is set to a GitHub token that can create repositories:

```powershell
.\scripts\publish-after-github-repo.ps1 -CreateRepo -Push
```

The script creates a public repository for the authenticated GitHub user, enables issues, keeps wiki/projects off, and does not initialize files on GitHub.

## Option C: GitHub CLI

If GitHub CLI is installed and authenticated:

```bash
gh repo create BigDragonDog123/ai-asset-pipeline-steward --public --source=. --remote=origin --push
```

`gh` is not currently installed on this machine, so Option A or B is the current path.

## ChatGPT/Codex GitHub Authorization

After the repository exists, follow `docs/github-connector-setup.md`.

The important rule: the ChatGPT/Codex GitHub app should be installed and configured to access `BigDragonDog123/ai-asset-pipeline-steward`. Codex can currently fetch the repository by explicit full name, but the installation listing still does not show visible accounts.

## After Push

Completed once on 2026-06-02:

- public repository created;
- `main` pushed;
- CI confirmed green;
- starter issues created;
- `v0.1.0` release published;
- `docs/adoption-evidence.json` filled with public evidence.

Repeat this checklist only for a fresh repository or a new release:

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
