"""
MainWindow — layout and orchestration.

Wires together all screens, workers, and the status bar.
Handles both Day Organiser and AI Organiser workflows.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Union

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFrame, QStackedWidget

from photorg.ui.theme import BG, BORDER
from photorg.ui.top_bar import TopBar
from photorg.ui.status_bar import StatusBar
from photorg.ui.screens.day_screen import DayScreen
from photorg.ui.screens.ai_screen import AIScreen
from photorg.ui.screens.output_screen import OutputScreen
from photorg.ui.workers.day_worker import DayOrganiserWorker
from photorg.ui.workers.ai_worker import AIOrganiserWorker


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Photorg")
        self.setMinimumSize(800, 500)
        self.resize(960, 600)
        self.setStatusBar(None)

        self._current_source: str | None = None
        self._last_destination: str | None = None
        self._worker: Union[DayOrganiserWorker, AIOrganiserWorker, None] = None

        self._build()

    # ── layout ──────────────────────────────────────────────────────────

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

        # Day Organizer
        self._day_screen = DayScreen()
        self._day_screen.folder_selected.connect(self._on_folder_selected)
        self._day_screen.run_requested.connect(self._run_day_organizer)
        self._day_screen.cancel_requested.connect(self.cancel_operation)
        self._stack.addWidget(self._day_screen)

        # AI Organizer
        self._ai_screen = AIScreen()
        self._ai_screen.folder_selected.connect(self._on_folder_selected)
        self._ai_screen.run_requested.connect(self._run_ai_organizer)
        self._ai_screen.cancel_requested.connect(self.cancel_operation)
        self._stack.addWidget(self._ai_screen)

        # Output Preview
        self._out_screen = OutputScreen()
        self._out_screen.folder_selected.connect(self._on_folder_selected)
        self._stack.addWidget(self._out_screen)

        sep_bot = QFrame()
        sep_bot.setFixedHeight(1)
        sep_bot.setStyleSheet(f"background: {BORDER};")
        v.addWidget(sep_bot)

        self._status = StatusBar()
        v.addWidget(self._status)

    # ── tab switching ───────────────────────────────────────────────────

    def _switch_tab(self, idx: int) -> None:
        self._stack.setCurrentIndex(idx)

    # ── folder selection ────────────────────────────────────────────────

    def _on_folder_selected(self, path: str) -> None:
        self._current_source = path
        name = os.path.basename(path)
        self._status.set_message(f"Selected:  {name}")

    # ── busy guard ──────────────────────────────────────────────────────

    def _is_busy(self) -> bool:
        """Return True if a worker is currently running."""
        return self._worker is not None and self._worker.isRunning()

    # ── Day Organizer ───────────────────────────────────────────────────

    def _run_day_organizer(self, title: str, destination: str, mode: str) -> None:
        if self._is_busy():
            self._status.set_message("⚠ An operation is already running.")
            return
        if not self._current_source:
            self._status.set_message("Error: Please drop a source folder first.")
            return
        if not title or not destination:
            self._status.set_message("Error: Please provide a title and destination.")
            return

        self._last_destination = str(Path(destination) / title.strip())
        self._day_screen.set_running(True)

        self._worker = DayOrganiserWorker(
            Path(self._current_source), Path(destination), title,
            mode=mode,
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)

        self._status.set_message(f"Starting Day Organizer ({mode} mode)…")
        self._status.show_progress(True)
        self._worker.start()

    # ── AI Organizer ────────────────────────────────────────────────────

    def _run_ai_organizer(self, title: str, places: list, destination: str, mode: str) -> None:
        if self._is_busy():
            self._status.set_message("⚠ An operation is already running.")
            return
        if not self._current_source:
            self._status.set_message("Error: Please drop a source folder first.")
            return
        if not title or not destination:
            self._status.set_message("Error: Please provide a title and destination.")
            return
        if not places:
            self._status.set_message("Error: Add at least one place tag.")
            return

        self._last_destination = str(Path(destination) / title.strip())
        self._ai_screen.set_running(True)

        self._worker = AIOrganiserWorker(
            Path(self._current_source), Path(destination), title, places,
            mode=mode,
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)

        self._status.set_message("Starting AI Organizer… (loading model)")
        self._status.show_progress(True)
        self._worker.start()

    # ── cancel ──────────────────────────────────────────────────────────

    def cancel_operation(self) -> None:
        """Cancel the currently running operation."""
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._status.set_message("Cancelling…")

    # ── worker callbacks ────────────────────────────────────────────────

    def _on_progress(self, current: int, total: int, msg: str) -> None:
        self._status.set_message(msg)
        self._status.set_progress(current, total)

    def _on_finished(self, total: int) -> None:
        self._status.set_message(f"✓ Done — {total} photos organised!")
        self._status.show_progress(False)
        self._day_screen.set_running(False)
        self._ai_screen.set_running(False)

        # Auto-switch to Output tab and refresh preview
        if self._last_destination:
            self._out_screen.refresh(self._last_destination)
            self._topbar.switch_to(2)
            self._stack.setCurrentIndex(2)

    def _on_error(self, err: str) -> None:
        self._status.set_message(f"Error: {err}")
        self._status.show_progress(False)
        self._day_screen.set_running(False)
        self._ai_screen.set_running(False)

    # ── cleanup ─────────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        """Terminate any running worker before closing."""
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait(3000)
        event.accept()
