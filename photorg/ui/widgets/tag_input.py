"""
TagInput widget.

Manages a list of removable chips for defining categories.

Implementation note
-------------------
Earlier versions called ``deleteLater()`` on *every* widget returned
by ``QHBoxLayout.takeAt()``, which inadvertently destroyed the
persistent ``QLineEdit`` (``self._entry``).  When ``_render()`` later
tried to re-add the deleted widget the Qt C++ side was already gone,
producing ``RuntimeError: Internal C++ object … already deleted``.

The fix is simple: **never delete ``self._entry``**.  We only delete
the ephemeral ``TagChip`` widgets, then re-insert ``self._entry`` at
the end.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QPushButton, QLineEdit, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal

from photorg.ui.theme import MUTED, GREEN, GREEN_DM, INPUT_BG, INPUT_BD, TEXT


class TagChip(QFrame):
    """A single removable tag chip."""

    removed = Signal(str)

    def __init__(self, text: str, parent=None) -> None:
        super().__init__(parent)
        self.text = text
        self.setFixedHeight(26)
        self.setStyleSheet(
            f"QFrame {{ background-color: {GREEN_DM}; border-radius: 13px; border: none; }}"
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
    """Input area that converts typed text into inline chips.

    The ``QLineEdit`` (``self._entry``) is a long-lived widget that is
    **never destroyed** during re-renders.  Only the ``TagChip`` widgets
    are created/destroyed as the tag list changes.
    """

    DEFAULT_TAGS = ["Beach", "Museum", "Park", "Restaurant", "Hotel"]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._tags: list[str] = list(self.DEFAULT_TAGS)
        self._chips: list[TagChip] = []
        self._build()

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(6)

        lbl = QLabel("→  Places / scenes to scan")
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

        # Persistent entry — created once, never destroyed
        self._entry = QLineEdit()
        self._entry.setPlaceholderText("Add place…")
        self._entry.setFixedWidth(100)
        self._entry.setStyleSheet(
            f"QLineEdit {{ background: transparent; border: none; color: {TEXT}; "
            "font-size: 11px; min-height: 26px; max-height: 26px; padding: 0 4px; }}"
        )
        self._entry.returnPressed.connect(self._add)

        self._render()

    @property
    def tags(self) -> list[str]:
        """Return a copy of the current tag list."""
        return list(self._tags)

    def _render(self) -> None:
        """Rebuild the chip layout.

        Only ``TagChip`` instances are destroyed and recreated.
        ``self._entry`` is removed from the layout (not deleted) and
        re-appended at the end.
        """
        # 1. Remove the entry from layout (without deleting it)
        self._flow.removeWidget(self._entry)
        self._entry.setParent(None)

        # 2. Destroy old chips only
        for chip in self._chips:
            self._flow.removeWidget(chip)
            chip.deleteLater()
        self._chips.clear()

        # 3. Remove any leftover spacer items
        while self._flow.count():
            item = self._flow.takeAt(0)
            # No widget deletion here — all widgets already handled

        # 4. Create fresh chips
        for tag in self._tags:
            chip = TagChip(tag)
            chip.removed.connect(self._remove)
            self._flow.addWidget(chip)
            self._chips.append(chip)

        # 5. Re-add the persistent entry at the end
        self._flow.addWidget(self._entry)

    def _add(self) -> None:
        """Add a new tag from the entry field."""
        val = self._entry.text().strip()
        if val and val not in self._tags:
            self._tags.append(val)
            self._entry.clear()
            self._render()

    def _remove(self, tag: str) -> None:
        """Remove a tag by name."""
        if tag in self._tags:
            self._tags.remove(tag)
            self._render()
