"""
AI Organizer screen.

Status: Stub for Commit 1.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Signal

from photorg.ui.theme import MUTED


class AIScreen(QWidget):
    """AI Organizer view (Stub)."""

    folder_selected = Signal(str)
    run_requested = Signal(str, list, str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        v = QVBoxLayout(self)
        lbl = QLabel("AI Organizer: Coming soon in feat(ui)")
        lbl.setStyleSheet(f"color: {MUTED};")
        v.addWidget(lbl)
