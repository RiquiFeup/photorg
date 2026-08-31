"""
TopBar widget.

App header containing the logo and icon-only tab navigation.
Emits ``tab_changed(int)`` when a different tab is clicked.

In frameless-window mode this widget also serves as the drag handle:
mouse-press anywhere on the bar (not on a button) starts a window-move
operation, and mouse-release ends it.  Three window-control buttons
(minimise · maximise/restore · close) sit on the far right.

UI design
---------
- Tabs are text-label buttons (By Date / By Scene / Output).
- Height 56 px for visual weight.
- Active tab: green tinted background pill + 2 px underline.
- Logo: "📷 Photorg" in green on the left.
- Window controls (–  □  ×) on the right, styled minimally.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QPushButton
from PySide6.QtCore import Signal, Qt, QPoint
from PySide6.QtGui import QPainter, QColor

from photorg.ui.theme import PANEL, BORDER, GREEN, MUTED, TEXT


class TopBar(QWidget):
    """Main application navigation bar (also the drag handle)."""

    tab_changed = Signal(int)

    # Text tab labels
    LABELS   = ["By Date", "By Scene", "Output"]
    TOOLTIPS = ["By Date — organise by day", "By Scene — AI organiser", "Output Preview"]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedHeight(56)
        self.setStyleSheet(f"background-color: {PANEL};")
        self._active: int = 0
        self._btns: list[QPushButton] = []
        self._drag_pos: QPoint | None = None
        self._build()

    def _build(self) -> None:
        h = QHBoxLayout(self)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        logo = QLabel("📷 Photorg")
        logo.setStyleSheet(
            f"color: {GREEN}; font-size: 16px; font-weight: 700; padding: 0 24px 0 20px;"
        )
        h.addWidget(logo)

        vsep = QFrame()
        vsep.setFrameShape(QFrame.VLine)
        vsep.setStyleSheet(f"color: {BORDER};")
        vsep.setFixedWidth(1)
        h.addWidget(vsep)

        for i, (label, tip) in enumerate(zip(self.LABELS, self.TOOLTIPS)):
            btn = QPushButton(label)
            btn.setObjectName("tab")
            btn.setToolTip(tip)
            if i == 0:
                btn.setProperty("active", "true")
            btn.clicked.connect(lambda _, idx=i: self._switch(idx))
            h.addWidget(btn)
            self._btns.append(btn)

        h.addStretch()

        # ── Window control buttons (frameless chrome) ────────────────────
        self._min_btn   = self._make_ctrl_btn("─", "Minimise")
        self._max_btn   = self._make_ctrl_btn("□", "Maximise")
        self._close_btn = self._make_ctrl_btn("✕", "Close")

        h.addWidget(self._min_btn)
        h.addWidget(self._max_btn)
        h.addWidget(self._close_btn)
        h.addSpacing(4)

        self._min_btn.clicked.connect(self._on_minimise)
        self._max_btn.clicked.connect(self._on_maximise)
        self._close_btn.clicked.connect(self._on_close)

    def _make_ctrl_btn(self, symbol: str, tip: str) -> QPushButton:
        """Create a minimal window control button."""
        btn = QPushButton(symbol)
        btn.setFixedSize(40, 40)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tip)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {MUTED};
                border: none;
                font-size: 14px;
                font-weight: 400;
            }}
            QPushButton:hover {{
                background-color: #2e2e2e;
                color: {TEXT};
            }}
        """)
        return btn

    def _on_minimise(self) -> None:
        w = self.window()
        if w:
            w.showMinimized()

    def _on_maximise(self) -> None:
        w = self.window()
        if w:
            if w.isMaximized():
                w.showNormal()
                self._max_btn.setText("□")
                self._max_btn.setToolTip("Maximise")
            else:
                w.showMaximized()
                self._max_btn.setText("❐")
                self._max_btn.setToolTip("Restore")

    def _on_close(self) -> None:
        w = self.window()
        if w:
            w.close()

    # ── Tab switching ────────────────────────────────────────────────────

    def switch_to(self, idx: int) -> None:
        """Public API — switch to tab *idx*."""
        self._switch(idx)

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
        """Draw a 2 px green underline beneath the active tab."""
        super().paintEvent(event)
        if not self._btns:
            return
        p = QPainter(self)
        btn = self._btns[self._active]
        p.fillRect(btn.x(), self.height() - 2, btn.width(), 2, QColor(GREEN))

    # ── Drag-to-move (frameless window) ─────────────────────────────────

    def mousePressEvent(self, event) -> None:
        """Start drag when left-clicking on bar background (not on a button)."""
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        """Move the parent window while dragging."""
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton:
            window = self.window()
            if window:
                delta = event.globalPosition().toPoint() - self._drag_pos
                window.move(window.pos() + delta)
                self._drag_pos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        """End drag."""
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        """Double-click bar to maximise/restore (standard OS behaviour)."""
        if event.button() == Qt.LeftButton:
            self._on_maximise()
        super().mouseDoubleClickEvent(event)

