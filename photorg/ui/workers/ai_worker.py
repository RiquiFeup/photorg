"""
QThread wrapper for AIOrganiser.

Runs the AI classification and file organisation in the background
to keep the UI responsive.  Supports cancellation and copy/move modes.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from PySide6.QtCore import QThread, Signal

from photorg.core.ai_classifier import AIOrganiser


class AIOrganiserWorker(QThread):
    """Background thread for running the AIOrganiser."""

    progress = Signal(int, int, str)  # current, total, message
    finished = Signal(int)            # total files processed
    error = Signal(str)

    def __init__(
        self,
        source: Path,
        destination: Path,
        title: str,
        places: list[str],
        *,
        mode: Literal["copy", "move"] = "copy",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._organiser = AIOrganiser(
            source, destination, title, places, mode=mode,
        )
        self._organiser.on_progress = lambda c, t, m: self.progress.emit(c, t, m)
        self._organiser.on_complete = lambda n: self.finished.emit(n)
        self._organiser.on_error = lambda e: self.error.emit(e)

    def run(self) -> None:
        self._organiser.run()

    def cancel(self) -> None:
        """Request cancellation of the running organiser."""
        self._organiser.cancel()
