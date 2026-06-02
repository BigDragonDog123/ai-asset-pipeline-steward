param(
    [switch]$OpenGitHubCreatePage,
    [switch]$CreateRepo,
    [switch]$Push,
    [string]$GitHubAccessValue = $env:GITHUB_TOKEN
)

$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/BigDragonDog123/ai-asset-pipeline-steward.git"
$CreateUrl = "https://github.com/new?name=ai-asset-pipeline-steward&description=Public-safe%20AI%20asset%20pipeline%20stewardship%20starter%20kit&visibility=public"
$ApiRoot = "https://api.github.com"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message"
}

function Invoke-GitHubJson {
    param(
        [string]$Method,
        [string]$Endpoint,
        [hashtable]$Payload
    )

    if (-not $GitHubAccessValue) {
        throw "Set GITHUB_TOKEN to a GitHub token that can create repositories."
    }

    $Headers = @{
        Accept = "application/vnd.github+json"
        Authorization = "Bearer $GitHubAccessValue"
        "X-GitHub-Api-Version" = "2022-11-28"
    }

    $Json = $null
    if ($Payload) {
        $Json = $Payload | ConvertTo-Json -Depth 10
    }

    Invoke-RestMethod -Method $Method -Uri "$ApiRoot/$Endpoint" -Headers $Headers -Body $Json -ContentType "application/json"
}

Write-Step "Checking local repository"
git rev-parse --is-inside-work-tree | Out-Null

$Branch = (git branch --show-current).Trim()
if ($Branch -ne "main") {
    throw "Current branch is '$Branch'. Switch to main before publishing."
}

$Status = git status --porcelain
if ($Status) {
    throw "The worktree has uncommitted changes. Commit or stash them before publishing."
}

Write-Step "Ensuring origin remote"
$CurrentOrigin = ""
try {
    $CurrentOrigin = (git remote get-url origin).Trim()
} catch {
    $CurrentOrigin = ""
}

if (-not $CurrentOrigin) {
    git remote add origin $RepoUrl
    Write-Host "Added origin: $RepoUrl"
} elseif ($CurrentOrigin -ne $RepoUrl) {
    git remote set-url origin $RepoUrl
    Write-Host "Updated origin: $RepoUrl"
} else {
    Write-Host "Origin is already set: $RepoUrl"
}

if ($OpenGitHubCreatePage) {
    Write-Step "Opening GitHub repository creation page"
    Start-Process $CreateUrl
}

if ($CreateRepo) {
    Write-Step "Creating public GitHub repository"
    $Payload = @{
        name = "ai-asset-pipeline-steward"
        description = "Public-safe AI asset pipeline stewardship starter kit"
        private = $false
        has_issues = $true
        has_projects = $false
        has_wiki = $false
        auto_init = $false
    }

    try {
        $Created = Invoke-GitHubJson -Method "Post" -Endpoint "user/repos" -Payload $Payload
        Write-Host "Created repository: $($Created.html_url)"
    } catch {
        if ($_.Exception.Response.StatusCode.value__ -eq 422) {
            Write-Host "Repository may already exist: $RepoUrl"
        } else {
            throw
        }
    }
}

if (-not $Push) {
    Write-Step "Ready"
    Write-Host "Create the public repository on GitHub, or run with -CreateRepo after setting GITHUB_TOKEN."
    Write-Host "Then push with:"
    Write-Host ".\scripts\publish-after-github-repo.ps1 -Push"
    exit 0
}

Write-Step "Pushing main to GitHub"
$env:GIT_TERMINAL_PROMPT = "0"
git push -u origin main

Write-Step "Next checks"
Write-Host "Open: https://github.com/BigDragonDog123/ai-asset-pipeline-steward"
Write-Host "Then confirm GitHub Actions CI, create v0.1.0, create starter issues, and update docs/adoption-evidence.json."
