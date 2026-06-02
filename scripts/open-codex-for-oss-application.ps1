$ErrorActionPreference = "Stop"

$Urls = @(
    "https://openai.com/form/codex-for-oss/",
    "https://platform.openai.com/settings/organization/general",
    "https://github.com/BigDragonDog123/ai-asset-pipeline-steward",
    "https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/8",
    "https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml"
)

foreach ($Url in $Urls) {
    Start-Process $Url
}

Write-Host "Opened Codex for OSS form, OpenAI Organization ID settings, repository, feedback task, and feedback form."
