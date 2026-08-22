"""
Day Organiser – core logic.

Reads EXIF DateTimeOriginal from each image and copies files into
date-grouped subfolders: <destination>/<title>/Day NN - <date>/<file>

Status: stub — UI is wired; logic not yet implemented.
"""
from __future__ import annotations
from pathlib import Path


class DayOrganiser:
    """Groups photos by capture date into sequential day folders."""

    def __init__(
        self,
        source: Path,
        destination: Path,
        folder_title: str,
    ) -> None:
        self.source = source
        self.destination = destination
        self.folder_title = folder_title

    def run(self) -> None:
        """Execute the organisation process."""
        raise NotImplementedError("Day organiser logic not yet implemented.")
