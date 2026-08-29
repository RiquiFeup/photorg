"""
QThread wrapper for DayOrganiser.

Runs the I/O-heavy processing in the background to keep the UI
responsive.  Supports cancellation and copy/move modes.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from PySide6.QtCore import QThread, Signal

from photorg.core.organiser import DayOrganiser


class DayOrganiserWorker(QThread):
    """Background thread for running the DayOrganiser."""

    progress = Signal(int, int, str)  # current, total, message
    finished = Signal(int)            # total files processed
    error = Signal(str)

    def __init__(
        self,
        source: Path,
        destination: Path,
        title: str,
        *,
        mode: Literal["copy", "move"] = "copy",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._organiser = DayOrganiser(
            source, destination, title, mode=mode,
        )
        self._organiser.on_progress = lambda c, t, m: self.progress.emit(c, t, m)
        self._organiser.on_complete = lambda n: self.finished.emit(n)
        self._organiser.on_error = lambda e: self.error.emit(e)

    def run(self) -> None:
        self._organiser.run()

    def cancel(self) -> None:
        """Request cancellation of the running organiser."""
        self._organiser.cancel()
