"""
Design tokens and global QSS stylesheet.

All colour values are defined once as Python constants (design tokens).
``build_qss()`` injects them into the stylesheet via f-strings,
giving the equivalent of CSS custom properties — one place to change
any colour across the entire application.
"""

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
BG       = "#111111"   # app / window background
PANEL    = "#1a1a1a"   # card / panel surface
SURFACE  = "#222222"   # slightly elevated surface
BORDER   = "#2e2e2e"   # subtle divider / border
GREEN    = "#3ddc84"   # primary accent
GREEN_HV = "#2ec46e"   # accent — hover state
GREEN_DM = "#1a3d2b"   # accent dim  (chips, selections)
TEXT     = "#f0f0f0"   # primary text
MUTED    = "#888888"   # secondary / placeholder text
DIMMER   = "#555555"   # tertiary / disabled text
INPUT_BG = "#1e1e1e"   # input field background
INPUT_BD = "#333333"   # input field border


def build_qss() -> str:
    """
    Return the application-level QSS stylesheet with design tokens injected.

    The stylesheet is structured like a design system:
        tokens → base reset → layout → components
    """
    return f"""
    /* ── Base ──────────────────────────────────────────────────────────── */
    * {{
        font-family: 'Segoe UI', 'SF Pro Text', system-ui, sans-serif;
    }}
    QMainWindow {{
        background-color: {BG};
    }}
    QWidget {{
        background-color: transparent;
        color: {TEXT};
    }}

    /* ── Scrollbars ─────────────────────────────────────────────────────── */
    QScrollBar:vertical {{
        background: {BG};
        width: 5px;
        border-radius: 2px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER};
        border-radius: 2px;
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{ height: 0; border: none; }}
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {{ background: none; }}

    /* ── Form controls ──────────────────────────────────────────────────── */
    QLineEdit {{
        background-color: {INPUT_BG};
        border: 1px solid {INPUT_BD};
        border-radius: 6px;
        color: {TEXT};
        padding: 0 10px;
        min-height: 34px;
        max-height: 34px;
        selection-background-color: {GREEN_DM};
    }}
    QLineEdit:focus {{
        border-color: {GREEN};
    }}

    /* ── Buttons ────────────────────────────────────────────────────────── */
    QPushButton {{
        outline: none;
    }}
    QPushButton#primary {{
        background-color: {GREEN};
        color: #000000;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        font-size: 12px;
        min-height: 38px;
        padding: 0 16px;
    }}
    QPushButton#primary:hover   {{ background-color: {GREEN_HV}; }}
    QPushButton#primary:pressed {{ background-color: #28a85e; }}

    QPushButton#browse {{
        background-color: {SURFACE};
        color: {MUTED};
        border: 1px solid {INPUT_BD};
        border-radius: 6px;
        font-size: 11px;
        min-width: 40px;
        min-height: 34px;
        max-height: 34px;
        padding: 0 10px;
    }}
    QPushButton#browse:hover {{
        background-color: {BORDER};
        color: {TEXT};
    }}

    /* ── Top-bar tab buttons ────────────────────────────────────────────── */
    QPushButton#tab {{
        background-color: transparent;
        color: {MUTED};
        border: none;
        border-radius: 0;
        font-size: 12px;
        min-height: 52px;
        max-height: 52px;
        padding: 0 20px;
        min-width: 130px;
    }}
    QPushButton#tab:hover           {{ background-color: {SURFACE}; color: {TEXT}; }}
    QPushButton#tab[active="true"]  {{ color: {GREEN}; font-weight: 700; }}

    /* ── Panels ─────────────────────────────────────────────────────────── */
    QFrame#panel {{
        background-color: {PANEL};
        border: 1px solid {BORDER};
        border-radius: 10px;
    }}

    /* ── Tree widget ────────────────────────────────────────────────────── */
    QTreeWidget {{
        background-color: transparent;
        border: none;
        color: {TEXT};
        font-size: 11px;
        outline: none;
        show-decoration-selected: 0;
    }}
    QTreeWidget::item           {{ padding: 3px 2px; }}
    QTreeWidget::item:hover     {{ background-color: {SURFACE}; border-radius: 4px; }}
    QTreeWidget::item:selected  {{
        background-color: {GREEN_DM};
        color: {GREEN};
        border-radius: 4px;
    }}
    QTreeWidget::branch         {{ background: transparent; image: none; }}
    QHeaderView::section {{
        background-color: transparent;
        border: none;
        color: {MUTED};
        font-size: 10px;
        padding: 4px 8px;
    }}
    """
