"""Shared pytest fixtures for the Photorg test suite."""
from __future__ import annotations

import pytest
from pathlib import Path
from PIL import Image


@pytest.fixture
def sample_images(tmp_path: Path) -> Path:
    """Create a directory with minimal sample JPEG images."""
    src = tmp_path / "photos"
    src.mkdir()
    for name in ("beach1.jpg", "beach2.jpg", "museum1.jpg"):
        Image.new("RGB", (100, 100), color="red").save(src / name)
    return src


@pytest.fixture
def empty_dir(tmp_path: Path) -> Path:
    """Create an empty directory."""
    d = tmp_path / "empty"
    d.mkdir()
    return d
