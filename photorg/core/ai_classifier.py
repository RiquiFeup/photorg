"""
AI Classifier – core logic.

Uses a vision model to classify photos by scene type (beach, museum,
park, …) and places them into labelled subfolders within each day folder.

Status: stub — UI is wired; logic not yet implemented.
"""
from __future__ import annotations
from pathlib import Path


class AIClassifier:
    """Classifies and groups photos by detected scene / location type."""

    def __init__(
        self,
        source: Path,
        destination: Path,
        folder_title: str,
        places: list[str],
    ) -> None:
        self.source = source
        self.destination = destination
        self.folder_title = folder_title
        self.places = places

    def run(self) -> None:
        """Execute the classification process."""
        raise NotImplementedError("AI classifier logic not yet implemented.")
