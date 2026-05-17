"""
Estilo empresarial premium - Inspirado en Linear/Stripe/Notion
Colores: slate oscuro, acento azul índigo, tipografía limpia
"""

CORPORATE_STYLE = """
/* ===== GLOBAL ===== */
QWidget {
    background-color: #0f1117;
    color: #e1e4e8;
    font-family: 'Segoe UI', -apple-system, 'Helvetica Neue', sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #0f1117;
}

/* ===== LOGIN WINDOW ===== */
#LoginWindow {
    background-color: #0f1117;
}

#LoginTitle {
    color: #ffffff;
    font-size: 24px;
    font-weight: 600;
}

#LoginSubtitle {
    color: #8b949e;
    font-size: 12px;
}

/* ===== INPUT FIELDS ===== */
QLineEdit {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 10px 14px;
    color: #e1e4e8;
    font-size: 13px;
    min-height: 18px;
}

QLineEdit:focus {
    border: 1px solid #58a6ff;
    background-color: #1c2333;
}

QLineEdit:hover:not(:focus) {
    border: 1px solid #484f58;
}

/* ===== BUTTONS ===== */
QPushButton {
    background-color: #238636;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
    min-height: 18px;
}

QPushButton:hover {
    background-color: #2ea043;
}

QPushButton:pressed {
    background-color: #1e7a30;
}

/* ===== DANGER BUTTON ===== */
QPushButton#btnDanger {
    background-color: #da3633;
}

QPushButton#btnDanger:hover {
    background-color: #f85149;
}

/* ===== SECONDARY BUTTON ===== */
QPushButton#btnSecondary {
    background-color: #21262d;
    border: 1px solid #30363d;
    color: #e1e4e8;
}

QPushButton#btnSecondary:hover {
    background-color: #30363d;
}

/* ===== LABELS ===== */
QLabel {
    color: #e1e4e8;
    background: transparent;
}

QLabel#ErrorLabel {
    color: #f85149;
    font-size: 12px;
    background: transparent;
}

QLabel#SuccessLabel {
    color: #3fb950;
    font-size: 12px;
    background: transparent;
}

/* ===== GROUP BOX ===== */
QGroupBox {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    margin-top: 16px;
    padding: 16px;
    padding-top: 28px;
    font-weight: 600;
    color: #58a6ff;
    font-size: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
    color: #58a6ff;
}

/* ===== TABLE ===== */
QTableWidget {
    background-color: #0f1117;
    alternate-background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    gridline-color: #21262d;
    selection-background-color: #1f3a5f;
    selection-color: #ffffff;
}

QTableWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #21262d;
    min-height: 32px;
}

QHeaderView::section {
    background-color: #161b22;
    color: #8b949e;
    padding: 10px 12px;
    border: none;
    border-bottom: 1px solid #30363d;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ===== COMBOBOX ===== */
QComboBox {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e1e4e8;
    font-size: 13px;
    min-height: 16px;
}

QComboBox:focus {
    border: 1px solid #58a6ff;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #8b949e;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #161b22;
    border: 1px solid #30363d;
    selection-background-color: #1f3a5f;
    color: #e1e4e8;
    outline: none;
}

/* ===== SCROLLBARS ===== */
QScrollBar:vertical {
    background: #0f1117;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #30363d;
    min-height: 30px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #484f58;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: #0f1117;
    height: 8px;
}

QScrollBar::handle:horizontal {
    background: #30363d;
    min-width: 30px;
    border-radius: 4px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ===== TAB WIDGET ===== */
QTabWidget::pane {
    border: 1px solid #30363d;
    border-radius: 8px;
    background-color: #0f1117;
}

QTabBar::tab {
    background-color: #161b22;
    color: #8b949e;
    border: 1px solid #30363d;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 2px;
    font-size: 12px;
}

QTabBar::tab:selected {
    background-color: #0f1117;
    color: #e1e4e8;
    border-bottom: 2px solid #58a6ff;
}

QTabBar::tab:hover:!selected {
    background-color: #21262d;
}

/* ===== CHECKBOX ===== */
QCheckBox {
    spacing: 8px;
    color: #e1e4e8;
    font-size: 12px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #484f58;
    border-radius: 3px;
    background: #161b22;
}

QCheckBox::indicator:checked {
    background: #238636;
    border-color: #238636;
}

/* ===== SPINBOX ===== */
QSpinBox, QDoubleSpinBox {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e1e4e8;
    font-size: 13px;
    min-height: 16px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #58a6ff;
}

/* ===== MESSAGE BOX ===== */
QMessageBox {
    background-color: #161b22;
}

QMessageBox QLabel {
    color: #e1e4e8;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* ===== STATUS BAR ===== */
QStatusBar {
    background-color: #161b22;
    color: #8b949e;
    border-top: 1px solid #30363d;
    font-size: 11px;
    padding: 2px 12px;
}

/* ===== PROGRESS BAR ===== */
QProgressBar {
    background: #21262d;
    border: none;
    border-radius: 4px;
    text-align: center;
    color: #e1e4e8;
    font-size: 11px;
    height: 8px;
}

QProgressBar::chunk {
    background: #238636;
    border-radius: 4px;
}

/* ===== ACCENT LINE ===== */
#AccentLine {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #238636, stop:0.3 #58a6ff, stop:0.7 #8b949e, stop:1 #238636);
    border-radius: 1px;
}
"""


def apply_style(app):
    """Aplica el tema corporativo a la aplicación."""
    app.setStyleSheet(CORPORATE_STYLE)
    return app
