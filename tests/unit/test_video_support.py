"""Unit tests for photorg.core.video_utils and video support in file_utils."""
from __future__ import annotations

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from photorg.core.file_utils import (
    find_media, find_images, is_video,
    VIDEO_EXTENSIONS, VALID_EXTENSIONS, MEDIA_EXTENSIONS,
)


# ── Extension sets ───────────────────────────────────────────────────────


class TestExtensionSets:
    """Verify extension sets are correct and disjoint."""

    def test_video_extensions_exist(self) -> None:
        assert ".mov" in VIDEO_EXTENSIONS
        assert ".mp4" in VIDEO_EXTENSIONS
        assert ".avi" in VIDEO_EXTENSIONS
        assert ".mkv" in VIDEO_EXTENSIONS

    def test_media_is_union(self) -> None:
        assert MEDIA_EXTENSIONS == VALID_EXTENSIONS | VIDEO_EXTENSIONS

    def test_no_overlap(self) -> None:
        assert VALID_EXTENSIONS & VIDEO_EXTENSIONS == frozenset()


# ── is_video ─────────────────────────────────────────────────────────────


class TestIsVideo:
    """Verify is_video correctly identifies video files."""

    def test_mov_is_video(self) -> None:
        assert is_video(Path("clip.mov"))

    def test_mp4_is_video(self) -> None:
        assert is_video(Path("clip.MP4"))

    def test_jpg_is_not_video(self) -> None:
        assert not is_video(Path("photo.jpg"))

    def test_png_is_not_video(self) -> None:
        assert not is_video(Path("image.png"))


# ── find_media ───────────────────────────────────────────────────────────


class TestFindMedia:
    """Verify find_media discovers both images and videos."""

    def test_finds_images_and_videos(self, tmp_path: Path) -> None:
        (tmp_path / "photo.jpg").write_bytes(b"fake")
        (tmp_path / "video.mov").write_bytes(b"fake")
        (tmp_path / "doc.txt").write_bytes(b"fake")
        result = list(find_media(tmp_path))
        assert len(result) == 2

    def test_find_images_excludes_videos(self, tmp_path: Path) -> None:
        """find_images must NOT return video files (backward compat)."""
        (tmp_path / "photo.jpg").write_bytes(b"fake")
        (tmp_path / "video.mov").write_bytes(b"fake")
        result = list(find_images(tmp_path))
        assert len(result) == 1
        assert result[0].name == "photo.jpg"

    def test_video_extensions_case_insensitive(self, tmp_path: Path) -> None:
        (tmp_path / "CLIP.MOV").write_bytes(b"fake")
        (tmp_path / "clip.Mp4").write_bytes(b"fake")
        result = list(find_media(tmp_path))
        assert len(result) == 2


# ── video_utils ──────────────────────────────────────────────────────────


class TestVideoUtils:
    """Tests for extract_frame and get_video_date (mocked)."""

    def test_extract_frame_returns_none_for_invalid_file(self, tmp_path: Path) -> None:
        """Corrupt/missing video should return None, not crash."""
        from photorg.core.video_utils import extract_frame

        bad = tmp_path / "corrupt.mov"
        bad.write_bytes(b"\x00\x01\x02")
        result = extract_frame(bad)
        assert result is None

    def test_get_video_date_falls_back_to_mtime(self, tmp_path: Path) -> None:
        """If no container metadata, fall back to file mtime."""
        from photorg.core.video_utils import get_video_date

        f = tmp_path / "test.mov"
        f.write_bytes(b"\x00\x01\x02")
        result = get_video_date(f)
        assert isinstance(result, datetime)

    def test_get_video_date_nonexistent_file(self, tmp_path: Path) -> None:
        """Nonexistent file should return None."""
        from photorg.core.video_utils import get_video_date

        result = get_video_date(tmp_path / "nope.mov")
        assert result is None
