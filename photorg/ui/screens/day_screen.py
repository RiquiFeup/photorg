"""
Day Organizer screen.

Combines the DropZone (left) with a scrollable configuration panel
(right) for setting the output title, destination, copy/move mode,
and triggering the organise action.

UI improvements
---------------
- Drop zone is always visible regardless of window size.
- All styling via global QSS objectName selectors — zero inline
  setStyleSheet() calls, eliminating stylesheet parse errors.
- Primary button: green background + white text.
- Cancel button: always present in layout, disabled when idle
  (prevents layout shift when toggling running state).
- Live path preview updates as the user types the folder title.
- Thin separator lines between config sections for visual clarity.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel,
    QLineEdit, QPushButton, QComboBox, QScrollArea,
)
from PySide6.QtCore import Qt, Signal

from photorg.ui.widgets.drop_zone import DropZone
from photorg.ui.widgets.browse_row import make_browse_row


def _h_sep() -> QFrame:
    """Return a thin horizontal separator line."""
    sep = QFrame()
    sep.setObjectName("h_sep")
    sep.setFrameShape(QFrame.HLine)
    return sep


class _DayConfigPanel(QFrame):
    """Right-side configuration panel for the Day Organizer."""

    run_clicked    = Signal(str, str, str)  # (title, destination, mode)
    cancel_clicked = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("panel")
        self._build()

    def _build(self) -> None:
        v = QVBoxLayout(self)
        v.setContentsMargins(28, 28, 28, 28)
        v.setSpacing(0)

        # ── Panel title ──────────────────────────────────────────────────
        title = QLabel("Configuration")
        title.setObjectName("panel_title")
        v.addWidget(title)
        v.addSpacing(24)

        # ── Folder title ─────────────────────────────────────────────────
        lbl1 = QLabel("FOLDER TITLE")
        lbl1.setObjectName("section_label")
        v.addWidget(lbl1)
        v.addSpacing(6)

        self._title_entry = QLineEdit()
        self._title_entry.setPlaceholderText("e.g.  Italy Trip")
        self._title_entry.textChanged.connect(self._update_preview)
        v.addWidget(self._title_entry)
        v.addSpacing(4)

        self._preview_lbl = QLabel("📂  <title> / Day 01 / photo.jpg")
        self._preview_lbl.setObjectName("preview_path")
        v.addWidget(self._preview_lbl)
        v.addSpacing(20)

        v.addWidget(_h_sep())
        v.addSpacing(20)

        # ── Destination folder ────────────────────────────────────────────
        dest_row, self._dest_entry = make_browse_row(
            "DESTINATION FOLDER", "Choose output location…"
        )
        v.addWidget(dest_row)
        v.addSpacing(20)

        v.addWidget(_h_sep())
        v.addSpacing(20)

        # ── File mode ─────────────────────────────────────────────────────
        lbl_mode = QLabel("FILE MODE")
        lbl_mode.setObjectName("section_label")
        v.addWidget(lbl_mode)
        v.addSpacing(6)

        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["Copy  (keep originals)", "Move  (remove originals)"])
        # No inline setStyleSheet — global QSS covers QComboBox
        v.addWidget(self._mode_combo)
        v.addStretch()

        # ── Action buttons ────────────────────────────────────────────────
        self._run_btn = QPushButton("Organise by Day")
        self._run_btn.setObjectName("pill_primary")
        self._run_btn.setMinimumHeight(44)
        self._run_btn.clicked.connect(self._on_run)
        v.addWidget(self._run_btn)

        v.addSpacing(8)

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setObjectName("cancel")
        self._cancel_btn.setEnabled(False)          # disabled when idle
        self._cancel_btn.clicked.connect(self.cancel_clicked.emit)
        v.addWidget(self._cancel_btn)

    # ── Helpers ──────────────────────────────────────────────────────────

    def _update_preview(self, text: str) -> None:
        label = text.strip() or "<title>"
        self._preview_lbl.setText(f"{label} / Day 01 / photo.jpg")

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
        self._run_btn.setText("Processing..." if running else "Organise by Day")
        self._cancel_btn.setEnabled(running)


class DayScreen(QWidget):
    """Day Organizer view."""

    folder_selected = Signal(str)
    run_requested   = Signal(str, str, str)   # (title, destination, mode)
    cancel_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        h = QHBoxLayout(self)
        h.setContentsMargins(16, 16, 16, 16)
        h.setSpacing(12)

        # Drop zone — always visible
        self.drop_zone = DropZone()
        self.drop_zone.folder_dropped.connect(self.folder_selected.emit)
        h.addWidget(self.drop_zone, 5)

        # Config panel wrapped in a scroll area for small screens
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
