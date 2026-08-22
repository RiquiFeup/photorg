"""
StatusBar widget.

Global application status footer.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

from photorg.ui.theme import PANEL, GREEN, MUTED, DIMMER


class StatusBar(QWidget):
    """Displays current app state, notifications, and version."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedHeight(28)
        self.setStyleSheet(f"background-color: {PANEL};")

        h = QHBoxLayout(self)
        h.setContentsMargins(16, 0, 16, 0)
        h.setSpacing(8)

        dot = QLabel("\u25cf  Ready")
        dot.setStyleSheet(f"color: {GREEN}; font-size: 10px;")
        h.addWidget(dot)

        self._msg = QLabel("No folder selected")
        self._msg.setStyleSheet(f"color: {MUTED}; font-size: 10px;")
        h.addWidget(self._msg)

        h.addStretch()

        from photorg import __version__
        ver = QLabel(f"v{__version__}")
        ver.setStyleSheet(f"color: {DIMMER}; font-size: 9px;")
        h.addWidget(ver)

    def set_message(self, text: str) -> None:
        """Update the status message."""
        self._msg.setText(text)
