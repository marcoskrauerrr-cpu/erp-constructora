#!/usr/bin/env python3
"""
ERP Constructora — Sistema de Gestión para Empresas Constructoras
Punto de entrada principal.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QPushButton, QLabel, QDialog, QLineEdit, QFormLayout, QHBoxLayout,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "erp_constructora.db"

from src.database.repository import Database

from src.gui.tabs.obras_tab import ObrasTab
from src.gui.tabs.clientes_tab import ClientesTab
from src.gui.tabs.catalogo_tab import CatalogoTab
from src.gui.tabs.presupuesto_tab import PresupuestoTab


# ── Tema oscuro premium ──────────────────────────────────────────────
DARK_STYLE = """
QMainWindow { background-color: #0f0f1a; }
QWidget {
    background-color: #1a1a2e;
    color: #e0e0f0;
    font-family: 'Segoe UI', 'Arial', sans-serif;
}
QTabWidget::pane {
    background-color: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    padding: 4px;
}
QTabBar::tab {
    background-color: #252545;
    color: #8888aa;
    padding: 12px 28px;
    margin: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-size: 14px;
    font-weight: 500;
}
QTabBar::tab:selected {
    background-color: #3a3a6a;
    color: #ffffff;
    font-weight: bold;
    border-bottom: 2px solid #6c63ff;
}
QTabBar::tab:hover:!selected {
    background-color: #303050;
    color: #ccccdd;
}
QPushButton {
    background-color: #6c63ff;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #7c73ff;
}
QPushButton:pressed {
    background-color: #5a52e0;
}
QPushButton#btn_danger {
    background-color: #e74c3c;
}
QPushButton#btn_danger:hover {
    background-color: #ff5a4a;
}
QTableWidget {
    background-color: #1a1a2e;
    alternate-background-color: #16162a;
    color: #e0e0f0;
    gridline-color: #2a2a4a;
    font-size: 13px;
    border-radius: 6px;
    border: 1px solid #2a2a4a;
}
QHeaderView::section {
    background-color: #252545;
    color: #e0e0f0;
    padding: 10px;
    font-weight: bold;
    border: 1px solid #2a2a4a;
}
QTableWidget::item:selected {
    background-color: #3a3a6a;
    color: #ffffff;
}
QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit {
    background-color: #252545;
    color: #e0e0f0;
    border: 1px solid #3a3a6a;
    border-radius: 6px;
    padding: 8px;
    font-size: 13px;
}
QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #6c63ff;
}
QComboBox QAbstractItemView {
    background-color: #1a1a2e;
    color: #e0e0f0;
    border: 1px solid #3a3a6a;
}
QLabel {
    color: #e0e0f0;
}
QGroupBox {
    color: #e0e0f0;
    font-size: 14px;
    font-weight: 600;
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 18px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
    color: #6c63ff;
}
QScrollBar:vertical {
    background-color: #1a1a2e;
    width: 12px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #3a3a6a;
    border-radius: 6px;
    min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""


# ── Login mejorado ────────────────────────────────────────────────────
class LoginDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("ERP Constructora — Ingreso")
        self.setFixedSize(420, 320)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f0f1a, stop:1 #1a1a2e
                );
            }
            QLabel { color: #e0e0f0; }
            QLineEdit {
                background-color: #252545;
                color: #e0e0f0;
                border: 2px solid #3a3a6a;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #6c63ff;
            }
            QPushButton {
                background-color: #6c63ff;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7c73ff;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Logo
        lbl_logo = QLabel("🏗️")
        lbl_logo.setAlignment(Qt.AlignCenter)
        lf = QFont()
        lf.setPointSize(40)
        lbl_logo.setFont(lf)

        # Título
        title = QLabel("ERP Constructora")
        title.setAlignment(Qt.AlignCenter)
        tf = QFont()
        tf.setPointSize(20)
        tf.setBold(True)
        title.setFont(tf)
        title.setStyleSheet("color: #6c63ff;")

        # Subtítulo
        subtitle = QLabel("Sistema de Gestión para Constructoras")
        subtitle.setAlignment(Qt.AlignCenter)
        sf = QFont()
        sf.setPointSize(11)
        subtitle.setFont(sf)
        subtitle.setStyleSheet("color: #8888aa;")

        layout.addStretch(1)
        layout.addWidget(lbl_logo)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)

        # Formulario de login
        form = QFormLayout()
        form.setSpacing(10)

        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("admin")
        form.addRow("👤 Usuario:", self.txt_usuario)

        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("admin")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.returnPressed.connect(self._do_login)
        form.addRow("🔒 Contraseña:", self.txt_password)

        layout.addLayout(form)
        layout.addSpacing(10)

        self.btn_ingresar = QPushButton("🚀 Ingresar")
        self.btn_ingresar.setMinimumHeight(45)
        self.btn_ingresar.clicked.connect(self._do_login)
        layout.addWidget(self.btn_ingresar)

        layout.addStretch(1)

    def _do_login(self):
        usuario = self.txt_usuario.text().strip()
        password = self.txt_password.text().strip()

        # Usuario por defecto
        if usuario == "admin" and password == "admin":
            self.accept()
            return

        # Verificar en BD
        cur = self.db.conn.execute(
            "SELECT * FROM usuarios WHERE nombre = ? AND password = ?",
            (usuario, password)
        )
        user = cur.fetchone()
        if user:
            self.accept()
        else:
            QMessageBox.warning(
                self, "Acceso denegado",
                "Usuario o contraseña incorrectos.\n\n"
                "Usuario por defecto: admin / admin"
            )


# ── Dashboard ────────────────────────────────────────────────────────
class MainDashboard(QMainWindow):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.setWindowTitle("ERP Constructora — Dashboard")
        self.resize(1300, 820)

        # Centrar en pantalla
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - 1300) // 2
        y = (screen.height() - 820) // 2
        self.move(x, y)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)

        self.tabs = QTabWidget()
        self.tabs.addTab(ObrasTab(db),    "📋 Obras")
        self.tabs.addTab(ClientesTab(db), "👥 Clientes")
        self.tabs.addTab(CatalogoTab(db), "📦 Catálogo")
        self.tabs.addTab(PresupuestoTab(db), "💰 Presupuesto")

        layout.addWidget(self.tabs)


# ── Entry Point ──────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ERP Constructora")
    app.setStyleSheet(DARK_STYLE)

    # Inicializar BD
    db = Database(DB_PATH)
    db.connect()
    db.ensure_defaults()  # Crear usuario admin por defecto

    # Login
    login = LoginDialog(db)
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
