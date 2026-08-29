"""
Regression tests for UI widget bugs.

These tests verify that specific bugs, once fixed, never recur.
Each test is named after the bug it guards against.
"""
from __future__ import annotations

import pytest


# ── TagInput: widget lifecycle crash ─────────────────────────────────────


class TestTagInputNoCrash:
    """Guard against RuntimeError: Internal C++ object already deleted.

    Bug: _render() used to call deleteLater() on self._entry (the
    persistent QLineEdit) then try to re-add it to the layout.
    The Qt event loop would later destroy the C++ side, causing a crash.

    Fix: _render() now only deletes TagChip widgets. self._entry is
    removed from layout and re-added without deletion.
    """

    def test_add_remove_cycle_does_not_crash(self, qtbot) -> None:
        """Add a tag, remove it, add another — no crash."""
        from photorg.ui.widgets.tag_input import TagInput

        widget = TagInput()
        qtbot.addWidget(widget)

        initial_count = len(widget.tags)

        # Add a tag
        widget._entry.setText("NewPlace")
        widget._add()
        assert "NewPlace" in widget.tags
        assert len(widget.tags) == initial_count + 1

        # Remove a tag
        widget._remove("NewPlace")
        assert "NewPlace" not in widget.tags
        assert len(widget.tags) == initial_count

        # Add again — this is where the old code crashed
        widget._entry.setText("AnotherPlace")
        widget._add()
        assert "AnotherPlace" in widget.tags

    def test_remove_all_default_tags(self, qtbot) -> None:
        """Removing every default tag should not crash."""
        from photorg.ui.widgets.tag_input import TagInput

        widget = TagInput()
        qtbot.addWidget(widget)

        for tag in list(widget.tags):
            widget._remove(tag)

        assert widget.tags == []

        # Re-add a tag after all removed
        widget._entry.setText("Recovery")
        widget._add()
        assert widget.tags == ["Recovery"]

    def test_rapid_add_remove_stress(self, qtbot) -> None:
        """Rapid add/remove cycles should not cause any crash."""
        from photorg.ui.widgets.tag_input import TagInput

        widget = TagInput()
        qtbot.addWidget(widget)

        for i in range(20):
            tag = f"Tag{i}"
            widget._entry.setText(tag)
            widget._add()
            widget._remove(tag)

        # Entry should still be functional
        widget._entry.setText("Final")
        widget._add()
        assert "Final" in widget.tags

    def test_entry_widget_is_never_deleted(self, qtbot) -> None:
        """The QLineEdit must remain a valid C++ object after re-renders."""
        from photorg.ui.widgets.tag_input import TagInput
        import shiboken6

        widget = TagInput()
        qtbot.addWidget(widget)

        entry_ref = widget._entry

        widget._entry.setText("X")
        widget._add()
        widget._remove("X")
        widget._render()
        widget._render()

        # The entry must still be a valid C++ object
        assert shiboken6.isValid(entry_ref)

    def test_duplicate_tag_not_added(self, qtbot) -> None:
        """Adding a duplicate tag should be silently ignored."""
        from photorg.ui.widgets.tag_input import TagInput

        widget = TagInput()
        qtbot.addWidget(widget)

        widget._entry.setText("Beach")
        widget._add()  # "Beach" is already in DEFAULT_TAGS

        assert widget.tags.count("Beach") == 1

    def test_whitespace_tag_not_added(self, qtbot) -> None:
        """Whitespace-only input should be silently ignored."""
        from photorg.ui.widgets.tag_input import TagInput

        widget = TagInput()
        qtbot.addWidget(widget)
        initial = len(widget.tags)

        widget._entry.setText("   ")
        widget._add()

        assert len(widget.tags) == initial


# ── QSS: no invalid CSS properties ──────────────────────────────────────


class TestQSSValidity:
    """Guard against 'Unknown property cursor' and parse errors.

    Bug: output_screen.py used CSS 'cursor: pointer;' which Qt
    doesn't support. Qt silently failed and spammed console warnings.

    Fix: Use widget.setCursor(Qt.PointingHandCursor) in Python instead.
    """

    def test_theme_qss_has_no_cursor_property(self) -> None:
        """The global stylesheet must not use the CSS 'cursor' property."""
        from photorg.ui.theme import build_qss

        qss = build_qss()
        assert "cursor:" not in qss.lower(), (
            "QSS contains 'cursor:' — Qt doesn't support this CSS property. "
            "Use widget.setCursor(Qt.PointingHandCursor) instead."
        )

    def test_output_screen_no_cursor_in_stylesheets(self) -> None:
        """OutputScreen must not set 'cursor:' in any stylesheet string."""
        import inspect
        from photorg.ui.screens import output_screen

        source = inspect.getsource(output_screen)
        # Allow 'setCursor' (the correct approach) but disallow 'cursor:'
        lines_with_cursor = [
            line.strip() for line in source.splitlines()
            if "cursor:" in line.lower() and "setCursor" not in line
        ]
        assert lines_with_cursor == [], (
            f"Found invalid CSS 'cursor:' in output_screen.py: {lines_with_cursor}"
        )


# ── DropZone: public API for labels ──────────────────────────────────────


class TestDropZonePublicAPI:
    """Guard against private member access on DropZone.

    Bug: OutputScreen accessed drop_zone._title and drop_zone._sub
    directly, breaking encapsulation.

    Fix: DropZone now exposes set_labels(title, subtitle).
    """

    def test_set_labels_method_exists(self) -> None:
        """DropZone must expose a public set_labels method."""
        from photorg.ui.widgets.drop_zone import DropZone

        assert hasattr(DropZone, "set_labels"), (
            "DropZone missing public set_labels() method"
        )

    def test_output_screen_does_not_access_private_members(self) -> None:
        """OutputScreen must not access _title or _sub on DropZone."""
        import inspect
        from photorg.ui.screens import output_screen

        source = inspect.getsource(output_screen)
        assert "drop_zone._title" not in source, (
            "OutputScreen accesses private drop_zone._title"
        )
        assert "drop_zone._sub" not in source, (
            "OutputScreen accesses private drop_zone._sub"
        )


# ── TopBar: public API for switching ────────────────────────────────────


class TestTopBarPublicAPI:
    """Guard against private method access on TopBar.

    Bug: MainWindow called self._topbar._switch(2) directly.

    Fix: TopBar now exposes switch_to(idx).
    """

    def test_switch_to_method_exists(self) -> None:
        """TopBar must expose a public switch_to method."""
        from photorg.ui.top_bar import TopBar

        assert hasattr(TopBar, "switch_to"), (
            "TopBar missing public switch_to() method"
        )

    def test_main_window_does_not_call_private_switch(self) -> None:
        """MainWindow must not call _topbar._switch()."""
        import inspect
        from photorg.ui import main_window

        source = inspect.getsource(main_window)
        assert "_topbar._switch" not in source, (
            "MainWindow calls private _topbar._switch() — use switch_to() instead"
        )
