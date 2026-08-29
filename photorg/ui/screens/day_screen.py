"""
Day Organizer screen.

Combines the DropZone (left) with a scrollable configuration panel
(right) for setting the output title, destination, copy/move mode,
and triggering the organise action.

The config panel is wrapped in a ``QScrollArea`` so the "Organise"
button is always reachable regardless of window size.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel,
    QLineEdit, QPushButton, QComboBox, QScrollArea,
)
from PySide6.QtCore import Qt, Signal

from photorg.ui.theme import TEXT, MUTED, DIMMER, INPUT_BG, INPUT_BD, SURFACE, GREEN
from photorg.ui.widgets.drop_zone import DropZone
from photorg.ui.widgets.browse_row import make_browse_row


class _DayConfigPanel(QFrame):
    """Right-side configuration panel for the Day Organizer."""

    run_clicked = Signal(str, str, str)   # (title, destination, mode)
    cancel_clicked = Signal()

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

        lbl1 = QLabel("→  Folder title")
        lbl1.setStyleSheet(f"color: {MUTED}; font-size: 10px;")
        v.addWidget(lbl1)
        v.addSpacing(5)

        self._title_entry = QLineEdit()
        self._title_entry.setPlaceholderText("e.g.  Italy Trip")
        v.addWidget(self._title_entry)
        v.addSpacing(6)

        suffix = QLabel("Output:   <title> / Day 01 / photo.jpg")
        suffix.setStyleSheet(f"color: {DIMMER}; font-size: 9px;")
        v.addWidget(suffix)
        v.addSpacing(22)

        dest_row, self._dest_entry = make_browse_row(
            "→  Destination folder", "Choose output location..."
        )
        v.addWidget(dest_row)
        v.addSpacing(20)

        # Mode selector
        lbl_mode = QLabel("→  File mode")
        lbl_mode.setStyleSheet(f"color: {MUTED}; font-size: 10px;")
        v.addWidget(lbl_mode)
        v.addSpacing(5)

        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["Copy (keep originals)", "Move (remove originals)"])
        self._mode_combo.setStyleSheet(
            f"QComboBox {{ background: {INPUT_BG}; border: 1px solid {INPUT_BD};"
            f" border-radius: 6px; color: {TEXT}; padding: 6px 10px;"
            f" min-height: 22px; font-size: 11px; }}"
            f"QComboBox::drop-down {{ border: none; width: 24px; }}"
            f"QComboBox QAbstractItemView {{ background: {SURFACE};"
            f" color: {TEXT}; selection-background-color: {INPUT_BD}; }}"
        )
        v.addWidget(self._mode_combo)
        v.addStretch()

        # Action buttons
        self._run_btn = QPushButton("Organise by Day  →")
        self._run_btn.setObjectName("primary")
        self._run_btn.setMinimumHeight(42)
        self._run_btn.clicked.connect(self._on_run)
        v.addWidget(self._run_btn)

        v.addSpacing(6)

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {MUTED}; border: 1px solid {INPUT_BD};"
            f" border-radius: 8px; font-size: 11px; min-height: 34px; }}"
            f"QPushButton:hover {{ color: #ff6b6b; border-color: #ff6b6b; }}"
        )
        self._cancel_btn.setVisible(False)
        self._cancel_btn.clicked.connect(self.cancel_clicked.emit)
        v.addWidget(self._cancel_btn)

    @property
    def selected_mode(self) -> str:
        return "move" if self._mode_combo.currentIndex() == 1 else "copy"

    def _on_run(self) -> None:
        self.run_clicked.emit(
            self._title_entry.text(),
            self._dest_entry.text(),
            self.selected_mode,
        )

    def set_running(self, running: bool) -> None:
        """Toggle UI between idle and processing states."""
        self._run_btn.setEnabled(not running)
        self._run_btn.setText("Processing…" if running else "Organise by Day  →")
        self._cancel_btn.setVisible(running)


class DayScreen(QWidget):
    """Day Organizer view."""

    folder_selected = Signal(str)
    run_requested = Signal(str, str, str)   # (title, destination, mode)
    cancel_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        h = QHBoxLayout(self)
        h.setContentsMargins(16, 16, 16, 16)
        h.setSpacing(12)

        self.drop_zone = DropZone()
        self.drop_zone.folder_dropped.connect(self.folder_selected.emit)
        h.addWidget(self.drop_zone, 5)

        # Wrap config panel in a scroll area for small screens
        self.config = _DayConfigPanel()
        self.config.run_clicked.connect(self.run_requested.emit)
        self.config.cancel_clicked.connect(self.cancel_requested.emit)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.config)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        h.addWidget(scroll, 6)

    def set_running(self, running: bool) -> None:
        """Propagate running state to the config panel."""
        self.config.set_running(running)
