"""Unit tests for photorg.core.ai_classifier – AI Organiser logic."""
from __future__ import annotations

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from PIL import Image

from photorg.core.ai_classifier import AIOrganiser


def _make_images(directory: Path, names: list[str]) -> list[Path]:
    """Create minimal JPEG files and return their paths."""
    paths = []
    for name in names:
        p = directory / name
        Image.new("RGB", (1, 1)).save(p)
        paths.append(p)
    return paths


class TestAIOrganiserErrors:
    """Verify error handling for invalid inputs."""

    def test_empty_source_reports_error(self, tmp_path: Path) -> None:
        src = tmp_path / "empty"
        src.mkdir()
        dest = tmp_path / "out"
        errors: list[str] = []

        org = AIOrganiser(src, dest, "Trip", ["beach", "museum"])
        org.on_error = errors.append
        org.run()

        assert len(errors) == 1
        assert "No valid images" in errors[0]

    def test_empty_places_reports_error(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _make_images(src, ["a.jpg"])
        dest = tmp_path / "out"
        errors: list[str] = []

        org = AIOrganiser(src, dest, "Trip", [])
        org.on_error = errors.append
        org.run()

        assert len(errors) == 1
        assert "No place tags" in errors[0]

    def test_whitespace_only_places_treated_as_empty(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _make_images(src, ["a.jpg"])
        dest = tmp_path / "out"
        errors: list[str] = []

        org = AIOrganiser(src, dest, "Trip", ["  ", ""])
        org.on_error = errors.append
        org.run()

        assert len(errors) == 1
        assert "No place tags" in errors[0]


class TestAIOrganiserCancellation:
    """Verify cancellation stops processing."""

    def test_cancel_before_start(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _make_images(src, ["a.jpg"])
        dest = tmp_path / "out"

        org = AIOrganiser(src, dest, "Trip", ["beach"])
        org.cancel()
        org.run()

        assert not dest.exists()

    def test_is_cancelled_property(self) -> None:
        org = AIOrganiser(Path("."), Path("."), "T", ["beach"])
        assert not org.is_cancelled
        org.cancel()
        assert org.is_cancelled


class TestAIOrganiserPipeline:
    """Integration tests with mocked scene classifier."""

    def test_creates_scene_subfolders(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _make_images(src, ["a.jpg", "b.jpg", "c.jpg"])
        dest = tmp_path / "out"

        mock_classifier = MagicMock()
        mock_classifier.classify.side_effect = ["Beach", "Museum", "Beach"]

        def mock_get_capture_date(path: Path) -> datetime:
            dates = {
                "a.jpg": datetime(2024, 7, 1, 10, 0, 0),
                "b.jpg": datetime(2024, 7, 1, 10, 5, 0),
                "c.jpg": datetime(2024, 7, 1, 10, 10, 0),
            }
            return dates[path.name]

        with patch("photorg.core.ai_classifier.get_capture_date",
                    side_effect=mock_get_capture_date), \
             patch("photorg.core.ai_classifier.SceneClassifier",
                    return_value=mock_classifier):
            org = AIOrganiser(src, dest, "Italy", ["beach", "museum"])
            completed: list[int] = []
            org.on_complete = completed.append
            org.run()

        assert completed == [3]
        root = dest / "Italy" / "Day 01"
        assert (root / "Beach").is_dir()
        assert (root / "Museum").is_dir()
        assert len(list((root / "Beach").iterdir())) == 2
        assert len(list((root / "Museum").iterdir())) == 1

    def test_multi_day_scene_grouping(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _make_images(src, ["a.jpg", "b.jpg"])
        dest = tmp_path / "out"

        dates = iter([datetime(2024, 7, 1), datetime(2024, 7, 2)])
        mock_classifier = MagicMock()
        mock_classifier.classify.side_effect = ["Beach", "Park"]

        with patch("photorg.core.ai_classifier.get_capture_date",
                    side_effect=dates), \
             patch("photorg.core.ai_classifier.SceneClassifier",
                    return_value=mock_classifier):
            org = AIOrganiser(src, dest, "Trip", ["beach", "park"])
            org.run()

        assert (dest / "Trip" / "Day 01" / "Beach").is_dir()
        assert (dest / "Trip" / "Day 02" / "Park").is_dir()

    def test_progress_callback(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _make_images(src, ["a.jpg", "b.jpg"])
        dest = tmp_path / "out"

        mock_classifier = MagicMock()
        mock_classifier.classify.return_value = "Beach"
        progress: list[tuple[int, int, str]] = []

        def mock_get_capture_date2(path: Path) -> datetime:
            dates = {
                "a.jpg": datetime(2024, 7, 1, 10, 0, 0),
                "b.jpg": datetime(2024, 7, 1, 10, 5, 0),
            }
            return dates[path.name]

        with patch("photorg.core.ai_classifier.get_capture_date",
                    side_effect=mock_get_capture_date2), \
             patch("photorg.core.ai_classifier.SceneClassifier",
                    return_value=mock_classifier):
            org = AIOrganiser(src, dest, "Trip", ["beach"])
            org.on_progress = lambda c, t, m: progress.append((c, t, m))
            org.run()

        assert len(progress) == 2
        assert progress[-1][0] == progress[-1][1]

    def test_move_mode_removes_originals(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        imgs = _make_images(src, ["photo.jpg"])
        dest = tmp_path / "out"

        mock_classifier = MagicMock()
        mock_classifier.classify.return_value = "Beach"

        with patch("photorg.core.ai_classifier.get_capture_date",
                    return_value=datetime(2024, 7, 1)), \
             patch("photorg.core.ai_classifier.SceneClassifier",
                    return_value=mock_classifier):
            org = AIOrganiser(src, dest, "Trip", ["beach"], mode="move")
            org.run()

        assert not imgs[0].exists()
        assert (dest / "Trip" / "Day 01" / "Beach" / "photo.jpg").exists()

    def test_burst_optimization_groups_photos(self, tmp_path: Path) -> None:
        """Photos within 60s should be treated as a burst and classified only once."""
        src = tmp_path / "src"
        src.mkdir()
        from photorg.core.file_utils import find_images
        _make_images(src, ["burst1.jpg", "burst2.jpg", "burst3.jpg", "later.jpg"])
        dest = tmp_path / "out"
        
        mock_classifier = MagicMock()
        # Only the first item of each burst should be classified
        mock_classifier.classify.side_effect = ["Beach", "Museum"]

        def mock_get_capture_date(path: Path) -> datetime:
            dates = {
                "burst1.jpg": datetime(2024, 7, 1, 10, 0, 0),
                "burst2.jpg": datetime(2024, 7, 1, 10, 0, 5),   # +5s
                "burst3.jpg": datetime(2024, 7, 1, 10, 0, 45),  # +40s from burst2
                "later.jpg": datetime(2024, 7, 1, 10, 5, 0),    # +5m (new burst)
            }
            return dates[path.name]

        with patch("photorg.core.ai_classifier.get_capture_date", side_effect=mock_get_capture_date), \
             patch("photorg.core.ai_classifier.SceneClassifier", return_value=mock_classifier):
            
            org = AIOrganiser(src, dest, "Trip", ["beach", "museum"])
            org.run()
            
        # The AI classifier should only be called twice (burst head, and later image)
        assert mock_classifier.classify.call_count == 2
        
        # All burst photos should go to the same folder
        beach_dir = dest / "Trip" / "Day 01" / "Beach"
        museum_dir = dest / "Trip" / "Day 01" / "Museum"
        
        assert (beach_dir / "burst1.jpg").exists()
        assert (beach_dir / "burst2.jpg").exists()
        assert (beach_dir / "burst3.jpg").exists()
        assert (museum_dir / "later.jpg").exists()
