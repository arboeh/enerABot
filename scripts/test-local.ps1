# scripts/test-local.ps1

$venv = ".venv"  # ← .venv-test → .venv (UV-Standard)
$pyproject_hash = (Get-FileHash pyproject.toml).Hash

if (!(Test-Path "$venv/pyproject.hash") -or
    (Get-Content "$venv/pyproject.hash") -ne $pyproject_hash) {

    Write-Host "pyproject.toml changed → fresh UV sync" -ForegroundColor Yellow

    if (Test-Path $venv) {
        Remove-Item -Recurse -Force $venv -ErrorAction SilentlyContinue
    }
    Remove-Item uv.lock -ErrorAction SilentlyContinue

    uv sync --dev

    if ($LASTEXITCODE -ne 0) {
        Write-Error "UV sync failed!"
        exit 1
    }

    # Jetzt existiert .venv garantiert
    Set-Content "$venv/pyproject.hash" $pyproject_hash
    Write-Host "Fresh UV sync complete (.venv + uv.lock)" -ForegroundColor Green
}
else {
    Write-Host "Using cached .venv (pyproject.toml unchanged)" -ForegroundColor Green
}

uv run pytest tests/ -v --cov=custom_components.enerabot --cov-report=term-missing
