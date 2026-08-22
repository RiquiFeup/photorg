"""
DropZone widget.

Accepts a folder via drag-and-drop or click-to-browse.
Emits ``folder_dropped(path: str)`` when a valid folder is chosen.
Visual state transitions: idle -> hover -> loaded.
"""
import os

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QFileDialog
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen

from photorg.ui.theme import PANEL, BORDER, GREEN, TEXT, MUTED, DIMMER


class DropZone(QFrame):
    """Drag-and-drop / click-to-browse area for selecting a source folder."""

    folder_dropped = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("panel")
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self._hover: bool = False
        self._folder: str = ""
        self._build()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(10)

        self._icon = QLabel("\u2193")
        self._icon.setAlignment(Qt.AlignCenter)
        self._icon.setStyleSheet(
            f"color: {DIMMER}; font-size: 32px; font-weight: 700; background: transparent;"
        )
        self._title = QLabel("Drop folder here")
        self._title.setAlignment(Qt.AlignCenter)
        self._title.setStyleSheet(
            f"color: {MUTED}; font-size: 13px; background: transparent;"
        )
        self._sub = QLabel("or click to browse")
        self._sub.setAlignment(Qt.AlignCenter)
        self._sub.setStyleSheet(
            f"color: {DIMMER}; font-size: 10px; background: transparent;"
        )
        lay.addWidget(self._icon)
        lay.addWidget(self._title)
        lay.addWidget(self._sub)

    # ── State ─────────────────────────────────────────────────────────────────

    def _load(self, path: str) -> None:
        self._folder = path
        self._icon.setText("\U0001f4c1")
        self._icon.setStyleSheet(
            f"color: {GREEN}; font-size: 28px; background: transparent;"
        )
        self._title.setText(os.path.basename(path))
        self._title.setStyleSheet(
            f"color: {TEXT}; font-size: 13px; font-weight: 700; background: transparent;"
        )
        self._sub.setText("Click to change")
        self.update()

    @property
    def folder(self) -> str:
        return self._folder

    # ── Paint: dashed rounded border ──────────────────────────────────────────

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor("#1e1e1e" if self._hover else PANEL))
        pen = QPen(QColor(GREEN if self._hover else BORDER))
        pen.setWidth(1)
        pen.setStyle(Qt.DashLine)
        p.setPen(pen)
        p.drawRoundedRect(self.rect().adjusted(14, 14, -14, -14), 8, 8)

    # ── Hover ─────────────────────────────────────────────────────────────────

    def enterEvent(self, e) -> None:
        self._hover = True
        self.update()

    def leaveEvent(self, e) -> None:
        self._hover = False
        self.update()

    # ── Click to browse ───────────────────────────────────────────────────────

    def mousePressEvent(self, e) -> None:
        if e.button() == Qt.LeftButton:
            path = QFileDialog.getExistingDirectory(self, "Select Source Folder")
            if path:
                self._load(path)
                self.folder_dropped.emit(path)

    # ── Drag and drop ─────────────────────────────────────────────────────────

    def dragEnterEvent(self, e) -> None:
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self._hover = True
            self.update()

    def dragLeaveEvent(self, e) -> None:
        self._hover = False
        self.update()

    def dropEvent(self, e) -> None:
        self._hover = False
        urls = e.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self._load(path)
            self.folder_dropped.emit(path)
        self.update()
