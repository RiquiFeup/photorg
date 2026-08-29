"""Unit tests for photorg.core.organiser – Day Organiser logic."""
from __future__ import annotations

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from photorg.core.organiser import DayOrganiser


# ── helpers ──────────────────────────────────────────────────────────────


def _make_images(directory: Path, names: list[str]) -> list[Path]:
    """Create minimal JPEG files and return their paths."""
    paths = []
    for name in names:
        p = directory / name
        Image.new("RGB", (1, 1)).save(p)
        paths.append(p)
    return paths


# ── tests ────────────────────────────────────────────────────────────────


class TestDayOrganiserFolderStructure:
    """Verify the nested output structure: <dest>/<title>/Day NN/…"""

    def test_creates_nested_day_folders(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _make_images(src, ["a.jpg", "b.jpg", "c.jpg"])
        dest = tmp_path / "out"

        dates = iter([
            datetime(2024, 6, 15),
            datetime(2024, 6, 15),
            datetime(2024, 6, 16),
        ])

        with patch("photorg.core.organiser.get_capture_date", side_effect=dates):
            org = DayOrganiser(src, dest, "Italy Trip")
            org.run()

        root = dest / "Italy Trip"
        assert root.is_dir()
        assert (root / "Day 01").is_dir()
        assert (root / "Day 02").is_dir()
        assert len(list((root / "Day 01").iterdir())) == 2
        assert len(list((root / "Day 02").iterdir())) == 1

    def test_unknown_date_group(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _make_images(src, ["x.jpg"])
        dest = tmp_path / "out"

        with patch("photorg.core.organiser.get_capture_date", return_value=None):
            org = DayOrganiser(src, dest, "Trip")
            org.run()

        assert (dest / "Trip" / "Unknown Date").is_dir()

    def test_mixed_known_and_unknown(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _make_images(src, ["a.jpg", "b.jpg"])
        dest = tmp_path / "out"

        dates = iter([datetime(2024, 1, 1), None])
        with patch("photorg.core.organiser.get_capture_date", side_effect=dates):
            org = DayOrganiser(src, dest, "Trip")
            org.run()

        assert (dest / "Trip" / "Day 01").is_dir()
        assert (dest / "Trip" / "Unknown Date").is_dir()


class TestDayOrganiserCopyMode:
    """Verify copy mode preserves original files."""

    def test_originals_preserved(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        imgs = _make_images(src, ["photo.jpg"])
        dest = tmp_path / "out"

        with patch("photorg.core.organiser.get_capture_date",
                    return_value=datetime(2024, 1, 1)):
            org = DayOrganiser(src, dest, "Trip", mode="copy")
            org.run()

        # Original still exists
        assert imgs[0].exists()
        # Copy exists in output
        assert (dest / "Trip" / "Day 01" / "photo.jpg").exists()


class TestDayOrganiserMoveMode:
    """Verify move mode removes original files."""

    def test_originals_removed(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        imgs = _make_images(src, ["photo.jpg"])
        dest = tmp_path / "out"

        with patch("photorg.core.organiser.get_capture_date",
                    return_value=datetime(2024, 1, 1)):
            org = DayOrganiser(src, dest, "Trip", mode="move")
            org.run()

        # Original removed
        assert not imgs[0].exists()
        # File exists in output
        assert (dest / "Trip" / "Day 01" / "photo.jpg").exists()


class TestDayOrganiserCallbacks:
    """Verify lifecycle callbacks fire correctly."""

    def test_empty_source_fires_error(self, tmp_path: Path) -> None:
        src = tmp_path / "empty"
        src.mkdir()
        dest = tmp_path / "out"

        errors: list[str] = []
        org = DayOrganiser(src, dest, "Trip")
        org.on_error = errors.append
        org.run()

        assert len(errors) == 1
        assert "No valid images" in errors[0]

    def test_progress_called_for_every_image(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _make_images(src, ["a.jpg", "b.jpg", "c.jpg"])
        dest = tmp_path / "out"

        progress: list[tuple[int, int, str]] = []

        with patch("photorg.core.organiser.get_capture_date",
                    return_value=datetime(2024, 1, 1)):
            org = DayOrganiser(src, dest, "Trip")
            org.on_progress = lambda c, t, m: progress.append((c, t, m))
            org.run()

        assert len(progress) == 3
        assert progress[-1][0] == progress[-1][1]  # last current == total

    def test_complete_called_with_count(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _make_images(src, ["a.jpg"])
        dest = tmp_path / "out"

        completed: list[int] = []

        with patch("photorg.core.organiser.get_capture_date",
                    return_value=datetime(2024, 1, 1)):
            org = DayOrganiser(src, dest, "Trip")
            org.on_complete = completed.append
            org.run()

        assert completed == [1]


class TestDayOrganiserCancellation:
    """Verify cancellation stops processing."""

    def test_cancel_before_start(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _make_images(src, ["a.jpg"])
        dest = tmp_path / "out"

        org = DayOrganiser(src, dest, "Trip")
        org.cancel()
        org.run()

        assert not dest.exists()

    def test_is_cancelled_property(self) -> None:
        org = DayOrganiser(Path("."), Path("."), "T")
        assert not org.is_cancelled
        org.cancel()
        assert org.is_cancelled


class TestDayOrganiserEdgeCases:
    """Edge cases and robustness tests."""

    def test_title_is_stripped(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _make_images(src, ["a.jpg"])
        dest = tmp_path / "out"

        with patch("photorg.core.organiser.get_capture_date",
                    return_value=datetime(2024, 1, 1)):
            org = DayOrganiser(src, dest, "  My Trip  ")
            org.run()

        assert (dest / "My Trip" / "Day 01").is_dir()

    def test_filename_collisions_handled(self, tmp_path: Path) -> None:
        """Same-name files in different subdirs get de-duped."""
        src = tmp_path / "src"
        sub1 = src / "batch1"
        sub2 = src / "batch2"
        sub1.mkdir(parents=True)
        sub2.mkdir(parents=True)
        Image.new("RGB", (1, 1)).save(sub1 / "photo.jpg")
        Image.new("RGB", (1, 1)).save(sub2 / "photo.jpg")
        dest = tmp_path / "out"

        with patch("photorg.core.organiser.get_capture_date",
                    return_value=datetime(2024, 1, 1)):
            org = DayOrganiser(src, dest, "Trip")
            org.run()

        day_dir = dest / "Trip" / "Day 01"
        files = list(day_dir.iterdir())
        assert len(files) == 2  # photo.jpg + photo_1.jpg
