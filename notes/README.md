# Release Checklist

Interne Anleitung zum Erstellen von **Development-Releases** und **öffentlichen HACS-Releases** für enerABot.

## Repository-Setup

### Single Repo mit Branches

```
enerABot/
├── main        # 🌟 Production Releases (git tag v0.3.0)
├── dev         # 🔧 Development & Beta-Releases (git tag v0.3.0-dev)
└── Remote: origin → https://github.com/arboeh/enerABot
```

**Workflow:**

1. **Development** auf `dev` Branch
2. **Beta-Releases** → `dev` → `git tag v0.3.0-dev`
3. **Production** → Merge `dev → main` → `git tag v0.3.0`

---

## Voraussetzungen

- [ ] Virtual Environment: `uv sync --dev --extra dev`
- [ ] Tests: `python -m pytest tests -v --cov=custom_components/enerabot --cov-report=term-missing`
- [ ] Lint: `python -m ruff check custom_components/enerabot tests`
- [ ] Format: `python -m ruff format --check custom_components/enerabot tests`
- [ ] Type Check: `python -m pyright custom_components/enerabot`
- [ ] Pre-commit: `pre-commit run --all-files` ✅ **passed**
- [ ] VS Code: `even-better-toml` + `ruff`
- [ ] `scripts/sync-manifest.ps1` (Version aus `pyproject.toml` in `manifest.json` synchronisieren)
- [ ] Hassfest-Validierung lokal (muss vor jedem Push ausgeführt werden): `python -m script.hassfest`

### Remote Setup (einmalig)

```powershell
git remote -v  # Sollte origin → GitHub zeigen
```

---

## Release Workflow

### 1. Development abschließen (dev Branch)

```powershell
git checkout dev
uv sync --dev --extra dev
```

### 2. Pre-commit Hooks ausführen

```powershell
pre-commit run --all-files
```

**Prüft automatisch:**

- ✅ Ruff Linting & Formatting
- ✅ Trailing Whitespace
- ✅ End-of-File Fixer
- ✅ JSON/YAML Syntax
- ✅ Merge Conflicts

### 3. Version aktualisieren

#### Zwei Stellen (wird jetzt über sync-manifest.ps1 synchronisiert)

```json
// custom_components/enerabot/manifest.json
{
  "version": "0.3.0-dev"  // ← Development/Beta
  // oder
  "version": "0.3.0"      // ← Production
}
```

```toml
# pyproject.toml
[project]
version = "0.3.0-dev"  # ← muss synchron zu manifest.json gepflegt werden
```

Verwende `.\scripts\sync-manifest.ps1` (liest Version aus `pyproject.toml` und schreibt sie nach `manifest.json`), oder `.\scripts\sync-manifest.ps1 -Version "0.3.0"` um beide Dateien zu aktualisieren.

### 4. Lint, Format, Type Check und Tests ausführen

```powershell
python -m ruff check custom_components/enerabot tests
python -m ruff format --check custom_components/enerabot tests
python -m pyright custom_components/enerabot
python -m pytest tests -v --cov=custom_components/enerabot --cov-report=term-missing
```

**Erwartung:**
- Ruff Check --- ✅ no errors
- Ruff Format --- ✅ no changes needed
- Pyright --- ✅ 0 errors, 0 warnings
- Pytest --- ✅ alle Tests passed

### 5. Hassfest lokal prüfen (**verpflichtend vor jedem Release**)

```powershell
python -m script.hassfest
```

> Verhindert, dass verbotene Schlüssel in `strings.json` (z. B. `selector`, `required`, `example` in Service-Feldern) erst in der CI auffallen. Muss vor jedem Commit ausgeführt werden.

### 6. CHANGELOG.md aktualisieren

```markdown
## [v0.3.0-dev] - 2026-08-04

### Added

- Konfigurierbare Preisquelle: fester Preis oder dynamischer Preissensor
- Automatischer Kosten-Sensor mit Reset-Zyklus (nie/monatlich/jährlich)
- Service `enerabot.reset_meter` sowie Reset-Button-Entity pro Zähler

### Fixed

- Übersetzungs-Konsistenzprüfung zwischen de.json/en.json ergänzt
```

### 7. Commit im dev-Branch

```powershell
git add .
git commit -m "feat: v0.3.0-dev (dynamic price + cost tracking + reset)"
git push origin dev
```

---

## Development Release (Beta)

### 8. Dev-Tag erstellen

```powershell
git checkout dev
git tag v0.3.0-dev
git push origin v0.3.0-dev
```

### 9. GitHub Release (Draft)

```
GitHub → Releases → Draft new release
├── Tag: v0.3.0-dev
├── Branch: dev
├── Title: enerABot v0.3.0-dev
└── Notes: Copy aus CHANGELOG.md
```

**Status:** **Draft** (für Beta-Tester)

---

## Production Release

### 10. Merge dev → main

