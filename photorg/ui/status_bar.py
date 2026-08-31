"""
StatusBar widget.

Displays current app state, notifications, and progress.

UI improvements
---------------
- Height increased to 40px for better readability.
- Font size increased to 11px.
- Progress bar is 180px wide (was 100px).
- State-aware dot colour: green=ready/done, yellow=running, red=error.
- set_state() public method for semantic state transitions.
- Message label is width-capped so the version badge is never pushed off.
"""
from __future__ import annotations

from typing import Literal

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar
from photorg.ui.theme import PANEL, GREEN, MUTED, DIMMER, SURFACE, ERROR, WARNING


_STATE_COLORS: dict[str, str] = {
    "ready":   GREEN,
    "running": WARNING,
    "error":   ERROR,
    "success": GREEN,
}


class StatusBar(QWidget):
    """Displays current app state, notifications, and progress."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setStyleSheet(f"background-color: {PANEL};")

        h = QHBoxLayout(self)
        h.setContentsMargins(16, 0, 16, 0)
        h.setSpacing(10)

        self._dot = QLabel("●")
        self._dot.setStyleSheet(f"color: {GREEN}; font-size: 10px;")
        h.addWidget(self._dot)

        self._msg = QLabel("No folder selected")
        self._msg.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        self._msg.setMaximumWidth(500)
        h.addWidget(self._msg)

        self._progress = QProgressBar()
        self._progress.setFixedWidth(180)
        self._progress.setTextVisible(False)
        self._progress.setVisible(False)
        # Progress bar styled by global QSS (QProgressBar selector)
        h.addWidget(self._progress)

        h.addStretch()

        from photorg import __version__
        ver = QLabel(f"v{__version__}")
        ver.setStyleSheet(f"color: {DIMMER}; font-size: 9px;")
        h.addWidget(ver)

    # ── Public API ────────────────────────────────────────────────────────

    def set_message(self, text: str) -> None:
        self._msg.setText(text)

    def set_state(self, state: Literal["ready", "running", "error", "success"]) -> None:
        """Change the status dot colour to reflect the app state."""
        color = _STATE_COLORS.get(state, GREEN)
        self._dot.setStyleSheet(f"color: {color}; font-size: 10px;")

    def show_progress(self, visible: bool) -> None:
        self._progress.setVisible(visible)
        if not visible:
            self._progress.setValue(0)

    def set_progress(self, current: int, total: int) -> None:
        self._progress.setMaximum(total)
        self._progress.setValue(current)
