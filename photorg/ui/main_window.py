"""
MainWindow layout and orchestration.
"""
import os

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFrame, QStackedWidget

from photorg.ui.theme import BG, BORDER
from photorg.ui.top_bar import TopBar
from photorg.ui.status_bar import StatusBar
from photorg.ui.screens.day_screen import DayScreen
from photorg.ui.screens.ai_screen import AIScreen
from photorg.ui.screens.output_screen import OutputScreen


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Photorg")
        self.setMinimumSize(800, 500)
        self.resize(960, 600)
        self.setStatusBar(None)  # Remove native white status bar
        self._build()

    def _build(self) -> None:
        root = QWidget()
        root.setStyleSheet(f"background-color: {BG};")
        self.setCentralWidget(root)

        v = QVBoxLayout(root)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        # Top Bar
        self._topbar = TopBar()
        self._topbar.tab_changed.connect(self._switch_tab)
        v.addWidget(self._topbar)

        sep_top = QFrame()
        sep_top.setFixedHeight(1)
        sep_top.setStyleSheet(f"background: {BORDER};")
        v.addWidget(sep_top)

        # Screens
        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background-color: {BG};")
        v.addWidget(self._stack, 1)

        self._day_screen = DayScreen()
        self._day_screen.folder_selected.connect(self._on_folder_selected)
        self._stack.addWidget(self._day_screen)

        self._ai_screen = AIScreen()
        self._ai_screen.folder_selected.connect(self._on_folder_selected)
        self._stack.addWidget(self._ai_screen)

        self._out_screen = OutputScreen()
        self._out_screen.folder_selected.connect(self._on_folder_selected)
        self._stack.addWidget(self._out_screen)

        sep_bot = QFrame()
        sep_bot.setFixedHeight(1)
        sep_bot.setStyleSheet(f"background: {BORDER};")
        v.addWidget(sep_bot)

        # Status Bar
        self._status = StatusBar()
        v.addWidget(self._status)

    def _switch_tab(self, idx: int) -> None:
        self._stack.setCurrentIndex(idx)

    def _on_folder_selected(self, path: str) -> None:
        name = os.path.basename(path)
        self._status.set_message(f"Selected:  {name}")