```powershell
git checkout main
git pull origin main
git merge dev --no-ff -m "Release v0.3.0: Dynamic Price & Cost Tracking"
```

### 11. Finale Checks

```powershell
pre-commit run --all-files
python -m ruff check custom_components/enerabot tests
python -m ruff format --check custom_components/enerabot tests
python -m pyright custom_components/enerabot
python -m pytest tests -v --cov=custom_components/enerabot --cov-report=term-missing
python -m script.hassfest
```

### 12. Production Tag

```powershell
git tag -a v0.3.0 -m "enerABot v0.3.0

### Added
- Dynamische und feste Preisquelle konfigurierbar
- Automatischer Kosten-Sensor mit Reset-Zyklus
- Reset-Service und Reset-Button pro Zähler
### Fixed
- Translation-Konsistenz de/en abgesichert durch Tests"
git push origin main --tags
```

### 13. GitHub Release (Public)

```
GitHub → Releases → v0.3.0 → Publish release
├── Copy Changelog
└── Assets: (optional) dist/*.zip
```

---

## Update-Testing (optional)

```powershell
# Vor Release in HA testen:
# 1. HACS → Custom Repository → enerABot (dev Branch)
# 2. v0.3.0-dev installieren
# 3. Config Flow: Preismodus "Fest" und "Dynamisch" jeweils durchspielen
# 4. Options Flow: Zählerkorrektur + Metadaten-Update prüfen
# 5. reset_meter Service über Entwicklerwerkzeuge auslösen, Sensor-Reset prüfen
# 6. Reset-Button-Entity in der UI drücken, identisches Verhalten prüfen
```

---

## Troubleshooting

### Tests schlagen fehl

```powershell
Remove-Item -Recurse -Force .venv
uv sync --dev --extra dev
python -m pytest tests -v --cov=custom_components/enerabot --cov-report=term-missing
```

### Ruff / Pyright melden Fehler

```powershell
python -m ruff check custom_components/enerabot tests --fix
python -m ruff format custom_components/enerabot tests
python -m pyright custom_components/enerabot
```

### Pre-commit Fehlermeldung

```powershell
pre-commit clean
pre-commit install
```

### manifest.json und pyproject.toml nicht synchron

```powershell
# Sync-Script verwenden:
.\scripts\sync-manifest.ps1
# Oder manuell vergleichen:
Get-Content custom_components/enerabot/manifest.json | Select-String version
Get-Content pyproject.toml | Select-String version
```

### Hassfest schlägt fehl

```powershell
python -m script.hassfest
# Häufigste Ursache: verbotene Schlüssel (selector/required/example)
# in custom_components/enerabot/strings.json unter "services"
```

### HACS zeigt alte Version

```
GitHub → Releases → Latest muss v0.3.0 sein
HACS → Reload → Update verfügbar
```

---

## Checkliste vor Release

**Kopiere in GitHub Issue:**

```markdown
## Release v0.3.0 Checklist

### Development (dev)
- [ ] `python -m ruff check custom_components/enerabot tests` ✅ passed
- [ ] `python -m ruff format --check custom_components/enerabot tests` ✅ passed
- [ ] `python -m pyright custom_components/enerabot` ✅ passed
- [ ] `python -m pytest tests -v --cov=custom_components/enerabot --cov-report=term-missing` ✅ passed
- [ ] `pre-commit run --all-files` ✅ passed
- [ ] `python -m script.hassfest` (**verpflichtend**) ✅ passed
- [ ] `manifest.json` version = "0.3.0"
- [ ] `pyproject.toml` version = "0.3.0" (manuell synchron!)
- [ ] `strings.json` / `translations/de.json` / `translations/en.json` Keys identisch
- [ ] CHANGELOG.md aktualisiert
- [ ] `git push origin dev`

### Beta Release

- [ ] `git tag v0.3.0-dev`
- [ ] GitHub Release (Draft)
- [ ] Config Flow (fest + dynamisch) in HA getestet
- [ ] `reset_meter` Service + Reset-Button getestet

### Production (main)

- [ ] `git merge dev → main`
- [ ] Finale Tests ✅
- [ ] `git tag v0.3.0`
- [ ] `git push origin main --tags`
- [ ] GitHub Release (Published)

### HACS

- [ ] HACS zeigt Update (Restart erforderlich)
```

---

## Quick Reference

```powershell
# Development
git checkout dev
# ... develop ...
pre-commit run --all-files
python -m ruff check custom_components/enerabot tests
python -m ruff format --check custom_components/enerabot tests
python -m pyright custom_components/enerabot
python -m script.hassfest
python -m pytest tests -v --cov=custom_components/enerabot --cov-report=term-missing
git commit -m "feat: XYZ"
git push origin dev

# Beta Release
git tag v0.3.0-dev
git push origin v0.3.0-dev

# Production
git checkout main
git merge dev
git tag v0.3.0
git push origin main --tags
```

**Dauer:** Dev-Release **~3 Min**, Production **~7 Min** 🎉
