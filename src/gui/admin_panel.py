"""
Panel de Administración - CRUD Usuarios con asignación de roles
Diseño futurista con tabla y formulario
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QComboBox, QGroupBox, QCheckBox,
    QMessageBox, QFrame, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QFont, QBrush


# ============================================================
# FORMULARIO DE USUARIO
# ============================================================

class UsuarioFormDialog(QDialog):
    """Diálogo para crear/editar un usuario."""

    def __init__(self, db_repo, usuario=None, parent=None):
        super().__init__(parent)
        self.db = db_repo
        self.usuario = usuario  # None = crear, dict = editar
        self._setup_ui()

        if usuario:
            self._populate(usuario)

    def _setup_ui(self):
        mode = "EDITAR" if self.usuario else "NUEVO"
        self.setWindowTitle(f"{mode} USUARIO")
        self.setFixedSize(500, 480)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a1a, stop:0.5 #0d0d2b, stop:1 #0a0a1a
                );
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Título
        title = QLabel(f"{'✏️' if self.usuario else '➕'} {mode} USUARIO")
        title.setStyleSheet("""
            font-size: 18px; font-weight: bold; color: #00f0ff;
            background: transparent; letter-spacing: 2px;
        """)
        layout.addWidget(title)

        # Línea decorativa
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
                           "stop:0 transparent, stop:0.5 #00f0ff, stop:1 transparent);")
        line.setFixedHeight(1)
        layout.addWidget(line)
        layout.addSpacing(8)

        # Formulario
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ej: jperez")
        self.username_input.setMaxLength(20)
        form.addRow("USUARIO:", self.username_input)

        # Contraseña
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Máx 20 caracteres")
        self.password_input.setMaxLength(20)
        self.password_input.setEchoMode(QLineEdit.Password)
        if self.usuario:
            self.password_input.setPlaceholderText("Dejar vacío para mantener actual")
            form.addRow("NUEVA CONTRASEÑA:", self.password_input)
        else:
            form.addRow("CONTRASEÑA:", self.password_input)

        # Nombre completo
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Ej: Juan Pérez")
        form.addRow("NOMBRE:", self.nombre_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Ej: juan@ejemplo.com")
        form.addRow("EMAIL:", self.email_input)

        # Estado
        self.estado_combo = QComboBox()
        self.estado_combo.addItem("Activo", 1)
        self.estado_combo.addItem("Inactivo", 0)
        form.addRow("ESTADO:", self.estado_combo)

        layout.addLayout(form)
        layout.addSpacing(8)

        # Roles (checkboxes)
        roles_group = QGroupBox("ROLES ASIGNADOS")
        roles_group.setStyleSheet("""
            QGroupBox {
                color: #00f0ff; font-weight: bold;
                border: 1px solid #2a2a5a; border-radius: 10px;
                margin-top: 16px; padding: 16px; padding-top: 24px;
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 16px;
                padding: 0 8px; color: #00f0ff;
            }
        """)
        roles_layout = QVBoxLayout(roles_group)

        self.role_checks = []
        all_roles = self.db.get_all_roles()
        for rol in all_roles:
            cb = QCheckBox(f"{rol['nombre']}")
            cb.setProperty("rol_id", rol['id_rol'])
            cb.setToolTip(rol['descripcion'])
            roles_layout.addWidget(cb)
            self.role_checks.append(cb)

        layout.addWidget(roles_group)
        layout.addStretch()

        # Botones
        btn_layout = QHBoxLayout()

        cancel_btn = QPushButton("CANCELAR")
        cancel_btn.setObjectName("btnSecondary")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("GUARDAR")
        save_btn.setObjectName("btnPrimary")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _populate(self, usuario):
        """Rellena el formulario con datos existentes."""
        self.username_input.setText(usuario['username'])
        self.nombre_input.setText(usuario.get('nombre', ''))
        self.email_input.setText(usuario.get('email', ''))

        idx = self.estado_combo.findData(usuario.get('activo', 1))
        if idx >= 0:
            self.estado_combo.setCurrentIndex(idx)

        # Marcar roles del usuario
        user_roles = self.db.get_roles_by_usuario(usuario['id_user'])
        user_role_ids = {r['id_rol'] for r in user_roles}
        for cb in self.role_checks:
            if cb.property("rol_id") in user_role_ids:
                cb.setChecked(True)

    def _save(self):
        """Valida y guarda."""
        try:
            username = self.username_input.text().strip()
            password = self.password_input.text()
            nombre = self.nombre_input.text().strip()
            email = self.email_input.text().strip()
            activo = self.estado_combo.currentData()

            # Validaciones
            if not username:
                raise ValueError("El nombre de usuario es obligatorio.")
            if len(username) > 20:
                raise ValueError("El usuario no puede exceder 20 caracteres.")

            if self.usuario:
                # EDITAR
                update_kwargs = {
                    'username': username,
                    'nombre': nombre or None,
                    'email': email or None,
                    'activo': activo
                }
                if password:
                    if len(password) > 20:
                        raise ValueError("La contraseña no puede exceder 20 caracteres.")
                    update_kwargs['password'] = password

                self.db.update_usuario(self.usuario['id_user'], **update_kwargs)
            else:
                # CREAR
                if not password:
                    raise ValueError("La contraseña es obligatoria.")
                if len(password) > 20:
                    raise ValueError("La contraseña no puede exceder 20 caracteres.")

                new_id = self.db.create_usuario(
                    username=username,
                    password=password,
                    nombre=nombre,
                    email=email,
                    activo=activo
                )
                self.usuario = {'id_user': new_id}

            # Asignar roles
            selected_roles = [
                cb.property("rol_id") for cb in self.role_checks if cb.isChecked()
            ]
            user_id = self.usuario['id_user']
            self.db.set_usuario_roles(user_id, selected_roles)

            self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Error de validación", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar: {str(e)}")


# ============================================================
# PANEL ADMIN
# ============================================================

class AdminPanel(QWidget):
    """Panel de administración de usuarios y roles."""

    def __init__(self, db_repo, parent=None):
        super().__init__(parent)
        self.db = db_repo
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # ===== HEADER =====
        header = QHBoxLayout()

        title = QLabel("👥 ADMINISTRACIÓN DE USUARIOS")
        title.setStyleSheet("""
            font-size: 20px; font-weight: bold; color: #00f0ff;
            background: transparent; letter-spacing: 1px;
        """)
        header.addWidget(title)

        header.addStretch()

        # Botones
        add_btn = QPushButton("➕ NUEVO USUARIO")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._nuevo_usuario)
        header.addWidget(add_btn)

        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedWidth(50)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setToolTip("Recargar datos")
        refresh_btn.clicked.connect(self._load_data)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # ===== TABLA =====
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "USUARIO", "NOMBRE", "EMAIL", "ROLES", "ESTADO", "ÚLTIMO ACCESO"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)

        # Ajustar anchos
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)

        self.table.doubleClicked.connect(self._editar_usuario_seleccionado)

        layout.addWidget(self.table)

        # ===== BOTONES DE ACCIÓN =====
        action_layout = QHBoxLayout()

        edit_btn = QPushButton("✏️ EDITAR")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(self._editar_usuario_seleccionado)
        action_layout.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️ ELIMINAR")
        delete_btn.setObjectName("btnDanger")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(self._eliminar_usuario_seleccionado)
        action_layout.addWidget(delete_btn)

        action_layout.addStretch()

        # Status label
        self.status_label = QLabel("")
        self.status_label.setObjectName("SuccessLabel")
        self.status_label.setStyleSheet("font-size: 11px; color: #7c7cba; background: transparent;")
        action_layout.addWidget(self.status_label)

        layout.addLayout(action_layout)

    def _load_data(self):
        """Carga los datos en la tabla."""
        usuarios = self.db.get_all_usuarios()
        self.table.setRowCount(len(usuarios))

        COLORS = {
            "activo": QColor("#00e676"),
            "inactivo": QColor("#ff5252"),
        }

        for i, user in enumerate(usuarios):
            # ID
            self.table.setItem(i, 0, QTableWidgetItem(str(user['id_user'])))

            # Username
            item_user = QTableWidgetItem(user['username'])
            item_user.setFont(QFont("Segoe UI", 11, QFont.Bold))
            self.table.setItem(i, 1, item_user)

            # Nombre
            self.table.setItem(i, 2, QTableWidgetItem(user.get('nombre', '') or ''))

            # Email
            self.table.setItem(i, 3, QTableWidgetItem(user.get('email', '') or ''))

            # Roles
            roles_str = user.get('roles', '') or ''
            item_roles = QTableWidgetItem(roles_str)
            item_roles.setForeground(QColor("#7c4dff"))
            self.table.setItem(i, 4, item_roles)

            # Estado
            activo = user.get('activo', 1)
            estado_text = "● ACTIVO" if activo else "○ INACTIVO"
            item_estado = QTableWidgetItem(estado_text)
            item_estado.setForeground(COLORS.get("activo" if activo else "inactivo"))
            self.table.setItem(i, 5, item_estado)

            # Último acceso
            last_access = user.get('ultimo_acceso', '') or 'Nunca'
            self.table.setItem(i, 6, QTableWidgetItem(last_access))

        self.status_label.setText(f"{len(usuarios)} usuarios cargados")
        QTimer.singleShot(3000, lambda: self.status_label.setText(""))

    def _nuevo_usuario(self):
        """Abre diálogo para crear nuevo usuario."""
        dialog = UsuarioFormDialog(self.db, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self._load_data()
            self.status_label.setStyleSheet("font-size: 11px; color: #00e676; background: transparent;")
            self.status_label.setText("✓ Usuario creado exitosamente")
            QTimer.singleShot(3000, lambda: self.status_label.setText(""))

    def _editar_usuario_seleccionado(self):
        """Abre diálogo para editar el usuario seleccionado."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Seleccionar", "Seleccione un usuario para editar.")
            return

        user_id = int(self.table.item(row, 0).text())
        user = self.db.get_usuario(user_id)
        if not user:
            QMessageBox.warning(self, "Error", "Usuario no encontrado.")
            return

        dialog = UsuarioFormDialog(self.db, usuario=user, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self._load_data()
            self.status_label.setStyleSheet("font-size: 11px; color: #00e676; background: transparent;")
            self.status_label.setText("✓ Usuario actualizado exitosamente")
            QTimer.singleShot(3000, lambda: self.status_label.setText(""))

    def _eliminar_usuario_seleccionado(self):
        """Elimina el usuario seleccionado."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Seleccionar", "Seleccione un usuario para eliminar.")
            return

        username = self.table.item(row, 1).text()
        user_id = int(self.table.item(row, 0).text())

        if username == "admin":
            QMessageBox.warning(self, "Acción denegada",
                                "No se puede eliminar el usuario administrador por defecto.")
            return

        confirm = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Está seguro de eliminar al usuario '{username}'?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                self.db.delete_usuario(user_id)
                self._load_data()
                self.status_label.setStyleSheet(
                    "font-size: 11px; color: #ff5252; background: transparent;"
                )
                self.status_label.setText(f"✗ Usuario '{username}' eliminado")
                QTimer.singleShot(3000, lambda: self.status_label.setText(""))
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
