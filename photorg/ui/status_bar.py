"""
StatusBar widget.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar
from photorg.ui.theme import PANEL, GREEN, MUTED, DIMMER, SURFACE

class StatusBar(QWidget):
    """Displays current app state, notifications, and progress."""

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

        self._progress = QProgressBar()
        self._progress.setFixedSize(100, 10)
        self._progress.setTextVisible(False)
        self._progress.setVisible(False)
        self._progress.setStyleSheet(
            f"QProgressBar {{ background: {SURFACE}; border-radius: 5px; border: none; }}"
            f"QProgressBar::chunk {{ background: {GREEN}; border-radius: 5px; }}"
        )
        h.addWidget(self._progress)

        h.addStretch()

        from photorg import __version__
        ver = QLabel(f"v{__version__}")
        ver.setStyleSheet(f"color: {DIMMER}; font-size: 9px;")
        h.addWidget(ver)

    def set_message(self, text: str) -> None:
        self._msg.setText(text)

    def show_progress(self, visible: bool) -> None:
        self._progress.setVisible(visible)
        if not visible:
            self._progress.setValue(0)

    def set_progress(self, current: int, total: int) -> None:
        self._progress.setMaximum(total)
        self._progress.setValue(current)
