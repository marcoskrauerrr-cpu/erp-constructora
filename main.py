#!/usr/bin/env python3
"""
ERP Constructora - Main Entry Point
Módulo de Usuarios y Roles con autenticación
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QMessageBox, QStatusBar
)
from PySide6.QtCore import Qt

from src.database.repository import UsuarioRepository
from src.gui.login import LoginDialog
from src.gui.admin_panel import AdminPanel
from src.gui.styles.futuristic_style import apply_style
from src.core.launcher import CoreLauncher

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "data", "erp_constructora.db")


class SidebarButton(QPushButton):
    """Botón de navegación en la sidebar."""

    def __init__(self, text, icon=""):
        super().__init__(f"  {icon}  {text}" if icon else text)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(38)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                text-align: left; padding: 8px 16px;
                font-size: 13px; border-radius: 6px;
                background: transparent; color: #8b949e;
                border: none; margin: 1px 0;
            }
            QPushButton:hover {
                background: #21262d; color: #e1e4e8;
            }
            QPushButton:checked {
                background: #1f3a5f; color: #58a6ff;
            }
        """)


class DashboardMain(QMainWindow):
    """Dashboard principal del ERP."""

    def __init__(self, db_repo, user):
        super().__init__()
        self.db = db_repo
        self.user = user
        self.core = CoreLauncher(db_repo, user)
        self.pages = {}

        self.core.register_module("admin_usuarios", AdminPanel, min_level=100)

        self._setup_ui()
        self._show_page("inicio")

    def _setup_ui(self):
        self.setWindowTitle("ERP Constructora")
        self.setMinimumSize(1100, 680)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top bar
        topbar = QWidget()
        topbar.setFixedHeight(52)
        topbar.setStyleSheet("background-color: #161b22; border-bottom: 1px solid #30363d;")
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("ERP Constructora")
        logo.setStyleSheet("font-size: 15px; font-weight: 600; color: #e1e4e8; background: transparent;")
        topbar_layout.addWidget(logo)

        topbar_layout.addStretch()

        info = self.core.get_user_info()
        roles_str = ", ".join(info['roles'][:2])
        user_tag = QLabel(f"{info['nombre'] or info['username']}  ·  {roles_str}")
        user_tag.setStyleSheet("font-size: 12px; color: #8b949e; background: transparent;")
        topbar_layout.addWidget(user_tag)

        logout_btn = QPushButton("Salir")
        logout_btn.setObjectName("btnSecondary")
        logout_btn.setFixedWidth(80)
        logout_btn.setFixedHeight(32)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self._confirm_logout)
        topbar_layout.addWidget(logout_btn)

        main_layout.addWidget(topbar)

        # Cuerpo
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #0f1117; border-right: 1px solid #21262d;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(8, 12, 8, 12)
        sidebar_layout.setSpacing(2)

        sec_label = QLabel("MÓDULOS")
        sec_label.setStyleSheet("font-size: 10px; color: #484f58; "
                                "letter-spacing: 1px; padding: 8px 12px 4px; "
                                "background: transparent;")
        sidebar_layout.addWidget(sec_label)

        self.nav_btns = {}
        navs = [
            ("inicio", "🏠", "Inicio"),
            ("usuarios", "👥", "Usuarios"),
        ]
        for key, icon, label in navs:
            btn = SidebarButton(label, icon)
            btn.clicked.connect(lambda checked, k=key: self._show_page(k))
            sidebar_layout.addWidget(btn)
            self.nav_btns[key] = btn

        sidebar_layout.addStretch()

        ver = QLabel("v1.0.0")
        ver.setStyleSheet("font-size: 10px; color: #484f58; padding: 8px 12px; background: transparent;")
        sidebar_layout.addWidget(ver)

        body.addWidget(sidebar)

        # Stacked content
        self.stack = QStackedWidget()
        body.addWidget(self.stack, 1)

        main_layout.addLayout(body)

        # Status bar
        sb = QStatusBar()
        sb.setStyleSheet("background: #161b22; color: #8b949e; "
                         "border-top: 1px solid #30363d; font-size: 11px;")
        self.setStatusBar(sb)
        sb.showMessage("Sistema listo  |  Usuario autenticado")

        # Welcome page
        welcome = QWidget()
        wl = QVBoxLayout(welcome)
        wl.setContentsMargins(40, 60, 40, 60)
        wl.setAlignment(Qt.AlignCenter)

        wt = QLabel("Bienvenido a ERP Constructora")
        wt.setStyleSheet("font-size: 26px; font-weight: 600; color: #e1e4e8; background: transparent;")
        wt.setAlignment(Qt.AlignCenter)
        wl.addWidget(wt)

        ws = QLabel(f"Iniciaste sesión como  {info['nombre'] or info['username']}")
        ws.setStyleSheet("font-size: 14px; color: #8b949e; margin: 8px 0 30px; background: transparent;")
        ws.setAlignment(Qt.AlignCenter)
        wl.addWidget(ws)

        # Info box
        box = QWidget()
        box.setStyleSheet("background: #161b22; border: 1px solid #30363d; "
                          "border-radius: 8px; max-width: 500px;")
        bl = QVBoxLayout(box)
        bl.setContentsMargins(20, 20, 20, 20)

        bt = QLabel("Módulos disponibles")
        bt.setStyleSheet("font-size: 14px; font-weight: 600; color: #58a6ff; background: transparent;")
        bl.addWidget(bt)

        for m in self.core.get_available_modules():
            mi = QLabel(f"  ✅  {m}")
            mi.setStyleSheet("font-size: 12px; color: #e1e4e8; padding: 6px 0; background: transparent;")
            bl.addWidget(mi)

        wl.addWidget(box, alignment=Qt.AlignCenter)
        self.stack.addWidget(welcome)

        # Páginas de módulos (placeholder para usuarios)
        self.stack.addWidget(QWidget())

    def _show_page(self, key):
        for k, btn in self.nav_btns.items():
            btn.setChecked(k == key)

        if key == "inicio":
            self.stack.setCurrentIndex(0)
            return

        if key == "usuarios" and "usuarios" not in self.pages:
            panel = AdminPanel(self.db, parent=self)
            self.pages["usuarios"] = panel
            self.stack.addWidget(panel)
            self.stack.setCurrentWidget(panel)
            panel._load_data()
        elif key == "usuarios" and "usuarios" in self.pages:
            self.stack.setCurrentWidget(self.pages["usuarios"])
            self.pages["usuarios"]._load_data()

    def _confirm_logout(self):
        confirm = QMessageBox.question(
            self, "Cerrar sesión",
            "¿Está seguro de cerrar sesión?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.close()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ERP Constructora")
    apply_style(app)

    repo = UsuarioRepository(DB_PATH)
    repo.ensure_defaults()

    login = LoginDialog(repo)
    if login.exec() != LoginDialog.Accepted:
        sys.exit(0)

    user = login.get_logged_user()
    if not user:
        sys.exit(0)

    dash = DashboardMain(repo, user)
    dash.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
