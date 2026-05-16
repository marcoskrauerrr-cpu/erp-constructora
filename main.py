#!/usr/bin/env python3
"""
ERP Constructora — Sistema de Gestión para Empresas Constructoras
Punto de entrada principal.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QPushButton, QLabel, QDialog, QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "erp_constructora.db"

from src.database.repository import Database

from src.gui.tabs.obras_tab import ObrasTab
from src.gui.tabs.clientes_tab import ClientesTab
from src.gui.tabs.catalogo_tab import CatalogoTab
from src.gui.tabs.presupuesto_tab import PresupuestoTab


# ── Tema oscuro Catppuccin Mocha ─────────────────────────────────────────
DARK_STYLE = """
QMainWindow { background-color: #181825; }
QWidget { background-color: #1e1e2e; color: #cdd6f4; }
QTabWidget::pane {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 6px;
}
QTabBar::tab {
    background-color: #313244;
    color: #a6adc8;
    padding: 10px 24px;
    margin: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-size: 14px;
}
QTabBar::tab:selected {
    background-color: #45475a;
    color: #cdd6f4;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background-color: #45475a;
}
QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton:hover { background-color: #b4d0fb; }
QPushButton:pressed { background-color: #74c7ec; }
QMessageBox {
    background-color: #1e1e2e;
    color: #cdd6f4;
}
QMessageBox QLabel { color: #cdd6f4; }
QMessageBox QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    min-width: 80px;
}
"""


# ── Login Dialog ─────────────────────────────────────────────────────────
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ERP Constructora — Ingreso")
        self.setFixedSize(360, 220)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e2e; }
            QLabel  { color: #cdd6f4; }
            QPushButton {
                background-color: #89b4fa; color: #1e1e2e;
                border: none; border-radius: 8px;
                padding: 10px 30px; font-size: 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #b4d0fb; }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("🏗️ ERP Constructora")
        title.setAlignment(Qt.AlignCenter)
        tf = QFont()
        tf.setPointSize(18)
        tf.setBold(True)
        title.setFont(tf)

        subtitle = QLabel("Sistema de Gestión para Constructoras")
        subtitle.setAlignment(Qt.AlignCenter)
        sf = QFont()
        sf.setPointSize(11)
        subtitle.setFont(sf)

        self.btn_ingresar = QPushButton("Ingresar")
        self.btn_ingresar.clicked.connect(self.accept)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        layout.addWidget(self.btn_ingresar, 0, Qt.AlignCenter)
        layout.addStretch()


# ── Main Dashboard ───────────────────────────────────────────────────────
class MainDashboard(QMainWindow):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.setWindowTitle("ERP Constructora — Dashboard")
        self.resize(1200, 780)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.tabs = QTabWidget()
        self.tabs.addTab(ObrasTab(db), "📋 Obras")
        self.tabs.addTab(ClientesTab(db), "👥 Clientes")
        self.tabs.addTab(CatalogoTab(db), "📦 Catálogo")
        self.tabs.addTab(PresupuestoTab(db), "💰 Presupuesto")

        layout.addWidget(self.tabs)


# ── Entry Point ──────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ERP Constructora")
    app.setStyleSheet(DARK_STYLE)

    # Inicializar base de datos
    db = Database(DB_PATH)
    db.connect()

    # Login
    login = LoginDialog()
    if login.exec() != QDialog.Accepted:
        sys.exit(0)

    # Dashboard
    dashboard = MainDashboard(db)
    dashboard.show()

    exit_code = app.exec()
    db.close()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
