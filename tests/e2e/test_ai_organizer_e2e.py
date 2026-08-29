"""End-to-end test for the AI Organizer pipeline (with mocked model inference)."""
from __future__ import annotations

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from PIL import Image

from photorg.core.ai_classifier import AIOrganiser


class TestAIOrganizerE2E:
    """E2E testing of the AIOrganiser file transfer process."""

    def test_full_pipeline_with_scene_subfolders(self, tmp_path: Path) -> None:
        """Complete pipeline: source dir → grouped day folders → scene folders."""
        src = tmp_path / "vacation"
        src.mkdir()
        dest = tmp_path / "output"

        # Create images
        for name in ["beach1.jpg", "museum1.jpg", "beach2.jpg"]:
            Image.new("RGB", (1, 1)).save(src / name)

        dates = [datetime(2024, 7, 1)] * 3
        scenes = ["Beach", "Museum", "Beach"]

        mock_classifier = MagicMock()
        mock_classifier.classify.side_effect = scenes

        with patch("photorg.core.ai_classifier.get_capture_date", side_effect=dates), \
             patch("photorg.core.ai_classifier.SceneClassifier", return_value=mock_classifier):
            
            org = AIOrganiser(src, dest, "Italy", ["beach", "museum"], mode="copy")
            completed = []
            org.on_complete = completed.append
            org.run()

        assert len(completed) == 1
        assert completed[0] == 3

        root = dest / "Italy" / "Day 01"
        assert (root / "Beach").is_dir()
        assert (root / "Museum").is_dir()
        
        assert len(list((root / "Beach").iterdir())) == 2
        assert len(list((root / "Museum").iterdir())) == 1

    def test_move_mode_removes_originals(self, tmp_path: Path) -> None:
        """Verify move mode properly removes source files."""
        src = tmp_path / "vacation"
        src.mkdir()
        dest = tmp_path / "output"
        
        orig_file = src / "test.jpg"
        Image.new("RGB", (1, 1)).save(orig_file)
        
        mock_classifier = MagicMock()
        mock_classifier.classify.return_value = "Park"

        with patch("photorg.core.ai_classifier.get_capture_date", return_value=datetime(2024, 1, 1)), \
             patch("photorg.core.ai_classifier.SceneClassifier", return_value=mock_classifier):
            
            org = AIOrganiser(src, dest, "Trip", ["park"], mode="move")
            org.run()

        # The source file should be gone
        assert not orig_file.exists()
        # The file should be in destination
        assert (dest / "Trip" / "Day 01" / "Park" / "test.jpg").is_file()
