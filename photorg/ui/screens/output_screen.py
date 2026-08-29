"""
Output screen.

Shows a scrollable file-tree preview of a real folder structure.
Supports both drop-to-preview and programmatic refresh after an
organise operation completes.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel,
    QTreeWidget, QTreeWidgetItem, QAbstractItemView,
)
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QColor, QFont, QDesktopServices

from photorg.ui.theme import TEXT, MUTED, DIMMER, GREEN, SURFACE, BORDER
from photorg.ui.widgets.drop_zone import DropZone

MEDIA_PREVIEW_EXTENSIONS = frozenset({
    ".jpg", ".jpeg", ".png", ".heic", ".heif",
    ".webp", ".bmp", ".gif", ".tiff", ".tif",
    ".mov", ".mp4", ".m4v", ".avi", ".mkv",
})


class _FileTreePanel(QFrame):
    """Scrollable tree view for previewing output folders."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("panel")
        self._root_path: Path | None = None
        self._build()

    def _build(self) -> None:
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        # Header
        hdr = QWidget()
        hdr.setFixedHeight(46)
        h = QHBoxLayout(hdr)
        h.setContentsMargins(16, 0, 16, 0)

        t = QLabel("Output Preview")
        t.setStyleSheet(f"color: {TEXT}; font-size: 12px; font-weight: 700;")
        h.addWidget(t)
        h.addStretch()

        self._badge = QLabel("  drop a folder  ")
        self._badge.setStyleSheet(
            f"color: {MUTED}; font-size: 9px; background: {SURFACE};"
            f" border-radius: 4px; padding: 2px;"
        )
        h.addWidget(self._badge)

        # Use QPushButton instead of QLabel + monkeypatch for proper click handling
        from PySide6.QtWidgets import QPushButton
        self._open_btn = QPushButton("📂 open")
        self._open_btn.setObjectName("browse")
        self._open_btn.setCursor(Qt.PointingHandCursor)
        self._open_btn.setVisible(False)
        self._open_btn.clicked.connect(self._open_in_explorer)
        h.addWidget(self._open_btn)

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

        # Placeholder
        self._placeholder = QLabel("Drop or browse an output folder to preview")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setStyleSheet(
            f"color: {DIMMER}; font-size: 11px; padding: 40px;"
        )
        self._placeholder.setWordWrap(True)
        v.addWidget(self._placeholder)

    def load_from_path(self, root: Path) -> None:
        """Scan a real directory and populate the tree."""
        self._tree.clear()
        if not root.exists() or not root.is_dir():
            self._placeholder.setVisible(True)
            self._tree.setVisible(False)
            self._open_btn.setVisible(False)
            self._badge.setText("  folder not found  ")
            return

        self._root_path = root
        self._placeholder.setVisible(False)
        self._tree.setVisible(True)
        self._open_btn.setVisible(True)
        self._badge.setText(f"  {root.name}  ")

        self._fill_from_disk(root, self._tree.invisibleRootItem(), depth=0)
        self._tree.expandAll()

    def _fill_from_disk(
        self, path: Path, parent: QTreeWidgetItem, depth: int,
    ) -> None:
        """Recursively populate tree items from the filesystem."""
        try:
            entries = sorted(
                path.iterdir(),
                key=lambda p: (p.is_file(), p.name.lower()),
            )
        except PermissionError:
            return

        for entry in entries:
            if entry.name.startswith("."):
                continue

            is_media = entry.is_file() and entry.suffix.lower() in MEDIA_PREVIEW_EXTENSIONS
            is_subfolder = entry.is_dir()

            if is_media:
                label = f"  🖼  {entry.name}"
                color = MUTED
                bold = False
            elif is_subfolder and depth >= 1:
                label = f"  📂  {entry.name}"
                color = GREEN
                bold = False
            else:
                label = f"  📁  {entry.name}"
                color = TEXT
                bold = (depth == 0)

            item = QTreeWidgetItem(parent, [label])
            item.setForeground(0, QColor(color))
            if bold:
                item.setFont(0, QFont("Segoe UI", 11, QFont.Bold))

            if is_subfolder:
                self._fill_from_disk(entry, item, depth + 1)

    def _open_in_explorer(self) -> None:
        """Open the root folder in the system file manager."""
        if self._root_path and self._root_path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._root_path)))


class OutputScreen(QWidget):
    """Output Preview view."""

    folder_selected = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        h = QHBoxLayout(self)
        h.setContentsMargins(16, 16, 16, 16)
        h.setSpacing(12)

        self.drop_zone = DropZone()
        self.drop_zone.set_labels("Drop output folder", "to preview generated tree")
        self.drop_zone.folder_dropped.connect(self._on_folder_dropped)
        h.addWidget(self.drop_zone, 5)

        self.tree_panel = _FileTreePanel()
        h.addWidget(self.tree_panel, 6)

    def _on_folder_dropped(self, path: str) -> None:
        """Handle folder selection via drop or browse."""
        self.folder_selected.emit(path)
        self.tree_panel.load_from_path(Path(path))

    def refresh(self, path: str) -> None:
        """Refresh the tree view (called after organising)."""
        self.tree_panel.load_from_path(Path(path))
