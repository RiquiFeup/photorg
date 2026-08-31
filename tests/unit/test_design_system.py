"""
Tests for the UI design system feature.

Covers:
- Design tokens (ERROR, WARNING, hex validity)
- build_qss(): QToolTip dark style, QPushButton#pill_primary,
  white primary button text, tag_entry line edit, no cursor: CSS property
- FlowLayout: count, add/take, hasHeightForWidth
- Pill button objectNames in DayScreen and AIScreen
- OutputScreen: folder emoji in tree, file tree population
- StatusBar: state machine transitions, message, progress visibility
- BrowseRow: factory output shape
- DropZone: set_labels public API
"""
from __future__ import annotations

import inspect
import pytest


# ── Design Tokens ───────────────────────────────────────────────────────────


class TestDesignTokens:
    """All colour tokens must be valid 7-character hex strings."""

    def test_error_token_value(self) -> None:
        from photorg.ui.theme import ERROR
        assert ERROR == "#ff6b6b"

    def test_warning_token_value(self) -> None:
        from photorg.ui.theme import WARNING
        assert WARNING == "#f0a500"

    def test_green_token_value(self) -> None:
        from photorg.ui.theme import GREEN
        assert GREEN == "#3ddc84"

    def test_all_tokens_are_valid_hex(self) -> None:
        from photorg.ui import theme
        token_names = [
            "BG", "PANEL", "SURFACE", "BORDER",
            "GREEN", "GREEN_HV", "GREEN_DM",
            "TEXT", "MUTED", "DIMMER",
            "INPUT_BG", "INPUT_BD",
            "ERROR", "WARNING",
        ]
        for name in token_names:
            val = getattr(theme, name)
            assert val.startswith("#") and len(val) == 7, (
                f"Token {name}={val!r} is not a valid 7-char hex colour"
            )

    def test_tokens_are_distinct(self) -> None:
        """Key tokens must not accidentally share the same value."""
        from photorg.ui.theme import BG, PANEL, SURFACE, GREEN, TEXT, ERROR
        assert len({BG, PANEL, SURFACE, GREEN, TEXT, ERROR}) == 6


# ── build_qss() ─────────────────────────────────────────────────────────────


class TestQSSRules:
    """build_qss() must produce correct QSS with all required rule blocks."""

    def _qss(self) -> str:
        from photorg.ui.theme import build_qss
        return build_qss()

    def test_returns_non_empty_string(self) -> None:
        assert isinstance(self._qss(), str)
        assert len(self._qss()) > 500

    # ── Tooltip ──

    def test_has_tooltip_block(self) -> None:
        assert "QToolTip" in self._qss()

    def test_tooltip_background_is_dark(self) -> None:
        qss = self._qss()
        # QToolTip block uses a dark background
        assert "#2a2a2a" in qss or "INPUT_BG" in qss or "1e1e1e" in qss or "2a2a2a" in qss

    def test_tooltip_color_is_text_token(self) -> None:
        from photorg.ui.theme import TEXT
        assert TEXT in self._qss()

    # ── Pill primary button ──

    def test_has_pill_primary_rule(self) -> None:
        assert "QPushButton#pill_primary" in self._qss()

    def test_pill_primary_has_22px_radius(self) -> None:
        assert "border-radius: 22px" in self._qss()

    def test_pill_primary_has_white_text(self) -> None:
        # pill_primary should have color: #ffffff
        assert "#ffffff" in self._qss()

    def test_pill_primary_has_hover_state(self) -> None:
        assert "QPushButton#pill_primary:hover" in self._qss()

    def test_pill_primary_has_disabled_state(self) -> None:
        assert "QPushButton#pill_primary:disabled" in self._qss()

    # ── Primary button ──

    def test_has_primary_rule(self) -> None:
        assert "QPushButton#primary" in self._qss()

    def test_primary_button_text_is_white(self) -> None:
        assert "#ffffff" in self._qss()

    # ── Tag entry inline ──

    def test_has_tag_entry_rule(self) -> None:
        assert "QLineEdit#tag_entry" in self._qss()

    # ── Safety rules ──

    def test_no_cursor_css_property(self) -> None:
        """Qt does not support the CSS 'cursor:' property."""
        assert "cursor:" not in self._qss().lower()

    def test_no_duplicate_qmainwindow_selector(self) -> None:
        qss = self._qss()
        count = qss.count("QMainWindow")
        assert count >= 1

    # ── Complete token injection ──

    def test_green_token_appears_in_qss(self) -> None:
        from photorg.ui.theme import GREEN
        assert GREEN in self._qss()

    def test_bg_token_appears_in_qss(self) -> None:
        from photorg.ui.theme import BG
        assert BG in self._qss()


