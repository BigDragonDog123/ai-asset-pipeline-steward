# GitHub Connector Setup

Use this after the repository has been created on GitHub. The local repository can pass all local checks before this step, but Codex for OSS still needs public URLs, CI evidence, release evidence, and visible maintainer activity.

## Current Diagnosis

As of 2026-06-02:

- GitHub user detected by Codex connector: `BigDragonDog123`.
- Installed GitHub App accounts visible to the connector: none.
- Repositories visible to the connector: none.
- Target repository status: `BigDragonDog123/ai-asset-pipeline-steward` returns 404.

This means the next missing piece is not another local code edit. The missing piece is public GitHub setup and ChatGPT/Codex GitHub authorization.

## Create The Repository

1. Open https://github.com/new.
2. Repository name: `ai-asset-pipeline-steward`.
3. Visibility: Public.
4. Do not add README, license, or `.gitignore`; they already exist locally.
5. Create the repository.

Then return to this local folder and run:

```powershell
.\scripts\publish-after-github-repo.ps1 -Push
```

If you prefer token-based setup, set `GITHUB_TOKEN` to a token that can create repositories and run:

```powershell
.\scripts\publish-after-github-repo.ps1 -CreateRepo -Push
```

## Connect GitHub To ChatGPT/Codex

OpenAI's GitHub connection flow is:

1. Open ChatGPT settings.
2. Go to Apps.
3. Find GitHub.
4. Install and authorize the ChatGPT GitHub app.
5. Choose repository access and include `BigDragonDog123/ai-asset-pipeline-steward`.

If the repository does not appear immediately, wait about 5 minutes. If it still does not appear, reopen the GitHub app settings and choose/configure repositories again.

## Verify Connector Access

After setup, Codex should be able to list the repository. If it cannot:

- Confirm the repository is public.
- Confirm the ChatGPT GitHub app is installed on the `BigDragonDog123` account.
- Confirm repository access includes `ai-asset-pipeline-steward`.
- Trigger GitHub search indexing by searching GitHub for:

```text
repo:BigDragonDog123/ai-asset-pipeline-steward import
```

Wait 5 to 10 minutes after indexing or authorization changes.

## After Connector Access Works

Record public proof in `docs/adoption-evidence.json`:

- public repository URL;
- CI run URL;
- release URL;
- starter issue URLs;
- any external feedback or usage examples.

Then run:

```powershell
asset-pipeline-steward collect-evidence .
asset-pipeline-steward evidence .
asset-pipeline-steward readiness .
```

The goal is for local readiness to keep passing and for adoption evidence warnings to shrink as public activity appears.
