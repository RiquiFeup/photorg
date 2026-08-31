"""
Tests for the frameless window chrome feature.

Covers:
- _apply_dark_title_bar: Win32 DWM API call, platform guard, silent error handling
- TopBar: drag handle, window controls, tab switching, active-state painting
- MainWindow: FramelessWindowHint, minimum size, layout integrity
"""
from __future__ import annotations

import sys
from unittest.mock import patch, MagicMock, call
import pytest


# ── _apply_dark_title_bar ───────────────────────────────────────────────────


class TestApplyDarkTitleBar:
    """Unit tests for the Win32 DWM dark title bar helper."""

    def test_function_is_importable(self) -> None:
        """_apply_dark_title_bar must be importable from photorg.main."""
        from photorg.main import _apply_dark_title_bar
        assert callable(_apply_dark_title_bar)

    def test_noop_on_non_windows(self) -> None:
        """On non-Windows platforms the function must return without doing anything."""
        from photorg.main import _apply_dark_title_bar

        mock_windll = MagicMock()
        with patch("photorg.main.sys") as mock_sys, \
             patch("ctypes.windll", mock_windll, create=True):
            mock_sys.platform = "linux"
            _apply_dark_title_bar(12345)
            # DwmSetWindowAttribute must NOT be called
            mock_windll.dwmapi.DwmSetWindowAttribute.assert_not_called()

    def test_noop_on_darwin(self) -> None:
        """On macOS the function must return without doing anything."""
        from photorg.main import _apply_dark_title_bar

        mock_windll = MagicMock()
        with patch("photorg.main.sys") as mock_sys, \
             patch("ctypes.windll", mock_windll, create=True):
            mock_sys.platform = "darwin"
            _apply_dark_title_bar(99)
            mock_windll.dwmapi.DwmSetWindowAttribute.assert_not_called()

    def test_silent_on_exception(self) -> None:
        """Any exception inside the function must be swallowed silently."""
        from photorg.main import _apply_dark_title_bar

        with patch("photorg.main.sys") as mock_sys:
            mock_sys.platform = "win32"
            # Passing hwnd=0 on Windows would be an invalid handle, but the
            # function wraps everything in try/except — it must not raise.
            try:
                _apply_dark_title_bar(0)
            except Exception as exc:  # noqa: BLE001
                pytest.fail(f"_apply_dark_title_bar raised unexpectedly: {exc}")

    def test_silent_on_import_error(self) -> None:
        """If ctypes is somehow unavailable the function must not propagate."""
        from photorg.main import _apply_dark_title_bar
        import builtins
        original_import = builtins.__import__

        def _blocked_import(name, *args, **kwargs):
            if name == "ctypes":
                raise ImportError("ctypes not available")
            return original_import(name, *args, **kwargs)

        with patch("photorg.main.sys") as mock_sys, \
             patch("builtins.__import__", side_effect=_blocked_import):
            mock_sys.platform = "win32"
            try:
                _apply_dark_title_bar(12345)
            except Exception as exc:  # noqa: BLE001
                pytest.fail(f"_apply_dark_title_bar raised on ImportError: {exc}")

    def test_dwm_attribute_id_is_20(self) -> None:
        """DWMWA_USE_IMMERSIVE_DARK_MODE must be 20 (Windows 10 build 18985+)."""
        # This verifies the constant used in the implementation is correct.
        # We inspect the source rather than mocking the full ctypes call,
        # since ctypes.windll is platform-specific.
        import inspect
        from photorg import main
        source = inspect.getsource(main._apply_dark_title_bar)
        assert "20" in source, (
            "DWMWA_USE_IMMERSIVE_DARK_MODE should be 20 in _apply_dark_title_bar"
        )

    def test_function_accepts_int_hwnd(self) -> None:
        """The function signature must accept an integer hwnd parameter."""
        import inspect
        from photorg.main import _apply_dark_title_bar
        sig = inspect.signature(_apply_dark_title_bar)
        params = list(sig.parameters)
        assert len(params) == 1 and params[0] == "hwnd"


# ── TopBar ──────────────────────────────────────────────────────────────────


class TestTopBarWindowControls:
    """TopBar must expose minimise, maximise, and close buttons."""

    def test_has_minimise_button(self, qtbot) -> None:
        from photorg.ui.top_bar import TopBar
        bar = TopBar()
        qtbot.addWidget(bar)
        assert hasattr(bar, "_min_btn"), "TopBar missing _min_btn"

    def test_has_maximise_button(self, qtbot) -> None:
        from photorg.ui.top_bar import TopBar
        bar = TopBar()
        qtbot.addWidget(bar)
        assert hasattr(bar, "_max_btn"), "TopBar missing _max_btn"

    def test_has_close_button(self, qtbot) -> None:
        from photorg.ui.top_bar import TopBar
        bar = TopBar()
        qtbot.addWidget(bar)
        assert hasattr(bar, "_close_btn"), "TopBar missing _close_btn"

    def test_height_is_56px(self, qtbot) -> None:
        from photorg.ui.top_bar import TopBar
        bar = TopBar()
        qtbot.addWidget(bar)
        assert bar.height() == 56

    def test_has_three_tab_buttons(self, qtbot) -> None:
        from photorg.ui.top_bar import TopBar
        bar = TopBar()
        qtbot.addWidget(bar)
        assert len(bar._btns) == 3


