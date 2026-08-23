"""
QThread wrapper for DayOrganiser.
Runs the I/O-heavy processing in the background to keep the UI responsive.
"""
from pathlib import Path
from PySide6.QtCore import QThread, Signal
from photorg.core.organiser import DayOrganiser


class DayOrganiserWorker(QThread):
    """Background thread for running the DayOrganiser."""
    
    progress = Signal(int, int, str)  # current, total, message
    finished = Signal()
    error = Signal(str)

    def __init__(self, source: Path, destination: Path, title: str, parent=None) -> None:
        super().__init__(parent)
        self.organiser = DayOrganiser(source, destination, title)
        
        # Wire backend callbacks directly to Qt signals
        self.organiser.on_progress = lambda c, t, m: self.progress.emit(c, t, m)
        self.organiser.on_complete = lambda: self.finished.emit()
        self.organiser.on_error = lambda e: self.error.emit(e)

    def run(self) -> None:
        self.organiser.run()
