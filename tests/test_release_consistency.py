"""Test that version references are consistent across project files."""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = REPO_ROOT / "custom_components" / "enerabot" / "manifest.json"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"


def _manifest_version() -> str:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return manifest["version"]


def _pyproject_version() -> str:
    content = PYPROJECT_PATH.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    assert match, f"Could not find version in {PYPROJECT_PATH}"
    return match.group(1)


def test_manifest_version_matches_pyproject() -> None:
    """manifest.json version must match pyproject.toml version."""
    manifest_version = _manifest_version()
    pyproject_version = _pyproject_version()
    assert manifest_version == pyproject_version, (
        f"Version mismatch: manifest.json={manifest_version}, pyproject.toml={pyproject_version}"
    )
