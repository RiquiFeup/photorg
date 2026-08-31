"""
Design tokens and global QSS stylesheet.

All colour values are defined once as Python constants (design tokens).
``build_qss()`` injects them into the stylesheet via f-strings,
giving the equivalent of CSS custom properties — one place to change
any colour across the entire application.

Rule: NO widget should call setStyleSheet() inline.
      Every style lives here, targeted via objectName selectors.
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
ERROR    = "#ff6b6b"   # error accent
WARNING  = "#f0a500"   # warning accent


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

    /* ── Tooltips ────────────────────────────────────────────────────────── */
    QToolTip {{
        background-color: #2a2a2a;
        color: {TEXT};
        border: 1px solid #444444;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 11px;
        opacity: 230;
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
        min-height: 36px;
        max-height: 36px;
        selection-background-color: {GREEN_DM};
    }}
    QLineEdit:focus {{
        border-color: {GREEN};
    }}

    /* ── Transparent inline entry (inside tag box) ──────────────────────── */
    QLineEdit#tag_entry {{
        background: transparent;
        border: none;
        color: {TEXT};
        font-size: 11px;
        min-height: 26px;
        max-height: 26px;
        padding: 0 4px;
        min-width: 90px;
        max-width: 120px;
    }}

    /* ── Buttons — base reset ────────────────────────────────────────────── */
    QPushButton {{
        outline: none;
    }}

    /* ── Primary action button (green bg + WHITE text) ──────────────────── */
    QPushButton#primary {{
        background-color: {GREEN};
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        font-size: 13px;
        min-height: 44px;
        padding: 0 24px;
        letter-spacing: 0.3px;
    }}
    QPushButton#primary:hover   {{ background-color: {GREEN_HV}; }}
    QPushButton#primary:pressed {{ background-color: #28a85e; }}
    QPushButton#primary:disabled {{
        background-color: {GREEN_DM};
        color: {DIMMER};
    }}

    /* ── Pill primary action button (fully rounded ends, green pill badge) ── */
    QPushButton#pill_primary {{
        background-color: {GREEN};
        color: #ffffff;
        border: none;
        border-radius: 22px;
        font-weight: 700;
        font-size: 13px;
        min-height: 44px;
        padding: 0 28px;
        letter-spacing: 0.4px;
    }}
    QPushButton#pill_primary:hover   {{ background-color: {GREEN_HV}; }}
    QPushButton#pill_primary:pressed {{ background-color: #28a85e; }}
    QPushButton#pill_primary:disabled {{
        background-color: {GREEN_DM};
        color: {DIMMER};
    }}

    /* ── Cancel button ───────────────────────────────────────────────────── */
    QPushButton#cancel {{
        background: transparent;
        color: {MUTED};
        border: 1px solid {INPUT_BD};
        border-radius: 8px;
        font-size: 11px;
        min-height: 36px;
        padding: 0 16px;
    }}
    QPushButton#cancel:hover   {{ color: {ERROR}; border-color: {ERROR}; }}
    QPushButton#cancel:disabled {{ color: {DIMMER}; border-color: {BORDER}; }}

    /* ── Browse / secondary button ───────────────────────────────────────── */
    QPushButton#browse {{
        background-color: {SURFACE};
        color: {MUTED};
        border: 1px solid {INPUT_BD};
        border-radius: 6px;
        font-size: 11px;
        min-width: 40px;
        min-height: 36px;
        max-height: 36px;
        padding: 0 10px;
    }}
    QPushButton#browse:hover {{
        background-color: {BORDER};
        color: {TEXT};
    }}

    /* ── Tag chip remove button ──────────────────────────────────────────── */
    QPushButton#chip_remove {{
        background: transparent;
        color: {GREEN};
        border: none;
        font-size: 11px;
        font-weight: 700;
        padding: 0;
        min-width: 16px;
        max-width: 16px;
        min-height: 16px;
        max-height: 16px;
    }}
    QPushButton#chip_remove:hover {{ color: #ffffff; }}

    /* ── Add-tag pill button ─────────────────────────────────────────────── */
    QPushButton#add_tag {{
        background: {GREEN_DM};
        color: {GREEN};
        border: 1px solid {GREEN};
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        padding: 0 10px;
        min-height: 24px;
        max-height: 24px;
    }}
    QPushButton#add_tag:hover {{ background: {GREEN}; color: #000000; }}

    /* ── Open-in-explorer / output button ───────────────────────────────── */
    QPushButton#open_folder {{
        background: {SURFACE};
        color: {MUTED};
        border: 1px solid {INPUT_BD};
        border-radius: 5px;
        font-size: 10px;
        padding: 2px 8px;
        min-height: 26px;
        max-height: 26px;
    }}
    QPushButton#open_folder:hover {{ color: {TEXT}; background: {BORDER}; }}

    /* ── Top-bar tab buttons (text labels) ──────────────────────────────── */
    QPushButton#tab {{
        background-color: transparent;
        color: {MUTED};
        border: none;
        border-radius: 6px;
        font-size: 12px;
        min-height: 56px;
        max-height: 56px;
        padding: 0 20px;
        min-width: 100px;
    }}
    QPushButton#tab:hover           {{ background-color: {SURFACE}; color: {TEXT}; }}
    QPushButton#tab[active="true"]  {{
        color: {GREEN};
        background-color: {GREEN_DM};
        font-weight: 700;
    }}

    /* ── QComboBox ───────────────────────────────────────────────────────── */
    QComboBox {{
        background: {INPUT_BG};
        border: 1px solid {INPUT_BD};
        border-radius: 6px;
        color: {TEXT};
        padding: 6px 12px;
        min-height: 36px;
        font-size: 11px;
    }}
    QComboBox:focus {{ border-color: {GREEN}; }}
    QComboBox::drop-down {{ border: none; width: 28px; }}
    QComboBox QAbstractItemView {{
        background: {SURFACE};
        color: {TEXT};
        border: 1px solid {BORDER};
        selection-background-color: {INPUT_BD};
        outline: none;
    }}

    /* ── Progress bar ────────────────────────────────────────────────────── */
    QProgressBar {{
        background: {SURFACE};
        border: none;
        border-radius: 3px;
        min-height: 6px;
        max-height: 6px;
    }}
    QProgressBar::chunk {{
        background: {GREEN};
        border-radius: 3px;
    }}

    /* ── Panels ──────────────────────────────────────────────────────────── */
    QFrame#panel {{
        background-color: {PANEL};
        border: none;
        border-radius: 10px;
    }}

    /* ── Tag chip frame ──────────────────────────────────────────────────── */
    QFrame#tag_chip {{
        background-color: {GREEN_DM};
        border-radius: 12px;
        border: none;
    }}

    /* ── Tag input box ───────────────────────────────────────────────────── */
    QFrame#tag_box {{
        background-color: {INPUT_BG};
        border: 1px solid {INPUT_BD};
        border-radius: 8px;
    }}

    /* ── Horizontal separator ────────────────────────────────────────────── */
    QFrame#h_sep {{
        background: {BORDER};
        max-height: 1px;
        min-height: 1px;
        border: none;
    }}

    /* ── Named labels ────────────────────────────────────────────────────── */
    QLabel#panel_title {{
        color: {TEXT};
        font-size: 14px;
        font-weight: 700;
    }}
    QLabel#section_label {{
        color: {MUTED};
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.8px;
    }}
    QLabel#hint {{
        color: {DIMMER};
        font-size: 9px;
    }}
    QLabel#badge {{
        color: {MUTED};
        font-size: 9px;
        background: {SURFACE};
        border-radius: 4px;
        padding: 2px 6px;
    }}
    QLabel#preview_path {{
        color: {DIMMER};
        font-size: 9px;
    }}

    /* ── Tree widget ─────────────────────────────────────────────────────── */
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