class TestTopBarTabSwitching:
    """TopBar tab navigation must work correctly."""

    def test_default_active_tab_is_zero(self, qtbot) -> None:
        from photorg.ui.top_bar import TopBar
        bar = TopBar()
        qtbot.addWidget(bar)
        assert bar._active == 0

    def test_switch_to_changes_active_tab(self, qtbot) -> None:
        from photorg.ui.top_bar import TopBar
        bar = TopBar()
        qtbot.addWidget(bar)
        bar.switch_to(1)
        assert bar._active == 1

    def test_switch_to_second_tab(self, qtbot) -> None:
        from photorg.ui.top_bar import TopBar
        bar = TopBar()
        qtbot.addWidget(bar)
        bar.switch_to(2)
        assert bar._active == 2

    def test_switch_to_same_tab_is_noop(self, qtbot) -> None:
        from photorg.ui.top_bar import TopBar
        bar = TopBar()
        qtbot.addWidget(bar)
        # Already on 0; switching to 0 should leave _active at 0
        bar.switch_to(0)
        assert bar._active == 0

    def test_switch_to_emits_tab_changed(self, qtbot) -> None:
        from photorg.ui.top_bar import TopBar
        bar = TopBar()
        qtbot.addWidget(bar)
        with qtbot.waitSignal(bar.tab_changed, timeout=500) as blocker:
            bar.switch_to(1)
        assert blocker.args == [1]

    def test_switch_back_emits_tab_changed(self, qtbot) -> None:
        from photorg.ui.top_bar import TopBar
        bar = TopBar()
        qtbot.addWidget(bar)
        bar.switch_to(2)
        with qtbot.waitSignal(bar.tab_changed, timeout=500) as blocker:
            bar.switch_to(0)
        assert blocker.args == [0]

    def test_switch_to_is_public_api(self) -> None:
        """switch_to must be a public method (no leading underscore)."""
        from photorg.ui.top_bar import TopBar
        assert hasattr(TopBar, "switch_to")
        assert not TopBar.switch_to.__name__.startswith("_")

    def test_main_window_does_not_access_private_switch(self) -> None:
        """MainWindow must use switch_to(), not _topbar._switch()."""
        import inspect
        from photorg.ui import main_window
        source = inspect.getsource(main_window)
        assert "_topbar._switch" not in source, (
            "MainWindow calls private _topbar._switch() — use switch_to() instead"
        )


class TestTopBarDragHandle:
    """TopBar source must implement frameless window drag."""

    def test_source_has_mousepressevent(self) -> None:
        import inspect
        from photorg.ui import top_bar
        source = inspect.getsource(top_bar)
        assert "mousePressEvent" in source

    def test_source_has_mousemoveevent(self) -> None:
        import inspect
        from photorg.ui import top_bar
        source = inspect.getsource(top_bar)
        assert "mouseMoveEvent" in source

    def test_source_has_double_click_maximise(self) -> None:
        import inspect
        from photorg.ui import top_bar
        source = inspect.getsource(top_bar)
        assert "mouseDoubleClickEvent" in source

    def test_drag_pos_initialised_to_none(self, qtbot) -> None:
        from photorg.ui.top_bar import TopBar
        bar = TopBar()
        qtbot.addWidget(bar)
        assert bar._drag_pos is None


# ── MainWindow ──────────────────────────────────────────────────────────────


class TestMainWindowFrameless:
    """MainWindow must be frameless and correctly sized."""

    def test_is_frameless(self, qtbot) -> None:
        from photorg.ui.main_window import MainWindow
        from PySide6.QtCore import Qt
        window = MainWindow()
        qtbot.addWidget(window)
        assert bool(window.windowFlags() & Qt.FramelessWindowHint), (
            "MainWindow must have Qt.FramelessWindowHint set"
        )

    def test_minimum_width_is_at_least_800(self, qtbot) -> None:
        from photorg.ui.main_window import MainWindow
        window = MainWindow()
        qtbot.addWidget(window)
        assert window.minimumWidth() >= 800

    def test_minimum_height_is_at_least_500(self, qtbot) -> None:
        from photorg.ui.main_window import MainWindow
        window = MainWindow()
        qtbot.addWidget(window)
        assert window.minimumHeight() >= 500

    def test_no_native_status_bar(self, qtbot) -> None:
        from photorg.ui.main_window import MainWindow
        window = MainWindow()
        qtbot.addWidget(window)
        # setStatusBar(None) was called — Qt returns a new empty one on access,
        # but we verify the call was made by checking source
        import inspect
        from photorg.ui import main_window
        source = inspect.getsource(main_window)
        assert "setStatusBar(None)" in source

    def test_window_title(self, qtbot) -> None:
        from photorg.ui.main_window import MainWindow
        window = MainWindow()
        qtbot.addWidget(window)
        assert window.windowTitle() == "Photorg"
