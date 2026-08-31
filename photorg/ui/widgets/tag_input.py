"""
TagInput widget.

Manages a list of removable chips for defining AI scene categories.

Layout
------
- Section header: green accent bar + "AI CATEGORIES" label
- Wrapping chip box:  chips laid out with FlowLayout so they wrap to
  new rows instead of clipping off-screen on narrow windows.
- Below the box: a visible [+ Add] pill button and an inline text entry.
- Helper hint text: "Type a place and press Enter or click + Add"

Implementation note
-------------------
``self._entry`` is a *long-lived* widget created once and re-inserted
into the layout on every ``_render()`` call — it is **never deleted**.
Only the ephemeral ``TagChip`` widgets are destroyed and recreated.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QPushButton, QLineEdit, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal

from photorg.ui.theme import GREEN
from photorg.ui.widgets.flow_layout import FlowLayout


class TagChip(QFrame):
    """A single removable tag chip."""

    removed = Signal(str)

    def __init__(self, text: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("tag_chip")
        self.text = text
        self.setFixedHeight(26)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 0, 6, 0)
        lay.setSpacing(4)

        lbl = QLabel(text)
        # Inline color only — not a structural rule, safe to keep here
        lbl.setStyleSheet(
            f"color: {GREEN}; font-size: 11px; background: transparent;"
        )
        lay.addWidget(lbl)

        x = QPushButton("×")
        x.setObjectName("chip_remove")   # picks up global QSS — no inline style
        x.setFixedSize(16, 16)
        x.setCursor(Qt.PointingHandCursor)
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

        # ── Section header ──────────────────────────────────────────────
        header_row = QWidget()
        hr = QHBoxLayout(header_row)
        hr.setContentsMargins(0, 0, 0, 0)
        hr.setSpacing(8)

        accent = QFrame()
        accent.setFixedSize(3, 14)
        accent.setStyleSheet(
            f"background: {GREEN}; border-radius: 1px; border: none;"
        )
        hr.addWidget(accent)

        lbl_header = QLabel("AI CATEGORIES")
        lbl_header.setObjectName("section_label")
        hr.addWidget(lbl_header)
        hr.addStretch()
        outer.addWidget(header_row)

        # ── Wrapping chip box ────────────────────────────────────────────
        self._box = QFrame()
        self._box.setObjectName("tag_box")
        self._box.setMinimumHeight(52)
        self._box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        outer.addWidget(self._box)

        self._flow = FlowLayout(self._box, h_spacing=6, v_spacing=5)
        self._flow.setContentsMargins(8, 8, 8, 8)

        # ── Persistent entry — created once, never destroyed ─────────────
        self._entry = QLineEdit()
        self._entry.setObjectName("tag_entry")   # global QSS handles style
        self._entry.setPlaceholderText("Add place…")
        self._entry.returnPressed.connect(self._add)

        # ── Add button + entry row below the box ─────────────────────────
        add_row = QWidget()
        ar = QHBoxLayout(add_row)
        ar.setContentsMargins(0, 0, 0, 0)
        ar.setSpacing(8)

        self._add_btn = QPushButton("+ Add")
        self._add_btn.setObjectName("add_tag")   # global QSS handles style
        self._add_btn.setCursor(Qt.PointingHandCursor)
        self._add_btn.clicked.connect(self._add)
        ar.addWidget(self._add_btn)

        ar.addWidget(self._entry)

        hint = QLabel("Type a place and press Enter")
        hint.setObjectName("hint")
        ar.addWidget(hint)
        ar.addStretch()
        outer.addWidget(add_row)

        self._render()

    # ── Public API ───────────────────────────────────────────────────────

    @property
    def tags(self) -> list[str]:
        """Return a copy of the current tag list."""
        return list(self._tags)

    # ── Rendering ────────────────────────────────────────────────────────

    def _render(self) -> None:
        """Rebuild the chip layout.

        Only ``TagChip`` instances are destroyed and recreated.
        ``self._entry`` is removed from the layout (not deleted) and
        is kept alive inside ``self`` until re-inserted.
        """
        # 1. Remove entry from flow (without deleting it)
        self._flow.removeWidget(self._entry)
        self._entry.setParent(None)

        # 2. Destroy old chips only
        for chip in self._chips:
            self._flow.removeWidget(chip)
            chip.deleteLater()
        self._chips.clear()

        # 3. Clear leftover layout items
        while self._flow.count():
            self._flow.takeAt(0)

        # 4. Create fresh chips
        for tag in self._tags:
            chip = TagChip(tag)
            chip.removed.connect(self._remove)
            self._flow.addWidget(chip)
            self._chips.append(chip)

        # 5. Re-insert the persistent entry at end of flow
        self._flow.addWidget(self._entry)

        # Force the box to recalculate its height based on flow content
        self._box.updateGeometry()

    # ── Mutations ────────────────────────────────────────────────────────

    def _add(self) -> None:
        """Add a new tag from the entry field."""
        val = self._entry.text().strip()
        if val and val not in self._tags:
            self._tags.append(val)
            self._entry.clear()
            self._render()
        self._entry.setFocus()

    def _remove(self, tag: str) -> None:
        """Remove a tag by name."""
        if tag in self._tags:
            self._tags.remove(tag)
            self._render()
