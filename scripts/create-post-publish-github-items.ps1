param(
    [switch]$Execute,
    [switch]$CreateIssues,
    [switch]$CreateRelease,
    [string]$Owner = "BigDragonDog123",
    [string]$Repo = "ai-asset-pipeline-steward",
    [string]$GitHubAccessValue = $env:GITHUB_TOKEN
)

$ErrorActionPreference = "Stop"

if (-not $CreateIssues -and -not $CreateRelease) {
    $CreateIssues = $true
    $CreateRelease = $true
}

$ApiRoot = "https://api.github.com/repos/$Owner/$Repo"
$RepoUrl = "https://github.com/$Owner/$Repo"
$StarterIssuesPath = Join-Path (Get-Location) "docs\starter-issues.json"

$LabelDefinitions = @{
    "documentation" = @{
        color = "0075ca"
        description = "Documentation, examples, or tutorials"
    }
    "enhancement" = @{
        color = "a2eeef"
        description = "New feature or request"
    }
    "release" = @{
        color = "5319e7"
        description = "Release preparation and publication"
    }
}

$ReleaseBody = @"
Initial public release of AI Asset Pipeline Steward.

Highlights:
- Public-safe manifest validator.
- Maintainer report command.
- Synthetic review, model-inventory, and review-queue manifests.
- Maintainability checks for workflow preflight, review-signal roles, decision gates, and handoffs.
- Repo-scoped Codex skill for AI asset pipeline stewardship.
- GitHub community health files, CI, and Codex for OSS readiness docs.

This release uses only synthetic examples and does not include model files, private paths, credentials, logs, caches, or non-public media.
"@

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message"
}

function Invoke-GitHubPost {
    param(
        [string]$Endpoint,
        [hashtable]$Payload
    )

    if (-not $GitHubAccessValue) {
        throw "Set GITHUB_TOKEN to a GitHub token with Issues and Contents write access."
    }

    $Headers = @{
        Accept = "application/vnd.github+json"
        Authorization = "Bearer $GitHubAccessValue"
        "X-GitHub-Api-Version" = "2022-11-28"
    }

    $Json = $Payload | ConvertTo-Json -Depth 10
    Invoke-RestMethod -Method Post -Uri "$ApiRoot/$Endpoint" -Headers $Headers -Body $Json -ContentType "application/json"
}

function Ensure-Labels {
    param([string[]]$Labels)

    foreach ($Label in ($Labels | Sort-Object -Unique)) {
        $Definition = $LabelDefinitions[$Label]
        if (-not $Definition) {
            $Definition = @{
                color = "d4c5f9"
                description = "Project label"
            }
        }

        $Payload = @{
            name = $Label
            color = $Definition.color
            description = $Definition.description
        }

        if (-not $Execute) {
            Write-Host "[dry-run] ensure label: $Label"
            continue
        }

        try {
            Invoke-GitHubPost -Endpoint "labels" -Payload $Payload | Out-Null
            Write-Host "Created label: $Label"
        } catch {
            if ($_.Exception.Response.StatusCode.value__ -eq 422) {
                Write-Host "Label already exists or cannot be created again: $Label"
            } else {
                throw
            }
        }
    }
}

Write-Step "Checking local starter issue source"
if (-not (Test-Path $StarterIssuesPath)) {
    throw "Missing starter issue source: $StarterIssuesPath"
}

$StarterIssues = Get-Content -Raw $StarterIssuesPath | ConvertFrom-Json
Write-Host "Repository: $RepoUrl"
Write-Host "Mode: $(if ($Execute) { 'execute' } else { 'dry-run' })"

if ($CreateIssues) {
    Write-Step "Preparing starter issues"
    $AllLabels = @()
    foreach ($Issue in $StarterIssues) {
        $AllLabels += @($Issue.labels)
    }
    Ensure-Labels -Labels $AllLabels

    foreach ($Issue in $StarterIssues) {
        $Payload = @{
            title = $Issue.title
            body = $Issue.body
            labels = @($Issue.labels)
        }

        if (-not $Execute) {
            Write-Host "[dry-run] create issue: $($Issue.title)"
            continue
        }

        $Created = Invoke-GitHubPost -Endpoint "issues" -Payload $Payload
        Write-Host "Created issue: $($Created.html_url)"
    }
}

if ($CreateRelease) {
    Write-Step "Preparing release v0.1.0"
    $Payload = @{
        tag_name = "v0.1.0"
        target_commitish = "main"
        name = "v0.1.0 - Public scaffold"
        body = $ReleaseBody
        draft = $false
        prerelease = $false
    }

    if (-not $Execute) {
        Write-Host "[dry-run] create release: v0.1.0"
    } else {
        $Created = Invoke-GitHubPost -Endpoint "releases" -Payload $Payload
        Write-Host "Created release: $($Created.html_url)"
    }
}

Write-Step "Next"
Write-Host "Run: asset-pipeline-steward collect-evidence ."
Write-Host "Then update docs/adoption-evidence.json and commit the evidence URLs."