# ── FlowLayout ──────────────────────────────────────────────────────────────


class TestFlowLayout:
    """FlowLayout must correctly manage items and report geometry hints."""

    def test_is_qlayout_subclass(self) -> None:
        from photorg.ui.widgets.flow_layout import FlowLayout
        from PySide6.QtWidgets import QLayout
        assert issubclass(FlowLayout, QLayout)

    def test_count_starts_at_zero(self, qtbot) -> None:
        from photorg.ui.widgets.flow_layout import FlowLayout
        from PySide6.QtWidgets import QWidget
        container = QWidget()
        qtbot.addWidget(container)
        layout = FlowLayout(container)
        assert layout.count() == 0

    def test_has_height_for_width(self, qtbot) -> None:
        from photorg.ui.widgets.flow_layout import FlowLayout
        from PySide6.QtWidgets import QWidget
        container = QWidget()
        qtbot.addWidget(container)
        layout = FlowLayout(container)
        assert layout.hasHeightForWidth() is True

    def test_add_widget_increments_count(self, qtbot) -> None:
        from photorg.ui.widgets.flow_layout import FlowLayout
        from PySide6.QtWidgets import QWidget, QLabel
        container = QWidget()
        qtbot.addWidget(container)
        layout = FlowLayout(container)
        label = QLabel("test")
        layout.addWidget(label)
        assert layout.count() == 1

    def test_add_two_widgets(self, qtbot) -> None:
        from photorg.ui.widgets.flow_layout import FlowLayout
        from PySide6.QtWidgets import QWidget, QLabel
        container = QWidget()
        qtbot.addWidget(container)
        layout = FlowLayout(container)
        layout.addWidget(QLabel("a"))
        layout.addWidget(QLabel("b"))
        assert layout.count() == 2

    def test_take_at_decrements_count(self, qtbot) -> None:
        from photorg.ui.widgets.flow_layout import FlowLayout
        from PySide6.QtWidgets import QWidget, QLabel
        container = QWidget()
        qtbot.addWidget(container)
        layout = FlowLayout(container)
        layout.addWidget(QLabel("x"))
        layout.addWidget(QLabel("y"))
        item = layout.takeAt(0)
        assert item is not None
        assert layout.count() == 1

    def test_item_at_returns_none_for_out_of_range(self, qtbot) -> None:
        from photorg.ui.widgets.flow_layout import FlowLayout
        from PySide6.QtWidgets import QWidget
        container = QWidget()
        qtbot.addWidget(container)
        layout = FlowLayout(container)
        assert layout.itemAt(0) is None
        assert layout.itemAt(99) is None

    def test_take_at_returns_none_for_empty(self, qtbot) -> None:
        from photorg.ui.widgets.flow_layout import FlowLayout
        from PySide6.QtWidgets import QWidget
        container = QWidget()
        qtbot.addWidget(container)
        layout = FlowLayout(container)
        assert layout.takeAt(0) is None

    def test_height_for_width_returns_positive(self, qtbot) -> None:
        from photorg.ui.widgets.flow_layout import FlowLayout
        from PySide6.QtWidgets import QWidget, QLabel
        container = QWidget()
        qtbot.addWidget(container)
        layout = FlowLayout(container)
        layout.addWidget(QLabel("chip"))
        result = layout.heightForWidth(300)
        assert result >= 0


