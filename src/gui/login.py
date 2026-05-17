"""
Login Dialog - Diseño corporativo premium
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QWidget
)
from PySide6.QtCore import Qt, Signal


class LoginDialog(QDialog):
    """Pantalla de login premium."""

    def __init__(self, db_repo, parent=None):
        super().__init__(parent)
        self.db = db_repo
        self._user = None
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("ERP Constructora - Acceso")
        self.setObjectName("LoginWindow")
        self.setFixedSize(420, 500)

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(0)

        # Título
        title = QLabel("ERP Constructora")
        title.setObjectName("LoginTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(4)

        sub = QLabel("Plataforma de Gestión")
        sub.setAlignment(Qt.AlignCenter)
        sub.setObjectName("LoginSubtitle")
        layout.addWidget(sub)
        layout.addSpacing(30)

        # Formulario
        form = QWidget()
        form.setStyleSheet("background-color: #161b22; border: 1px solid #30363d; border-radius: 8px;")
        fl = QVBoxLayout(form)
        fl.setContentsMargins(24, 24, 24, 24)
        fl.setSpacing(16)

        form_title = QLabel("Iniciar sesión")
        form_title.setAlignment(Qt.AlignCenter)
        form_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #e1e4e8; background: transparent; margin-bottom: 8px;")
        fl.addWidget(form_title)

        # Usuario
        ul = QLabel("Usuario")
        ul.setStyleSheet("font-size: 12px; color: #8b949e; font-weight: 500; background: transparent;")
        fl.addWidget(ul)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ingrese su usuario...")
        self.username_input.setMaxLength(20)
        self.username_input.returnPressed.connect(self._try_login)
        fl.addWidget(self.username_input)

        # Contraseña
        pl = QLabel("Contraseña")
        pl.setStyleSheet("font-size: 12px; color: #8b949e; font-weight: 500; background: transparent;")
        fl.addWidget(pl)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("••••••••••")
        self.password_input.setMaxLength(20)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self._try_login)
        fl.addWidget(self.password_input)

        fl.addSpacing(8)

        self.login_btn = QPushButton("Acceder")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setMinimumHeight(40)
        self.login_btn.clicked.connect(self._try_login)
        fl.addWidget(self.login_btn)

        self.error_label = QLabel("")
        self.error_label.setObjectName("ErrorLabel")
        self.error_label.setAlignment(Qt.AlignCenter)
        fl.addWidget(self.error_label)

        layout.addWidget(form)
        layout.addStretch()

        footer = QLabel("© 2026 ERP Constructora")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("font-size: 10px; color: #484f58; background: transparent;")
        layout.addWidget(footer)

        self.setLayout(layout)

    def _try_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username:
            self.error_label.setText("Ingrese su nombre de usuario.")
            return
        if not password:
            self.error_label.setText("Ingrese su contraseña.")
            return

        user = self.db.authenticate(username, password)
        if user:
            self._user = user
            self.accept()
        else:
            self.error_label.setText("Usuario o contraseña incorrectos.")
            self.password_input.clear()
            self.password_input.setFocus()

    def get_logged_user(self):
        return self._user
