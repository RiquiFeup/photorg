"""
Photorg application entry point.
"""
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

from photorg.ui.theme import BG, TEXT, GREEN, MUTED, INPUT_BG, PANEL, build_qss
from photorg.ui.main_window import MainWindow


def _build_dark_palette() -> QPalette:
    """Create a dark palette to complement QSS and prevent white OS elements."""
    p = QPalette()
    p.setColor(QPalette.Window, QColor(BG))
    p.setColor(QPalette.WindowText, QColor(TEXT))
    p.setColor(QPalette.Base, QColor(INPUT_BG))
    p.setColor(QPalette.AlternateBase, QColor(PANEL))
    p.setColor(QPalette.Text, QColor(TEXT))
    p.setColor(QPalette.Button, QColor(PANEL))
    p.setColor(QPalette.ButtonText, QColor(TEXT))
    p.setColor(QPalette.Highlight, QColor(GREEN))
    p.setColor(QPalette.HighlightedText, QColor("#000000"))
    p.setColor(QPalette.PlaceholderText, QColor(MUTED))
    return p


def _apply_dark_title_bar(hwnd: int) -> None:
    """Enable dark title bar on Windows via DWM API.

    Uses ``DwmSetWindowAttribute`` (attribute 20 = DWMWA_USE_IMMERSIVE_DARK_MODE)
    introduced in Windows 10 build 18985.  Gracefully no-ops on other platforms
    or older Windows versions — the call is cosmetic only.
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        value = ctypes.c_int(1)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(value),
            ctypes.sizeof(value),
        )
    except Exception:
        pass  # silently ignore — cosmetic only


def main() -> None:
    """Launch the Photorg desktop application."""
    app = QApplication(sys.argv)
    from photorg import __version__
    app.setApplicationName("Photorg")
    app.setApplicationVersion(__version__)
    app.setStyle("Fusion")
    app.setPalette(_build_dark_palette())
    app.setStyleSheet(build_qss())

    window = MainWindow()
    window.show()
    _apply_dark_title_bar(int(window.winId()))
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