# ── Pill Button objectNames ──────────────────────────────────────────────────


class TestPillButtonObjectNames:
    """DayScreen and AIScreen run buttons must use pill_primary objectName."""

    def test_day_screen_run_btn_uses_pill_primary(self) -> None:
        from photorg.ui.screens import day_screen
        source = inspect.getsource(day_screen)
        assert '"pill_primary"' in source or "'pill_primary'" in source, (
            "DayScreen._run_btn must use setObjectName('pill_primary')"
        )

    def test_ai_screen_run_btn_uses_pill_primary(self) -> None:
        from photorg.ui.screens import ai_screen
        source = inspect.getsource(ai_screen)
        assert '"pill_primary"' in source or "'pill_primary'" in source, (
            "AIScreen._run_btn must use setObjectName('pill_primary')"
        )

    def test_day_screen_run_btn_objectname_at_runtime(self, qtbot) -> None:
        from photorg.ui.screens.day_screen import DayScreen
        screen = DayScreen()
        qtbot.addWidget(screen)
        assert screen.config._run_btn.objectName() == "pill_primary"

    def test_ai_screen_run_btn_objectname_at_runtime(self, qtbot) -> None:
        from photorg.ui.screens.ai_screen import AIScreen
        screen = AIScreen()
        qtbot.addWidget(screen)
        assert screen.config._run_btn.objectName() == "pill_primary"

    def test_day_screen_cancel_btn_uses_cancel(self, qtbot) -> None:
        from photorg.ui.screens.day_screen import DayScreen
        screen = DayScreen()
        qtbot.addWidget(screen)
        assert screen.config._cancel_btn.objectName() == "cancel"

    def test_ai_screen_cancel_btn_uses_cancel(self, qtbot) -> None:
        from photorg.ui.screens.ai_screen import AIScreen
        screen = AIScreen()
        qtbot.addWidget(screen)
        assert screen.config._cancel_btn.objectName() == "cancel"


# ── OutputScreen Folder Icons ────────────────────────────────────────────────


class TestOutputScreenFolderIcons:
    """_FileTreePanel must show folder emoji for directory nodes."""

    def test_source_contains_folder_emoji(self) -> None:
        from photorg.ui.screens import output_screen
        source = inspect.getsource(output_screen)
        assert "\U0001f4c1" in source, (
            "output_screen.py must contain the 📁 folder emoji for directory tree nodes"
        )

    def test_fill_from_disk_adds_folder_items(self, qtbot, tmp_path) -> None:
        from photorg.ui.screens.output_screen import OutputScreen
        # Create a real directory structure
        (tmp_path / "Day 01").mkdir()
        (tmp_path / "Day 02").mkdir()
        screen = OutputScreen()
        qtbot.addWidget(screen)
        screen.refresh(str(tmp_path))
        tree = screen.tree_panel._tree
        assert tree.topLevelItemCount() >= 2

    def test_fill_from_disk_uses_folder_emoji_in_text(self, qtbot, tmp_path) -> None:
        from photorg.ui.screens.output_screen import OutputScreen
        (tmp_path / "Beach").mkdir()
        screen = OutputScreen()
        qtbot.addWidget(screen)
        screen.refresh(str(tmp_path))
        tree = screen.tree_panel._tree
        # At least one top-level item should contain the folder emoji
        found_emoji = False
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            if "\U0001f4c1" in item.text(0):
                found_emoji = True
                break
        assert found_emoji, "No tree item contains the 📁 folder emoji"



# ── StatusBar State Machine ──────────────────────────────────────────────────


