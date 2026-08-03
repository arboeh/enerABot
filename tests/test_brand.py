# tests/test_brand.py

"""Test that brand assets exist."""

import os
from pathlib import Path

import pytest

BRAND_DIR = Path(__file__).parent.parent / "custom_components" / "enerabot" / "brand"


def test_brand_icon_exists() -> None:
    """Test that the brand icon exists."""
    assert (BRAND_DIR / "icon.png").exists()
