"""Unit tests for photorg.core.file_utils – image discovery and safe copy."""
from __future__ import annotations

import pytest
from pathlib import Path

from photorg.core.file_utils import find_images, safe_copy, VALID_EXTENSIONS


# ── find_images ──────────────────────────────────────────────────────────


class TestFindImages:
    """Tests for recursive image file discovery."""

    def test_finds_jpg_and_png(self, tmp_path: Path) -> None:
        (tmp_path / "a.jpg").write_bytes(b"fake-jpg")
        (tmp_path / "b.png").write_bytes(b"fake-png")
        (tmp_path / "c.txt").write_bytes(b"not-an-image")
        result = list(find_images(tmp_path))
        assert len(result) == 2

    def test_finds_all_valid_extensions(self, tmp_path: Path) -> None:
        for ext in VALID_EXTENSIONS:
            (tmp_path / f"img{ext}").write_bytes(b"fake")
        result = list(find_images(tmp_path))
        assert len(result) == len(VALID_EXTENSIONS)

    def test_recursive_discovery(self, tmp_path: Path) -> None:
        sub = tmp_path / "sub" / "deep"
        sub.mkdir(parents=True)
        (sub / "deep.jpeg").write_bytes(b"fake")
        result = list(find_images(tmp_path))
        assert len(result) == 1
        assert result[0].name == "deep.jpeg"

    def test_nonexistent_directory(self, tmp_path: Path) -> None:
        assert list(find_images(tmp_path / "nope")) == []

    def test_file_instead_of_directory(self, tmp_path: Path) -> None:
        f = tmp_path / "file.txt"
        f.write_text("x")
        assert list(find_images(f)) == []

    def test_case_insensitive_extensions(self, tmp_path: Path) -> None:
        (tmp_path / "UPPER.JPG").write_bytes(b"fake")
        (tmp_path / "Mixed.Jpeg").write_bytes(b"fake")
        result = list(find_images(tmp_path))
        assert len(result) == 2

    def test_empty_directory(self, tmp_path: Path) -> None:
        assert list(find_images(tmp_path)) == []

    def test_ignores_hidden_and_non_image(self, tmp_path: Path) -> None:
        (tmp_path / ".hidden.jpg").write_bytes(b"fake")  # hidden but valid ext
        (tmp_path / "doc.pdf").write_bytes(b"fake")
        result = list(find_images(tmp_path))
        # .hidden.jpg has valid extension so it should be found
        assert len(result) == 1


# ── safe_copy ────────────────────────────────────────────────────────────


class TestSafeCopy:
    """Tests for collision-safe file copying."""

    def test_basic_copy(self, tmp_path: Path) -> None:
        src = tmp_path / "original.txt"
        src.write_text("hello world")
        dest = tmp_path / "output" / "original.txt"

        result = safe_copy(src, dest)

        assert result.exists()
        assert result.read_text() == "hello world"
        assert result == dest

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        src = tmp_path / "file.txt"
        src.write_text("data")
        dest = tmp_path / "a" / "b" / "c" / "file.txt"

        result = safe_copy(src, dest)
        assert result.exists()
        assert result.parent.exists()

    def test_collision_appends_counter(self, tmp_path: Path) -> None:
        src = tmp_path / "src.txt"
        src.write_text("new data")

        dest_dir = tmp_path / "output"
        dest_dir.mkdir()
        (dest_dir / "src.txt").write_text("existing")

        result = safe_copy(src, dest_dir / "src.txt")

        assert result.name == "src_1.txt"
        assert result.read_text() == "new data"
        # Original should still exist
        assert (dest_dir / "src.txt").read_text() == "existing"

    def test_multiple_collisions(self, tmp_path: Path) -> None:
        src = tmp_path / "photo.jpg"
        src.write_bytes(b"img-data")

        dest_dir = tmp_path / "output"
        dest_dir.mkdir()
        (dest_dir / "photo.jpg").write_bytes(b"v1")
        (dest_dir / "photo_1.jpg").write_bytes(b"v2")

        result = safe_copy(src, dest_dir / "photo.jpg")
        assert result.name == "photo_2.jpg"

    def test_preserves_metadata(self, tmp_path: Path) -> None:
        """shutil.copy2 should preserve file modification time."""
        src = tmp_path / "meta.txt"
        src.write_text("metadata test")

        import time
        time.sleep(0.1)

        dest = tmp_path / "out" / "meta.txt"
        result = safe_copy(src, dest)

        # copy2 preserves mtime (approximately)
        import os
        src_mtime = os.path.getmtime(src)
        dst_mtime = os.path.getmtime(result)
        assert abs(src_mtime - dst_mtime) < 2.0
