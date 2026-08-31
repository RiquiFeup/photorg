"""
Output screen.

Shows a scrollable file-tree preview of a real folder structure.
Supports both drop-to-preview and programmatic refresh after an
organise operation completes.

UI improvements
---------------
- Open-folder button uses #open_folder objectName (dedicated QSS rule).
- File count badge uses #badge objectName.
- Double-clicking a file in the tree opens it in the system default app.
- Expand/Collapse All toggle button in the header.
- File count shown in badge after loading.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel,
    QTreeWidget, QTreeWidgetItem, QAbstractItemView, QPushButton,
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
        self._expanded: bool = True
        self._file_count: int = 0
        self._build()

    def _build(self) -> None:
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────
        hdr = QWidget()
        hdr.setFixedHeight(50)
        h = QHBoxLayout(hdr)
        h.setContentsMargins(16, 0, 12, 0)
        h.setSpacing(8)

        t = QLabel("Output Preview")
        t.setObjectName("panel_title")
        h.addWidget(t)
        h.addStretch()

        self._badge = QLabel("  drop a folder  ")
        self._badge.setObjectName("badge")
        h.addWidget(self._badge)

        self._expand_btn = QPushButton("−")
        self._expand_btn.setObjectName("browse")
        self._expand_btn.setFixedSize(26, 26)
        self._expand_btn.setToolTip("Collapse all")
        self._expand_btn.clicked.connect(self._toggle_expand)
        h.addWidget(self._expand_btn)

        self._open_btn = QPushButton("📁 Open")
        self._open_btn.setObjectName("open_folder")
        self._open_btn.setToolTip("Open destination folder in Explorer")
        self._open_btn.setCursor(Qt.PointingHandCursor)
        self._open_btn.setVisible(False)
        self._open_btn.clicked.connect(self._open_in_explorer)
        h.addWidget(self._open_btn)

        v.addWidget(hdr)

        sep = QFrame()
        sep.setObjectName("h_sep")
        sep.setFrameShape(QFrame.HLine)
        v.addWidget(sep)

        # ── Tree ──────────────────────────────────────────────────────────
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setIndentation(20)
        self._tree.setAnimated(True)
        self._tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self._tree.setStyleSheet("QTreeWidget { padding: 8px 6px; }")
        self._tree.itemDoubleClicked.connect(self._on_double_click)
        v.addWidget(self._tree)

        # ── Placeholder ───────────────────────────────────────────────────
        self._placeholder = QLabel("Drop or browse an output folder to preview")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setObjectName("hint")
        self._placeholder.setWordWrap(True)
        self._placeholder.setStyleSheet("font-size: 11px; padding: 40px;")
        v.addWidget(self._placeholder)

    # ── Public API ────────────────────────────────────────────────────────

    def load_from_path(self, root: Path) -> None:
        """Scan a real directory and populate the tree."""
        self._tree.clear()
        self._file_count = 0

        if not root.exists() or not root.is_dir():
            self._placeholder.setVisible(True)
            self._tree.setVisible(False)
            self._open_btn.setVisible(False)
            self._expand_btn.setVisible(False)
            self._badge.setText("  folder not found  ")
            return

        self._root_path = root
        self._placeholder.setVisible(False)
        self._tree.setVisible(True)
        self._open_btn.setVisible(True)
        self._expand_btn.setVisible(True)

        self._fill_from_disk(root, self._tree.invisibleRootItem(), depth=0)
        self._tree.expandAll()
        self._expanded = True
        self._expand_btn.setText("−")
        self._expand_btn.setToolTip("Collapse all")

        count_txt = f"  {self._file_count} file{'s' if self._file_count != 1 else ''}  "
        self._badge.setText(count_txt)

    # ── Internal ──────────────────────────────────────────────────────────

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
                label = f"   {entry.name}"
                color = MUTED
                bold = False
                self._file_count += 1
            elif is_subfolder and depth >= 1:
                label = f"  📁 {entry.name}"
                color = GREEN
                bold = False
            else:
                label = f"  📁 {entry.name}"
                color = TEXT
                bold = (depth == 0)

            item = QTreeWidgetItem(parent, [label])
            item.setForeground(0, QColor(color))
            item.setData(0, Qt.UserRole, str(entry))  # store full path for double-click
            if bold:
                item.setFont(0, QFont("Segoe UI", 11, QFont.Bold))

            if is_subfolder:
                self._fill_from_disk(entry, item, depth + 1)

    def _toggle_expand(self) -> None:
        if self._expanded:
            self._tree.collapseAll()
            self._expand_btn.setText("+")
            self._expand_btn.setToolTip("Expand all")
        else:
            self._tree.expandAll()
            self._expand_btn.setText("−")
            self._expand_btn.setToolTip("Collapse all")
        self._expanded = not self._expanded

    def _on_double_click(self, item: QTreeWidgetItem, _column: int) -> None:
        """Open the file or folder in the system default application."""
        path_str = item.data(0, Qt.UserRole)
        if path_str:
            path = Path(path_str)
            if path.exists():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

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
