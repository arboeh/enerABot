# scripts/test-local.ps1

param(
    [switch]$Lint,
    [switch]$Format,
    [switch]$TypeCheck,
    [switch]$Tests,
    [switch]$All,
    [switch]$SkipTests,
    [switch]$Force
)

$runLint = $Lint -or $All
$runFormat = $Format -or $All
$runTypeCheck = $TypeCheck -or $All
$runTests = ($Tests -or $All -or (-not $Lint -and -not $Format -and -not $TypeCheck)) -and -not $SkipTests

$venv = ".venv"
$cacheDir = "$venv/check-cache"
$sourcePaths = @("custom_components\enerabot", "tests")

if (!(Test-Path $cacheDir)) {
    New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null
}

function Get-SourceHash {
    param([string[]]$Paths)
    $files = Get-ChildItem -Path $Paths -Recurse -File -Include *.py, *.json, *.yaml, *.yml |
        Where-Object { $_.FullName -notmatch '__pycache__|\.pytest_cache|\.ruff_cache|\.mypy_cache' } |
        Sort-Object FullName
    $combined = ($files | ForEach-Object { (Get-FileHash $_.FullName).Hash }) -join ""
    if (-not $combined) { return "empty" }
    $stream = [System.IO.MemoryStream]::new([System.Text.Encoding]::UTF8.GetBytes($combined))
    return (Get-FileHash -InputStream $stream -Algorithm SHA256).Hash
}

function Get-ToolVersionHash {
    $freeze = uv run pip freeze 2>$null | Where-Object {
        $_ -match '^(ruff|pyright|pytest-asyncio)==(\S+)'
    }
    $combined = ($freeze -join "`n")
    if (-not $combined) { return "empty" }
    $stream = [System.IO.MemoryStream]::new([System.Text.Encoding]::UTF8.GetBytes($combined))
    return (Get-FileHash -InputStream $stream -Algorithm SHA256).Hash
}

function Test-CheckCache {
    param([string]$Name, [string]$CurrentHash, [bool]$ExplicitRequest = $false)
    if ($Force) { return $false }
    if ($ExplicitRequest -and -not $All) { return $false }
    $cacheFile = "$cacheDir/$Name.hash"
    if (!(Test-Path $cacheFile)) { return $false }
    return (Get-Content $cacheFile) -eq $CurrentHash
}

function Set-CheckCache {
    param([string]$Name, [string]$Hash)
    Set-Content "$cacheDir/$Name.hash" $Hash
}

# --- UV Sync (pyproject.toml driven) ---
$pyproject_hash = (Get-FileHash pyproject.toml).Hash

if (!(Test-Path "$venv/pyproject.hash") -or
    (Get-Content "$venv/pyproject.hash") -ne $pyproject_hash) {

    Write-Host "pyproject.toml changed -> fresh UV sync" -ForegroundColor Yellow

    if (Test-Path $venv) {
        Remove-Item -Recurse -Force $venv -ErrorAction SilentlyContinue
    }
    Remove-Item uv.lock -ErrorAction SilentlyContinue

    uv sync --dev --extra dev

    if ($LASTEXITCODE -ne 0) {
        Write-Error "UV sync failed!"
        exit 1
    }

    if (!(Test-Path $cacheDir)) {
        New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null
    }
    Set-Content "$venv/pyproject.hash" $pyproject_hash
    Write-Host "Fresh UV sync complete (.venv + uv.lock)" -ForegroundColor Green
}
else {
    Write-Host "Using cached .venv (pyproject.toml unchanged)" -ForegroundColor Green
}

$exitCode = 0
$sourceHash = Get-SourceHash -Paths $sourcePaths
$toolVersionHash = Get-ToolVersionHash

# Combine source hash and tool version hash so dependency upgrades invalidate cache
$sourceHash = "$sourceHash$toolVersionHash"

Write-Host "DEBUG sourceHash=$sourceHash" -ForegroundColor DarkGray

# --- Ruff Check ---
if ($runLint) {
    if (Test-CheckCache -Name "lint" -CurrentHash $sourceHash -ExplicitRequest $Lint) {
        Write-Host "`n--- Ruff Check: skipped (no source changes) ---" -ForegroundColor DarkGray
    }
    else {
        Write-Host "`n--- Ruff Check ---" -ForegroundColor Cyan
        uv run ruff check custom_components\enerabot tests
        if ($LASTEXITCODE -ne 0) {
            $exitCode = 1
        }
        else {
            Set-CheckCache -Name "lint" -Hash $sourceHash
        }
    }
}

# --- Ruff Format Check ---
if ($runFormat) {
    if (Test-CheckCache -Name "format" -CurrentHash $sourceHash -ExplicitRequest $Format) {
        Write-Host "`n--- Ruff Format Check: skipped (no source changes) ---" -ForegroundColor DarkGray
    }
    else {
        Write-Host "`n--- Ruff Format Check ---" -ForegroundColor Cyan
        uv run ruff format --check custom_components\enerabot tests
        if ($LASTEXITCODE -ne 0) {
            $exitCode = 1
        }
        else {
            Set-CheckCache -Name "format" -Hash $sourceHash
        }
    }
}

# --- Pyright ---
if ($runTypeCheck) {
    if (Test-CheckCache -Name "typecheck" -CurrentHash $sourceHash -ExplicitRequest $TypeCheck) {
        Write-Host "`n--- Pyright: skipped (no source changes) ---" -ForegroundColor DarkGray
    }
    else {
        Write-Host "`n--- Pyright ---" -ForegroundColor Cyan
        uv run pyright custom_components\enerabot
        if ($LASTEXITCODE -ne 0) {
            $exitCode = 1
        }
        else {
            Set-CheckCache -Name "typecheck" -Hash $sourceHash
        }
    }
}

# --- Pytest ---
if ($runTests) {
    if (Test-CheckCache -Name "tests" -CurrentHash $sourceHash -ExplicitRequest $Tests) {
        Write-Host "`n--- Pytest: skipped (no source changes) ---" -ForegroundColor DarkGray
    }
    else {
        Write-Host "`n--- Pytest ---" -ForegroundColor Cyan
        uv run pytest tests/ -v --cov=custom_components.enerabot --cov-report=term-missing
        if ($LASTEXITCODE -ne 0) {
            $exitCode = 1
        }
        else {
            Set-CheckCache -Name "tests" -Hash $sourceHash
        }
    }
}

if ($exitCode -ne 0) {
    Write-Error "One or more checks failed!"
    exit $exitCode
}

Write-Host "`nAll requested checks passed (or already up to date)." -ForegroundColor Green