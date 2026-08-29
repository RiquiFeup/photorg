"""Unit tests for photorg.core.exif – capture-date extraction."""
from __future__ import annotations

import os
import time
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from PIL import Image

from photorg.core.exif import get_capture_date, _parse_exif_datetime, _get_file_mtime


# ── _parse_exif_datetime ─────────────────────────────────────────────────


class TestParseExifDatetime:
    """Tests for the EXIF datetime string parser."""

    def test_standard_colon_format(self) -> None:
        result = _parse_exif_datetime("2024:06:15 14:30:00")
        assert result == datetime(2024, 6, 15, 14, 30, 0)

    def test_dash_format(self) -> None:
        result = _parse_exif_datetime("2024-06-15 14:30:00")
        assert result == datetime(2024, 6, 15, 14, 30, 0)

    def test_subsecond_precision(self) -> None:
        result = _parse_exif_datetime("2024:06:15 14:30:00.123456")
        assert result == datetime(2024, 6, 15, 14, 30, 0, 123456)

    def test_invalid_string_returns_none(self) -> None:
        assert _parse_exif_datetime("not-a-date") is None

    def test_none_input_returns_none(self) -> None:
        assert _parse_exif_datetime(None) is None

    def test_empty_string_returns_none(self) -> None:
        assert _parse_exif_datetime("") is None

    def test_whitespace_is_stripped(self) -> None:
        result = _parse_exif_datetime("  2024:06:15 14:30:00  ")
        assert result == datetime(2024, 6, 15, 14, 30, 0)

    def test_integer_input_returns_none(self) -> None:
        # Some broken EXIF data may store an int instead of a string
        assert _parse_exif_datetime(12345) is None


# ── _get_file_mtime ─────────────────────────────────────────────────────


class TestGetFileMtime:
    """Tests for the file-mtime fallback helper."""

    def test_returns_datetime_for_existing_file(self, tmp_path: Path) -> None:
        f = tmp_path / "sample.txt"
        f.write_text("x")
        result = _get_file_mtime(f)
        assert isinstance(result, datetime)

    def test_returns_none_for_missing_file(self, tmp_path: Path) -> None:
        assert _get_file_mtime(tmp_path / "nope.txt") is None


# ── get_capture_date ─────────────────────────────────────────────────────


class TestGetCaptureDate:
    """Integration tests for the main extraction function."""

    def test_plain_image_falls_back_to_mtime(self, tmp_path: Path) -> None:
        """A Pillow-created image has no EXIF → should return mtime."""
        img_path = tmp_path / "no_exif.jpg"
        Image.new("RGB", (1, 1)).save(img_path)
        result = get_capture_date(img_path)
        assert isinstance(result, datetime)

    def test_nonexistent_file_returns_none(self, tmp_path: Path) -> None:
        result = get_capture_date(tmp_path / "missing.jpg")
        assert result is None

    def test_corrupt_file_returns_none_or_mtime(self, tmp_path: Path) -> None:
        """A file with garbage bytes should not crash."""
        bad = tmp_path / "corrupt.jpg"
        bad.write_bytes(b"\x00\x01\x02\x03")
        result = get_capture_date(bad)
        # Either returns mtime or None – must not raise
        assert result is None or isinstance(result, datetime)

    def test_exif_sub_ifd_is_read(self, tmp_path: Path) -> None:
        """Verify we read from the Exif sub-IFD, not the root IFD."""
        img_path = tmp_path / "photo.jpg"
        img = Image.new("RGB", (1, 1))

        # Inject EXIF via Pillow's API
        from PIL.ExifTags import IFD as _IFD
        exif = img.getexif()
        exif_ifd = exif.get_ifd(_IFD.Exif)
        exif_ifd[36867] = "2023:12:25 10:00:00"
        img.save(img_path, exif=exif.tobytes())

        result = get_capture_date(img_path)
        assert result == datetime(2023, 12, 25, 10, 0, 0)

    def test_root_ifd_datetime_fallback(self, tmp_path: Path) -> None:
        """If sub-IFD has no date, fall back to root IFD tag 306."""
        img_path = tmp_path / "photo.jpg"
        img = Image.new("RGB", (1, 1))

        exif = img.getexif()
        exif[306] = "2023:11:01 08:00:00"
        img.save(img_path, exif=exif.tobytes())

        result = get_capture_date(img_path)
        assert result == datetime(2023, 11, 1, 8, 0, 0)

    def test_png_without_exif(self, tmp_path: Path) -> None:
        """PNG files typically have no EXIF – should fall back to mtime."""
        img_path = tmp_path / "image.png"
        Image.new("RGB", (1, 1)).save(img_path)
        result = get_capture_date(img_path)
        assert isinstance(result, datetime)
