"""
TopBar widget.

App header containing the logo and tab navigation.
Emits ``tab_changed(int)`` when a different tab is clicked.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QPushButton
from PySide6.QtCore import Signal
from PySide6.QtGui import QPainter, QColor

from photorg.ui.theme import PANEL, BORDER, GREEN


class TopBar(QWidget):
    """Main application navigation bar."""

    tab_changed = Signal(int)
    LABELS = ["Day Organizer", "AI Organizer", "Output"]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedHeight(52)
        self.setStyleSheet(f"background-color: {PANEL};")
        self._active: int = 0
        self._btns: list[QPushButton] = []
        self._build()

    def _build(self) -> None:
        h = QHBoxLayout(self)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        logo = QLabel("Photorg")
        logo.setStyleSheet(
            f"color: {GREEN}; font-size: 16px; font-weight: 700; padding: 0 28px 0 20px;"
        )
        h.addWidget(logo)

        vsep = QFrame()
        vsep.setFrameShape(QFrame.VLine)
        vsep.setStyleSheet(f"color: {BORDER};")
        vsep.setFixedWidth(1)
        h.addWidget(vsep)

        for i, label in enumerate(self.LABELS):
            btn = QPushButton(label)
            btn.setObjectName("tab")
            if i == 0:
                btn.setProperty("active", "true")
            btn.clicked.connect(lambda _, idx=i: self._switch(idx))
            h.addWidget(btn)
            self._btns.append(btn)

        h.addStretch()

    def _switch(self, idx: int) -> None:
        if idx == self._active:
            return
        self._active = idx
        for i, btn in enumerate(self._btns):
            btn.setProperty("active", "true" if i == idx else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.tab_changed.emit(idx)
        self.update()  # force repaint for underline

    def paintEvent(self, event) -> None:
        """Draw a 2px green underline beneath the active tab."""
        super().paintEvent(event)
        if not self._btns:
            return
        p = QPainter(self)
        btn = self._btns[self._active]
        p.fillRect(btn.x(), self.height() - 2, btn.width(), 2, QColor(GREEN))