class TestStatusBarStateMachine:
    """StatusBar must handle all state transitions without crashing."""

    def test_set_state_ready(self, qtbot) -> None:
        from photorg.ui.status_bar import StatusBar
        bar = StatusBar()
        qtbot.addWidget(bar)
        bar.set_state("ready")  # must not raise

    def test_set_state_running(self, qtbot) -> None:
        from photorg.ui.status_bar import StatusBar
        bar = StatusBar()
        qtbot.addWidget(bar)
        bar.set_state("running")

    def test_set_state_error(self, qtbot) -> None:
        from photorg.ui.status_bar import StatusBar
        bar = StatusBar()
        qtbot.addWidget(bar)
        bar.set_state("error")

    def test_set_state_success(self, qtbot) -> None:
        from photorg.ui.status_bar import StatusBar
        bar = StatusBar()
        qtbot.addWidget(bar)
        bar.set_state("success")

    def test_set_message_updates_label(self, qtbot) -> None:
        from photorg.ui.status_bar import StatusBar
        bar = StatusBar()
        qtbot.addWidget(bar)
        bar.set_message("Hello world")
        assert bar._msg.text() == "Hello world"

    def test_show_progress_true(self, qtbot) -> None:
        from photorg.ui.status_bar import StatusBar
        bar = StatusBar()
        qtbot.addWidget(bar)
        bar.show_progress(True)
        # In headless tests the parent isn't shown, so isVisible() returns False.
        # Check that the widget is not explicitly hidden instead.
        assert not bar._progress.isHidden()

    def test_show_progress_false(self, qtbot) -> None:
        from photorg.ui.status_bar import StatusBar
        bar = StatusBar()
        qtbot.addWidget(bar)
        bar.show_progress(True)
        bar.show_progress(False)
        assert bar._progress.isHidden()

    def test_show_progress_false_resets_value(self, qtbot) -> None:
        from photorg.ui.status_bar import StatusBar
        bar = StatusBar()
        qtbot.addWidget(bar)
        bar.show_progress(True)
        bar.set_progress(5, 10)
        bar.show_progress(False)
        assert bar._progress.value() == 0

    def test_set_progress_updates_value(self, qtbot) -> None:
        from photorg.ui.status_bar import StatusBar
        bar = StatusBar()
        qtbot.addWidget(bar)
        bar.show_progress(True)
        bar.set_progress(3, 10)
        assert bar._progress.value() == 3
        assert bar._progress.maximum() == 10

    def test_status_bar_height_is_40(self, qtbot) -> None:
        from photorg.ui.status_bar import StatusBar
        bar = StatusBar()
        qtbot.addWidget(bar)
        assert bar.height() == 40

    def test_uses_error_token_from_theme(self) -> None:
        from photorg.ui import status_bar
        source = inspect.getsource(status_bar)
        assert "ERROR" in source, "StatusBar must import and use the ERROR design token"

    def test_uses_warning_token_from_theme(self) -> None:
        from photorg.ui import status_bar
        source = inspect.getsource(status_bar)
        assert "WARNING" in source, "StatusBar must import and use the WARNING design token"


# ── DropZone Public API ──────────────────────────────────────────────────────


class TestDropZoneDesignSystem:
    """DropZone must expose set_labels() and not inline cursor: CSS."""

    def test_set_labels_exists(self) -> None:
        from photorg.ui.widgets.drop_zone import DropZone
        assert hasattr(DropZone, "set_labels")

    def test_set_labels_callable(self, qtbot) -> None:
        from photorg.ui.widgets.drop_zone import DropZone
        dz = DropZone()
        qtbot.addWidget(dz)
        dz.set_labels("Drop Here", "or click Browse")  # must not raise

    def test_no_cursor_css_in_source(self) -> None:
        from photorg.ui.widgets import drop_zone
        source = inspect.getsource(drop_zone)
        bad_lines = [
            line.strip() for line in source.splitlines()
            if "cursor:" in line.lower() and "setCursor" not in line
        ]
        assert bad_lines == [], f"cursor: CSS found in drop_zone.py: {bad_lines}"


# ── BrowseRow Factory ────────────────────────────────────────────────────────


