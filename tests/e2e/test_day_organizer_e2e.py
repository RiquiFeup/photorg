"""End-to-end tests for the Day Organizer pipeline."""
from __future__ import annotations

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from photorg.core.organiser import DayOrganiser


class TestDayOrganizerE2E:
    """E2E testing of the DayOrganiser file transfer process."""

    def test_full_pipeline_three_days(self, tmp_path: Path) -> None:
        """Complete pipeline: source dir → grouped day folders."""
        src = tmp_path / "vacation"
        src.mkdir()
        dest = tmp_path / "output"

        # Create 5 images
        for name in ["a.jpg", "b.jpg", "c.jpg", "d.jpg", "e.jpg"]:
            Image.new("RGB", (1, 1)).save(src / name)

        dates = [
            datetime(2024, 7, 1),  # Day 01
            datetime(2024, 7, 1),  # Day 01
            datetime(2024, 7, 2),  # Day 02
            datetime(2024, 7, 2),  # Day 02
            datetime(2024, 7, 3),  # Day 03
        ]

        with patch("photorg.core.organiser.get_capture_date", side_effect=dates):
            org = DayOrganiser(src, dest, "Summer 2024", mode="copy")
            completed = []
            org.on_complete = completed.append
            org.run()

        assert len(completed) == 1
        assert completed[0] == 5

        root = dest / "Summer 2024"
        assert root.is_dir()
        assert (root / "Day 01").is_dir()
        assert (root / "Day 02").is_dir()
        assert (root / "Day 03").is_dir()
        
        assert len(list((root / "Day 01").iterdir())) == 2
        assert len(list((root / "Day 02").iterdir())) == 2
        assert len(list((root / "Day 03").iterdir())) == 1

    def test_all_unknown_dates(self, tmp_path: Path) -> None:
        """All photos without dates go to 'Unknown Date' folder."""
        src = tmp_path / "photos"
        src.mkdir()
        dest = tmp_path / "output"
        Image.new("RGB", (1, 1)).save(src / "x.jpg")

        with patch("photorg.core.organiser.get_capture_date", return_value=None):
            org = DayOrganiser(src, dest, "Trip")
            org.run()

        assert (dest / "Trip" / "Unknown Date").is_dir()
        assert (dest / "Trip" / "Unknown Date" / "x.jpg").is_file()

    def test_filename_collision_handled(self, tmp_path: Path) -> None:
        """Same-named files in different subdirs don't overwrite each other."""
        src = tmp_path / "photos"
        sub1 = src / "batch1"
        sub2 = src / "batch2"
        sub1.mkdir(parents=True)
        sub2.mkdir(parents=True)
        Image.new("RGB", (1, 1)).save(sub1 / "photo.jpg")
        Image.new("RGB", (1, 1)).save(sub2 / "photo.jpg")

        dest = tmp_path / "output"

        with patch("photorg.core.organiser.get_capture_date",
                   return_value=datetime(2024, 1, 1)):
            org = DayOrganiser(src, dest, "Trip")
            org.run()

        day_dir = dest / "Trip" / "Day 01"
        files = sorted([f.name for f in day_dir.iterdir()])
        assert len(files) == 2
        assert "photo.jpg" in files
        assert "photo_1.jpg" in files
