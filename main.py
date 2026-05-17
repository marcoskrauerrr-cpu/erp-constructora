#!/usr/bin/env python3
"""
ERP Constructora - Main Entry Point
"""

import sys
import os
import logging

# Determinar directorio base (funciona tanto en desarrollo como en .exe compilado)
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, APP_DIR)

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QMessageBox, QStatusBar
from PySide6.QtCore import Qt

from src.database.repository import UsuarioRepository
from src.gui.login import LoginDialog
from src.gui.admin_panel import AdminPanel
from src.gui.styles.futuristic_style import apply_style
from src.core.launcher import CoreLauncher

DB_PATH = os.path.join(APP_DIR, "data", "erp_constructora.db")
VERSION = "1.1.0"

# Configurar logging
log_path = os.path.join(APP_DIR, "data", "erp.log")
os.makedirs(os.path.join(APP_DIR, "data"), exist_ok=True)
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


class SidebarButton(QPushButton):
    def __init__(self, text: str, icon: str = ""):
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
            QPushButton:hover { background: #21262d; color: #e1e4e8; }
            QPushButton:checked { background: #1f3a5f; color: #58a6ff; }
        """)


class DashboardMain(QMainWindow):
    def __init__(self, db_repo, user: dict):
        super().__init__()
        self.db = db_repo
        self.user = user
        self.core = CoreLauncher(db_repo, user)
        self.pages: dict = {}
        self.core.register_module("admin_usuarios", AdminPanel, min_level=100)
        self._setup_ui()
        self._show_page("inicio")
        logger.info(f"Usuario '{user['username']}' inició sesión")

    def _setup_ui(self):
        self.setWindowTitle(f"ERP Constructora v{VERSION}")
        self.setMinimumSize(1100, 680)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Topbar
        topbar = QWidget()
        topbar.setFixedHeight(52)
        topbar.setStyleSheet("background-color: #161b22; border-bottom: 1px solid #30363d;")
        tl = QHBoxLayout(topbar)
        tl.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("ERP Constructora")
        logo.setStyleSheet("font-size: 15px; font-weight: 600; color: #e1e4e8; background: transparent;")
        tl.addWidget(logo)
        tl.addStretch()

        info = self.core.get_user_info()
        roles_str = ", ".join(info['roles'][:2])
        user_tag = QLabel(f"{info['nombre'] or info['username']}  ·  {roles_str}")
        user_tag.setStyleSheet("font-size: 12px; color: #8b949e; background: transparent;")
        tl.addWidget(user_tag)

        logout_btn = QPushButton("Salir")
        logout_btn.setObjectName("btnSecondary")
        logout_btn.setFixedWidth(80)
        logout_btn.setFixedHeight(32)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self._confirm_logout)
        tl.addWidget(logout_btn)
        main_layout.addWidget(topbar)

        # Body
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #0f1117; border-right: 1px solid #21262d;")
        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(8, 12, 8, 12)
        sl.setSpacing(2)

        sec = QLabel("MÓDULOS")
        sec.setStyleSheet("font-size: 10px; color: #484f58; letter-spacing: 1px; padding: 8px 12px 4px; background: transparent;")
        sl.addWidget(sec)

        self.nav_btns: dict = {}
        for key, icon, label in [("inicio", "🏠", "Inicio"), ("usuarios", "👥", "Usuarios")]:
            btn = SidebarButton(label, icon)
            btn.clicked.connect(lambda checked, k=key: self._show_page(k))
            sl.addWidget(btn)
            self.nav_btns[key] = btn

        # Separador visual
        sep = QLabel("")
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #21262d; margin: 8px 12px;")
        sl.addWidget(sep)

        # Modulos disponibles
        mod_title = QLabel("MÓDULOS ACTIVOS")
        mod_title.setStyleSheet("font-size: 10px; color: #484f58; letter-spacing: 1px; padding: 8px 12px 4px; background: transparent;")
        sl.addWidget(mod_title)

        info = self.core.get_user_info()
        for m in self.core.get_available_modules():
            mi = QLabel(f"  ✅  {m}")
            mi.setStyleSheet("font-size: 11px; color: #8b949e; padding: 4px 12px; background: transparent;")
            sl.addWidget(mi)

        sl.addStretch()
        ver = QLabel(f"v{VERSION}")
        ver.setStyleSheet("font-size: 10px; color: #484f58; padding: 8px 12px; background: transparent;")
        sl.addWidget(ver)
        body.addWidget(sidebar)

        self.stack = QStackedWidget()
        body.addWidget(self.stack, 1)
        main_layout.addLayout(body)

        self.statusBar().setStyleSheet("background: #161b22; color: #8b949e; border-top: 1px solid #30363d; font-size: 11px;")
        self.statusBar().showMessage("Sistema listo")

        # Welcome
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

        box = QWidget()
        box.setStyleSheet("background: #161b22; border: 1px solid #30363d; border-radius: 8px; max-width: 500px;")
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
        self.stack.addWidget(QWidget())

    def _show_page(self, key: str):
        for k, btn in self.nav_btns.items():
            btn.setChecked(k == key)
        if key == "inicio":
            self.stack.setCurrentIndex(0)
            return
        if key == "usuarios":
            if "usuarios" not in self.pages:
                panel = AdminPanel(self.db, parent=self)
                self.pages["usuarios"] = panel
                self.stack.addWidget(panel)
            self.stack.setCurrentWidget(self.pages["usuarios"])
            self.pages["usuarios"].refresh()

    def _confirm_logout(self):
        if QMessageBox.question(self, "Cerrar sesión", "¿Está seguro de cerrar sesión?",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            logger.info(f"Usuario '{self.user['username']}' cerró sesión")
            self.close()


def main():
    logger.info("Iniciando ERP Constructora")
    app = QApplication(sys.argv)
    app.setApplicationName("ERP Constructora")
    apply_style(app)

    repo = UsuarioRepository(DB_PATH)
    try:
        repo.ensure_defaults()
    except Exception as e:
        logger.error(f"Error inicializando BD: {e}")
        QMessageBox.critical(None, "Error crítico", f"No se pudo inicializar la base de datos:\n{e}")
        sys.exit(1)

    login = LoginDialog(repo)
    if login.exec() != LoginDialog.Accepted:
        logger.info("Login cancelado por el usuario")
        sys.exit(0)

    user = login.get_logged_user()
    if not user:
        sys.exit(0)

    dash = DashboardMain(repo, dict(user))
    dash.show()
    logger.info("Aplicación iniciada correctamente")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
