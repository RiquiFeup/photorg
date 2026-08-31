"""
FlowLayout — wrapping chip / tag layout.

Lays out child items left-to-right, wrapping to new rows when the
available width is exhausted. Equivalent to CSS ``flex-wrap: wrap``.

This replaces the single-row ``QHBoxLayout`` in ``TagInput`` so that
tag chips never overflow or clip off-screen at narrow window widths.
"""
from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout, QLayoutItem, QSizePolicy, QWidget


class FlowLayout(QLayout):
    """Wrapping flow layout for tag chips.

    Parameters
    ----------
    parent:
        Optional parent widget — pass to ``QLayout.__init__``.
    h_spacing:
        Horizontal gap between items in pixels.
    v_spacing:
        Vertical gap between rows in pixels.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        h_spacing: int = 6,
        v_spacing: int = 6,
    ) -> None:
        super().__init__(parent)
        self._items: list[QLayoutItem] = []
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing

    # ── QLayout interface ────────────────────────────────────────────────

    def addItem(self, item: QLayoutItem) -> None:
        self._items.append(item)

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index: int) -> QLayoutItem | None:
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index: int) -> QLayoutItem | None:
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self) -> Qt.Orientation:
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect: QRect) -> None:
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        m = self.contentsMargins()
        size += QSize(m.left() + m.right(), m.top() + m.bottom())
        return size

    # ── Internal layout engine ───────────────────────────────────────────

    def _do_layout(self, rect: QRect, *, test_only: bool) -> int:
        """Place items and return the total height used."""
        m = self.contentsMargins()
        eff = rect.adjusted(m.left(), m.top(), -m.right(), -m.bottom())
        x = eff.x()
        y = eff.y()
        row_height = 0

        for item in self._items:
            w = item.sizeHint().width()
            h = item.sizeHint().height()

            # Wrap to next row if this item doesn't fit
            if row_height > 0 and x + w > eff.right():
                x = eff.x()
                y += row_height + self._v_spacing
                row_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x += w + self._h_spacing
            row_height = max(row_height, h)

        return y + row_height - eff.y() + m.top() + m.bottom()
