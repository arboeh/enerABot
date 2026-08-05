<#
.SYNOPSIS
    Syncs the integration version from pyproject.toml to manifest.json.

.DESCRIPTION
    Reads the [project].version value from pyproject.toml and writes it
    to custom_components/enerabot/manifest.json.

.PARAMETER Version
    If provided, uses this version string instead of reading from
    pyproject.toml.

.PARAMETER WhatIf
    If set, shows what would change without modifying files.

.EXAMPLE
    PS> .\scripts\sync-manifest.ps1
    .SYNOPSIS

    Syncs version from pyproject.toml to manifest.json.

.EXAMPLE
    PS> .\scripts\sync-manifest.ps1 -Version "0.3.2"
    Forces manifest.json version to 0.3.2 and updates pyproject.toml.
#>
param(
    [string] $Version,
    [switch] $WhatIf
)

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$ProjectToml = Join-Path $RepoRoot 'pyproject.toml'
$ManifestJson = Join-Path $RepoRoot 'custom_components/enerabot/manifest.json'

if (-not (Test-Path $ProjectToml)) {
    Write-Error "pyproject.toml not found at $ProjectToml"
    exit 1
}

if (-not (Test-Path $ManifestJson)) {
    Write-Error "manifest.json not found at $ManifestJson"
    exit 1
}

function Get-TomlVersion {
    param([string]$Path)
    $content = Get-Content $Path -Raw
    if ($content -match '^\[project\]\s*\nversion\s*=\s*"([^"]+)"'m) {
        return $matches[1]
    }
    throw "Could not find [project].version in $Path"
}

function Set-TomlVersion {
    param([string]$Path, [string]$NewVersion)
    $content = Get-Content $Path -Raw
    $content -creplace '(^\[project\]\s*\nversion\s*=\s*")([^"]+)(")', "`$1$NewVersion`$3" |
        Set-Content $Path -Encoding utf8
}

function Get-ManifestVersion {
    param([string]$Path)
    $json = Get-Content $Path -Raw | ConvertFrom-Json
    return $json.version
}

function Set-ManifestVersion {
    param([string]$Path, [string]$NewVersion)
    $json = Get-Content $Path -Raw | ConvertFrom-Json
    $json.version = $NewVersion
    $json | ConvertTo-Json -Depth 10 | Set-Content $Path -Encoding utf8 -NoNewline
    Add-Content $Path "`n"
}

$sourceVersion = if ($Version) { $Version } else { Get-TomlVersion $ProjectToml }
$manifestVersion = Get-ManifestVersion $ManifestJson

Write-Host "pyproject.toml version:   $sourceVersion"
Write-Host "manifest.json version:    $manifestVersion"

if ($sourceVersion -eq $manifestVersion) {
    Write-Host "Versions are already in sync." -ForegroundColor Green
    return
}

if ($WhatIf) {
    Write-Host "[WhatIf] Would update manifest.json to $sourceVersion" -ForegroundColor Yellow
    return
}

Set-ManifestVersion $ManifestJson $sourceVersion

if ($Version) {
    Set-TomlVersion $ProjectToml $Version
    Write-Host "pyproject.toml updated to $Version" -ForegroundColor Green
}

Write-Host "manifest.json updated to $sourceVersion" -ForegroundColor Green
