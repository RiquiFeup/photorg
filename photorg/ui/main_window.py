"""
MainWindow layout and orchestration.
"""
import os
from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFrame, QStackedWidget

from photorg.ui.theme import BG, BORDER
from photorg.ui.top_bar import TopBar
from photorg.ui.status_bar import StatusBar
from photorg.ui.screens.day_screen import DayScreen
from photorg.ui.screens.ai_screen import AIScreen
from photorg.ui.screens.output_screen import OutputScreen
from photorg.ui.workers.day_worker import DayOrganiserWorker


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Photorg")
        self.setMinimumSize(800, 500)
        self.resize(960, 600)
        self.setStatusBar(None)
        
        self._current_source: str | None = None
        self._worker: DayOrganiserWorker | None = None
        
        self._build()

    def _build(self) -> None:
        root = QWidget()
        root.setStyleSheet(f"background-color: {BG};")
        self.setCentralWidget(root)

        v = QVBoxLayout(root)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        self._topbar = TopBar()
        self._topbar.tab_changed.connect(self._switch_tab)
        v.addWidget(self._topbar)

        sep_top = QFrame()
        sep_top.setFixedHeight(1)
        sep_top.setStyleSheet(f"background: {BORDER};")
        v.addWidget(sep_top)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background-color: {BG};")
        v.addWidget(self._stack, 1)

        self._day_screen = DayScreen()
        self._day_screen.folder_selected.connect(self._on_folder_selected)
        self._day_screen.run_requested.connect(self._run_day_organizer)
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

        self._status = StatusBar()
        v.addWidget(self._status)

    def _switch_tab(self, idx: int) -> None:
        self._stack.setCurrentIndex(idx)

    def _on_folder_selected(self, path: str) -> None:
        self._current_source = path
        name = os.path.basename(path)
        self._status.set_message(f"Selected:  {name}")

    def _run_day_organizer(self, title: str, destination: str) -> None:
        if not self._current_source:
            self._status.set_message("Error: Please drop a source folder first.")
            return
        if not title or not destination:
            self._status.set_message("Error: Please provide a title and destination.")
            return

        # Start worker thread
        self._worker = DayOrganiserWorker(Path(self._current_source), Path(destination), title)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        
        self._status.set_message("Starting Day Organizer...")
        self._status.show_progress(True)
        self._worker.start()

    def _on_progress(self, current: int, total: int, msg: str) -> None:
        self._status.set_message(msg)
        self._status.set_progress(current, total)
    
    def _on_finished(self) -> None:
        self._status.set_message("Organisation complete! Check your output folder.")
        self._status.show_progress(False)
    
    def _on_error(self, err: str) -> None:
        self._status.set_message(f"Error: {err}")
        self._status.show_progress(False)
