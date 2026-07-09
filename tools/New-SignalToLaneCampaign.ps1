# New-SignalToLaneCampaign.ps1
# Creates a Signal-to-Lane campaign folder structure.

param(
    [Parameter(Mandatory=$true)]
    [string]$Root,

    [Parameter(Mandatory=$true)]
    [string]$Platform,

    [Parameter(Mandatory=$true)]
    [string]$CampaignId,

    [Parameter(Mandatory=$true)]
    [string]$CampaignName
)

$CampaignRoot = Join-Path $Root "platforms\$Platform\campaigns\$CampaignId"

$Folders = @(
    "00_campaign_manifest",
    "01_search_insights",
    "02_content_angles",
    "03_scripts",
    "04_post_queue",
    "05_published_posts",
    "06_performance_notes",
    "07_cross_lane_promotions",
    "08_screenshots",
    "08_screenshots\creator_search_insights",
    "08_screenshots\published_posts",
    "08_screenshots\comments",
    "08_screenshots\analytics"
)

foreach ($Folder in $Folders) {
    New-Item -ItemType Directory -Force -Path (Join-Path $CampaignRoot $Folder) | Out-Null
}

$Files = @(
    "00_campaign_manifest\CAMPAIGN_DESCRIPTION.md",
    "00_campaign_manifest\CAMPAIGN_RULES.md",
    "00_campaign_manifest\ROUTING_LOGIC.md",
    "01_search_insights\SEARCH_TERMS_LOG.md",
    "01_search_insights\TREND_NOTES.md",
    "02_content_angles\HOOK_LIBRARY.md",
    "02_content_angles\PRESSURE_LINES.md",
    "03_scripts\15_SECOND_SCRIPTS.md",
    "03_scripts\30_SECOND_SCRIPTS.md",
    "03_scripts\60_SECOND_SCRIPTS.md",
    "04_post_queue\READY_TO_RECORD.md",
    "05_published_posts\PUBLISHED_LOG.md",
    "06_performance_notes\VIEW_LOG.md",
    "06_performance_notes\COMMENT_THEMES.md",
    "06_performance_notes\WINNING_PATTERNS.md",
    "07_cross_lane_promotions\ROUTING_LOG.md"
)

foreach ($File in $Files) {
    $Path = Join-Path $CampaignRoot $File

    if (-not (Test-Path $Path)) {
        New-Item -ItemType File -Force -Path $Path | Out-Null
    }
}

$Readme = @"
# $CampaignName

Campaign ID:

$CampaignId

Platform:

$Platform

## Signal-to-Lane Rule

The platform tests pressure.

The library preserves meaning.
"@

Set-Content -Path (Join-Path $CampaignRoot "README.md") -Value $Readme -Encoding UTF8

Write-Host "Signal-to-Lane campaign created:"
Write-Host $CampaignRoot