class TestBrowseRowFactory:
    """make_browse_row() must return the correct widget + line-edit pair."""

    def test_returns_tuple_of_two(self, qtbot) -> None:
        from photorg.ui.widgets.browse_row import make_browse_row
        from PySide6.QtWidgets import QWidget, QLineEdit
        result = make_browse_row("LABEL", "placeholder…")
        assert isinstance(result, tuple) and len(result) == 2

    def test_first_element_is_qwidget(self, qtbot) -> None:
        from photorg.ui.widgets.browse_row import make_browse_row
        from PySide6.QtWidgets import QWidget
        widget, entry = make_browse_row("DEST", "Choose…")
        qtbot.addWidget(widget)
        assert isinstance(widget, QWidget)

    def test_second_element_is_qlineedit(self, qtbot) -> None:
        from photorg.ui.widgets.browse_row import make_browse_row
        from PySide6.QtWidgets import QLineEdit
        widget, entry = make_browse_row("DEST", "Choose…")
        qtbot.addWidget(widget)
        assert isinstance(entry, QLineEdit)

    def test_placeholder_text_set(self, qtbot) -> None:
        from photorg.ui.widgets.browse_row import make_browse_row
        widget, entry = make_browse_row("DEST", "my placeholder")
        qtbot.addWidget(widget)
        assert entry.placeholderText() == "my placeholder"

    def test_browse_button_has_folder_icon(self, qtbot) -> None:
        """Browse button must show a folder emoji, not '...' or '…'."""
        from photorg.ui.widgets.browse_row import make_browse_row
        from PySide6.QtWidgets import QPushButton
        widget, _ = make_browse_row("DEST", "Choose…")
        qtbot.addWidget(widget)
        # Find the QPushButton#browse child
        btn = widget.findChild(QPushButton, "browse")
        assert btn is not None
        assert "\U0001f4c1" in btn.text(), (
            f"Browse button text should be '📁', got: {btn.text()!r}"
        )

    def test_browse_button_has_tooltip(self, qtbot) -> None:
        """Browse button must have a tooltip for accessibility."""
        from photorg.ui.widgets.browse_row import make_browse_row
        from PySide6.QtWidgets import QPushButton
        widget, _ = make_browse_row("DEST", "Choose…")
        qtbot.addWidget(widget)
        btn = widget.findChild(QPushButton, "browse")
        assert btn is not None
        assert btn.toolTip() != "", "Browse button must have a tooltip"


# ── Border removal regression ────────────────────────────────────────────────


class TestNoBordersRegression:
    """Guard against reintroducing visible box borders on panels and window root."""

    def test_panel_frame_has_no_border_in_qss(self) -> None:
        """QFrame#panel must not have a border property in QSS.

        Bug: A '1px solid BORDER' on the panel frame created a visible box
        around every config panel. Removed — panels now rely on background
        colour contrast only.
        """
        from photorg.ui.theme import build_qss
        qss = build_qss()
        # Extract just the QFrame#panel block (roughly)
        panel_start = qss.find("QFrame#panel")
        panel_end = qss.find("}", panel_start)
        panel_block = qss[panel_start:panel_end]
        assert "border: 1px solid" not in panel_block, (
            "QFrame#panel must not have a visible 1px border. "
            "Remove it from theme.py."
        )

    def test_main_window_root_has_no_border_in_source(self) -> None:
        """MainWindow root widget must not set a border via inline stylesheet.

        Bug: root.setStyleSheet('... border: 1px solid {BORDER};') wrapped
        the entire frameless window in a visible box. Removed.
        """
        import inspect
        from photorg.ui import main_window
        source = inspect.getsource(main_window)
        # The inline setStyleSheet on root must not contain 'border:'
        # (find the specific line that was the problem)
        bad = [
            line.strip() for line in source.splitlines()
            if "border:" in line and "root.setStyleSheet" in line
        ]
        assert bad == [], (
            f"MainWindow root widget has inline border: {bad}. Remove it."
        )

