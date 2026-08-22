"""
TagInput widget.

Manages a list of removable chips for defining categories.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QLineEdit, QSizePolicy
from PySide6.QtCore import Qt, Signal

from photorg.ui.theme import MUTED, GREEN, INPUT_BG, INPUT_BD, TEXT


class TagChip(QFrame):
    """A single removable tag chip."""

    removed = Signal(str)

    def __init__(self, text: str, parent=None) -> None:
        super().__init__(parent)
        self.text = text
        self.setFixedHeight(26)
        self.setStyleSheet(
            "QFrame { background-color: #1a3d2b; border-radius: 13px; border: none; }"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 0, 6, 0)
        lay.setSpacing(5)

        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {GREEN}; font-size: 11px; background: transparent;")
        lay.addWidget(lbl)

        x = QPushButton("x")
        x.setFixedSize(14, 14)
        x.setCursor(Qt.PointingHandCursor)
        x.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {GREEN}; border: none; "
            "font-size: 9px; padding: 0; }}"
            "QPushButton:hover { color: #ffffff; }"
        )
        x.clicked.connect(lambda: self.removed.emit(self.text))
        lay.addWidget(x)


class TagInput(QWidget):
    """Input area that converts typed text into inline chips."""

    DEFAULT_TAGS = ["Beach", "Museum", "Park", "Restaurant", "Hotel"]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._tags: list[str] = list(self.DEFAULT_TAGS)
        self._build()

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(6)

        lbl = QLabel("->  Places to scan")
        lbl.setStyleSheet(f"color: {MUTED}; font-size: 10px;")
        outer.addWidget(lbl)

        self._box = QFrame()
        self._box.setStyleSheet(
            f"QFrame {{ background-color: {INPUT_BG}; border: 1px solid {INPUT_BD}; border-radius: 8px; }}"
        )
        self._box.setMinimumHeight(46)
        self._box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        outer.addWidget(self._box)

        self._flow = QHBoxLayout(self._box)
        self._flow.setContentsMargins(8, 8, 8, 8)
        self._flow.setSpacing(6)
        self._flow.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self._entry = QLineEdit()
        self._entry.setPlaceholderText("Add place...")
        self._entry.setFixedWidth(100)
        self._entry.setStyleSheet(
            f"QLineEdit {{ background: transparent; border: none; color: {TEXT}; "
            "font-size: 11px; min-height: 26px; max-height: 26px; padding: 0 4px; }}"
        )
        self._entry.returnPressed.connect(self._add)

        self._render()

    @property
    def tags(self) -> list[str]:
        return list(self._tags)

    def _render(self) -> None:
        while self._flow.count():
            item = self._flow.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for tag in self._tags:
            chip = TagChip(tag)
            chip.removed.connect(self._remove)
            self._flow.addWidget(chip)

        self._flow.addWidget(self._entry)
        self._flow.addStretch()

    def _add(self) -> None:
        val = self._entry.text().strip()
        if val and val not in self._tags:
            self._tags.append(val)
            self._entry.clear()
            self._render()

    def _remove(self, tag: str) -> None:
        if tag in self._tags:
            self._tags.remove(tag)
            self._render()
