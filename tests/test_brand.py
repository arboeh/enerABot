# tests/test_brand.py

"""Test that brand assets exist."""

import os
from pathlib import Path

import pytest

BRAND_DIR = Path(__file__).parent.parent / "custom_components" / "enerabot" / "brand"


def test_brand_icon_exists() -> None:
    """Test that the brand icon exists."""
    assert (BRAND_DIR / "icon.png").exists()


def test_brand_logo_exists() -> None:
    """Test that the brand logo exists."""
    assert (BRAND_DIR / "logo.png").exists()


def test_brand_icon_is_png() -> None:
    """Test that the brand icon is a valid PNG."""
    icon_path = BRAND_DIR / "icon.png"
    assert icon_path.exists()
    with open(icon_path, "rb") as f:
        header = f.read(8)
    assert header == b"\x89PNG\r\n\x1a\n"


def test_brand_logo_is_png() -> None:
    """Test that the brand logo is a valid PNG."""
    logo_path = BRAND_DIR / "logo.png"
    assert logo_path.exists()
    with open(logo_path, "rb") as f:
        header = f.read(8)
    assert header == b"\x89PNG\r\n\x1a\n"
