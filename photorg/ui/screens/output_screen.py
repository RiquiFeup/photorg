"""
Output screen.

Shows a scrollable file-tree preview of the generated folder structure.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QTreeWidget, QTreeWidgetItem, QAbstractItemView
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QFont

from photorg.ui.theme import TEXT, MUTED, DIMMER, GREEN, SURFACE, BORDER
from photorg.ui.widgets.drop_zone import DropZone


MOCK_TREE = {
    "Italy_Trip": {
        "Day 01 - Rome": {
            "Beach": {},
            "Restaurant": {},
            "IMG_0012.jpg": None,
            "IMG_0015.jpg": None,
        },
        "Day 02 - Rome": {
            "Museum": {},
            "IMG_0034.jpg": None,
        },
        "Day 03 - Amalfi": {
            "Beach": {},
            "Park": {},
        },
    }
}


class _FileTreePanel(QFrame):
    """Scrollable tree view for previewing output folders."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("panel")
        self._build()

    def _build(self) -> None:
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        # Header
        hdr = QWidget()
        hdr.setFixedHeight(46)
        hdr.setStyleSheet("background: transparent;")
        h = QHBoxLayout(hdr)
        h.setContentsMargins(16, 0, 16, 0)

        t = QLabel("Output Preview")
        t.setStyleSheet(f"color: {TEXT}; font-size: 12px; font-weight: 700;")
        h.addWidget(t)
        h.addStretch()

        badge = QLabel("  mock data  ")
        badge.setStyleSheet(
            f"color: {MUTED}; font-size: 9px; background: {SURFACE}; border-radius: 4px; padding: 2px;"
        )
        h.addWidget(badge)
        v.addWidget(hdr)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER};")
        v.addWidget(sep)

        # Tree
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setIndentation(20)
        self._tree.setAnimated(True)
        self._tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self._tree.setStyleSheet("QTreeWidget { padding: 8px 6px; }")
        v.addWidget(self._tree)

        self._fill(MOCK_TREE, self._tree.invisibleRootItem(), depth=0)
        self._tree.expandAll()

    def _fill(self, data: dict, parent: QTreeWidgetItem, depth: int) -> None:
        for name, children in data.items():
            is_image = children is None
            is_place = (not is_image) and (depth == 2)

            if is_image:
                label = f"  \U0001f5bc  {name}"  # Frame icon
                color = MUTED
                bold = False
            elif is_place:
                label = f"  \U0001f4c2  {name}"  # Open folder icon
                color = GREEN
                bold = False
            else:
                label = f"  \U0001f4c1  {name}"  # Closed folder icon
                color = TEXT
                bold = (depth == 0)

            item = QTreeWidgetItem(parent, [label])
            item.setForeground(0, QColor(color))
            if bold:
                item.setFont(0, QFont("Segoe UI", 11, QFont.Bold))

            if children:
                self._fill(children, item, depth + 1)


class OutputScreen(QWidget):
    """Output Preview view."""

    folder_selected = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        h = QHBoxLayout(self)
        h.setContentsMargins(16, 16, 16, 16)
        h.setSpacing(12)

        # Reuse DropZone for selecting the output root folder to scan
        self.drop_zone = DropZone()
        self.drop_zone._title.setText("Drop output folder")
        self.drop_zone._sub.setText("to preview generated tree")
        self.drop_zone.folder_dropped.connect(self.folder_selected.emit)
        h.addWidget(self.drop_zone, 5)

        self.tree = _FileTreePanel()
        h.addWidget(self.tree, 6)
