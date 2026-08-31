"""
BrowseRow factory.

Creates a standard labelled input row with a '...' browse button.
Returns the containing widget (to add to layout) and the QLineEdit
(to read/write the selected path).

Styling is handled entirely by the global QSS in theme.py via
objectName selectors — no inline setStyleSheet() calls here.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog,
)


def make_browse_row(label_text: str, placeholder: str) -> tuple[QWidget, QLineEdit]:
    """Return (container_widget, entry_widget) for a labelled path-picker row."""
    container = QWidget()
    v = QVBoxLayout(container)
    v.setContentsMargins(0, 0, 0, 0)
    v.setSpacing(4)

    lbl = QLabel(label_text)
    lbl.setObjectName("section_label")   # styled by global QSS
    v.addWidget(lbl)

    row = QWidget()
    h = QHBoxLayout(row)
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(8)

    entry = QLineEdit()
    entry.setPlaceholderText(placeholder)
    h.addWidget(entry, 1)

    btn = QPushButton("…")
    btn.setObjectName("browse")
    btn.setFixedWidth(44)
    btn.clicked.connect(lambda: _pick_folder(entry))
    h.addWidget(btn)

    v.addWidget(row)
    return container, entry


def _pick_folder(entry: QLineEdit) -> None:
    path = QFileDialog.getExistingDirectory(None, "Select Destination Folder")
    if path:
        entry.setText(path)
