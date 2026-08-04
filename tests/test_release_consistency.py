"""Test that README version references match manifest.json."""

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = REPO_ROOT / "custom_components" / "enerabot" / "manifest.json"
README_FILES = ["README.md", "README.de.md"]


def _manifest_version() -> str:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return manifest["version"]


@pytest.mark.parametrize("readme", README_FILES)
def test_readme_version_matches_manifest(readme: str) -> None:
    """READMEs must reference the same version as manifest.json."""
    version = _manifest_version()
    content = (REPO_ROOT / readme).read_text(encoding="utf-8")
    assert version in content, f"{readme} does not mention current manifest version {version}"
