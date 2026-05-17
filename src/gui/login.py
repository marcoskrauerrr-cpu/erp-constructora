"""
Login Dialog - Diseño futurista cyberpunk
Pantalla completa con gradiente, glow y animaciones
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QWidget, QApplication
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Property, Signal
from PySide6.QtGui import QFont, QPixmap, QPainter, QLinearGradient, QColor, QBrush, QPen


class GlowButton(QPushButton):
    """Botón con efecto glow animado."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._glow = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate_glow)
        self._timer.start(50)
        self._direction = 1

    def _animate_glow(self):
        self._glow += 0.02 * self._direction
        if self._glow >= 1.0:
            self._direction = -1
        elif self._glow <= 0.0:
            self._direction = 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fondo gradiente
        grad = QLinearGradient(0, 0, self.width(), 0)
        glow_intensity = int(60 + 40 * self._glow)
        grad.setColorAt(0, QColor(0, 200 + glow_intensity // 3, 255))
        grad.setColorAt(1, QColor(124 + glow_intensity // 3, 77, 255))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

        # Texto centrado
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Segoe UI", 13, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())

        painter.end()


class LoginDialog(QDialog):
    """Pantalla de login con diseño futurista."""

    login_successful = Signal(object)  # Emite el usuario logueado

    def __init__(self, db_repo, parent=None):
        super().__init__(parent)
        self.db = db_repo
        self._user = None  # Store authenticated user
        self._setup_ui()
        self._apply_theme()

    def _setup_ui(self):
        """Construye la interfaz del login."""
        self.setWindowTitle("ERP Constructora - Acceso")
        self.setObjectName("LoginWindow")
        self.setFixedSize(420, 520)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(0)

        # ===== LOGO / TÍTULO =====
        title_label = QLabel("ERP Constructora")
        title_label.setObjectName("LoginTitle")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        main_layout.addSpacing(4)

        version_label = QLabel("Plataforma de Gestión")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setObjectName("LoginSubtitle")
        main_layout.addWidget(version_label)
        main_layout.addSpacing(30)

        # ===== FORMULARIO =====
        form_container = QWidget()
        form_container.setStyleSheet("""
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(16)

        # Título del formulario
        form_title = QLabel("Iniciar sesión")
        form_title.setAlignment(Qt.AlignCenter)
        form_title.setStyleSheet("font-size: 14px; font-weight: 600; "
                                 "color: #e1e4e8; background: transparent; margin-bottom: 8px;")
        form_layout.addWidget(form_title)

        # Usuario
        user_label = QLabel("Usuario")
        user_label.setStyleSheet("font-size: 12px; color: #8b949e; "
                                 "font-weight: 500; background: transparent;")
        form_layout.addWidget(user_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ingrese su usuario...")
        self.username_input.setMaxLength(20)
        self.username_input.returnPressed.connect(self._try_login)
        form_layout.addWidget(self.username_input)

        # Contraseña
        pass_label = QLabel("Contraseña")
        pass_label.setStyleSheet("font-size: 12px; color: #8b949e; "
                                 "font-weight: 500; background: transparent;")
        form_layout.addWidget(pass_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("••••••••••")
        self.password_input.setMaxLength(20)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self._try_login)
        form_layout.addWidget(self.password_input)

        form_layout.addSpacing(8)

        # Botón de login
        self.login_btn = QPushButton("Acceder")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setMinimumHeight(40)
        self.login_btn.clicked.connect(self._try_login)
        form_layout.addWidget(self.login_btn)

        # Mensaje de error
        self.error_label = QLabel("")
        self.error_label.setObjectName("ErrorLabel")
        self.error_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(self.error_label)

        main_layout.addWidget(form_container)
        main_layout.addStretch()

        # ===== FOOTER =====
        footer = QLabel("© 2026 ERP Constructora")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("font-size: 10px; color: #484f58; background: transparent;")
        main_layout.addWidget(footer)

        self.setLayout(main_layout)

    def _fade_in(self):
        """Efecto fade-in al abrir."""
        self._opacity += 0.05
        if self._opacity >= 1.0:
            self._opacity = 1.0
            self._fade_timer.stop()
        self.setWindowOpacity(self._opacity)

    def _apply_theme(self):
        """Aplica fondo gradiente con painter."""
        pass  # El estilo global se aplica desde main.py

    def _try_login(self):
        """Intenta autenticar al usuario."""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        # Validaciones básicas
        if not username:
            self._show_error("Ingrese su nombre de usuario.")
            return
        if not password:
            self._show_error("Ingrese su contraseña.")
            return
        if len(username) > 20:
            self._show_error("El usuario no puede exceder 20 caracteres.")
            return
        if len(password) > 20:
            self._show_error("La contraseña no puede exceder 20 caracteres.")
            return

        # Autenticar
        user = self.db.authenticate(username, password)
        if user:
            self._user = user
            self.accept()
        else:
            self._show_error("Usuario o contraseña incorrectos.")
            self.password_input.clear()
            self.password_input.setFocus()

    def _accept_login(self, user):
        """Acepta el login y emite la señal."""
        self._user = user
        self.login_successful.emit(user)
        self.accept()

    def _show_error(self, msg):
        """Muestra mensaje de error."""
        self.error_label.setText(msg)

    def get_logged_user(self):
        """Retorna el usuario autenticado."""
        return self._user


# Para pruebas rápidas
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from database.repository import UsuarioRepository

    app = QApplication(sys.argv)
    from styles.futuristic_style import apply_style
    apply_style(app)

    db_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'erp_constructora.db')
    repo = UsuarioRepository(db_path)
    repo.ensure_defaults()

    login = LoginDialog(repo)
    if login.exec() == QDialog.Accepted:
        print("Login exitoso!")
    sys.exit(0)
