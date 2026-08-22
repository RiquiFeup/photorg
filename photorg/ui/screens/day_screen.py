"""
Day Organizer screen.

Combines the DropZone and the DayConfigPanel.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Signal

from photorg.ui.theme import TEXT, MUTED, DIMMER
from photorg.ui.widgets.drop_zone import DropZone
from photorg.ui.widgets.browse_row import make_browse_row


class _DayConfigPanel(QFrame):
    """Right-side configuration panel for the Day Organizer."""

    run_clicked = Signal(str, str)  # (title, destination)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("panel")
        self._build()

    def _build(self) -> None:
        v = QVBoxLayout(self)
        v.setContentsMargins(28, 28, 28, 28)
        v.setSpacing(0)

        title = QLabel("Configuration")
        title.setStyleSheet(f"color: {TEXT}; font-size: 13px; font-weight: 700;")
        v.addWidget(title)
        v.addSpacing(22)

        lbl1 = QLabel("->  Folder title")
        lbl1.setStyleSheet(f"color: {MUTED}; font-size: 10px;")
        v.addWidget(lbl1)
        v.addSpacing(5)

        self._title_entry = QLineEdit()
        self._title_entry.setPlaceholderText("e.g.  Italy Trip")
        v.addWidget(self._title_entry)
        v.addSpacing(6)

        suffix = QLabel('Output:   <title> / Day 01 / photo.jpg')
        suffix.setStyleSheet(f"color: {DIMMER}; font-size: 9px;")
        v.addWidget(suffix)
        v.addSpacing(22)

        dest_row, self._dest_entry = make_browse_row(
            "->  Destination folder", "Choose output location..."
        )
        v.addWidget(dest_row)
        v.addStretch()

        run = QPushButton("Organise by Day  ->")
        run.setObjectName("primary")
        run.clicked.connect(self._on_run)
        v.addWidget(run)

    def _on_run(self) -> None:
        self.run_clicked.emit(self._title_entry.text(), self._dest_entry.text())


class DayScreen(QWidget):
    """Day Organizer view."""

    folder_selected = Signal(str)
    run_requested = Signal(str, str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        h = QHBoxLayout(self)
        h.setContentsMargins(16, 16, 16, 16)
        h.setSpacing(12)

        self.drop_zone = DropZone()
        self.drop_zone.folder_dropped.connect(self.folder_selected.emit)
        h.addWidget(self.drop_zone, 5)

        self.config = _DayConfigPanel()
        self.config.run_clicked.connect(self.run_requested.emit)
        h.addWidget(self.config, 6)
