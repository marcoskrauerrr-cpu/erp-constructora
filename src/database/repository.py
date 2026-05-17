"""
Repository - Capa de acceso a datos para Usuarios y Roles
"""

import sqlite3


class UsuarioRepository:
    """CRUD de usuarios con validaciones de unicidad y longitud."""

    # Constantes de validación
    MAX_USERNAME = 20
    MAX_PASSWORD = 20

    def __init__(self, db_path):
        self.db_path = db_path

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    # ============================================================
    # VALIDACIONES
    # ============================================================

    def _validate_username(self, username):
        """Valida username: requerido, único, máx 20 chars."""
        if not username or not username.strip():
            raise ValueError("El nombre de usuario es obligatorio.")
        username = username.strip()
        if len(username) > self.MAX_USERNAME:
            raise ValueError(f"El nombre de usuario no puede exceder {self.MAX_USERNAME} caracteres.")
        # Solo alfanumérico + guión bajo
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValueError("El nombre de usuario solo puede contener letras, números y guión bajo.")
        return username

    def _validate_password(self, password):
        """Valida password: requerida, máx 20 chars."""
        if not password:
            raise ValueError("La contraseña es obligatoria.")
        if len(password) > self.MAX_PASSWORD:
            raise ValueError(f"La contraseña no puede exceder {self.MAX_PASSWORD} caracteres.")
        return password

    def _check_unique_username(self, username, exclude_id=None):
        """Verifica que el username no exista ya."""
        conn = self._connect()
        try:
            if exclude_id:
                row = conn.execute(
                    "SELECT 1 FROM usuarios WHERE username = ? AND id_user != ?",
                    (username, exclude_id)
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT 1 FROM usuarios WHERE username = ?", (username,)
                ).fetchone()
            if row:
                raise ValueError(f"El usuario '{username}' ya existe. Debe ser único.")
        finally:
            conn.close()

    # ============================================================
    # CRUD USUARIOS
    # ============================================================

    def create_usuario(self, username, password, nombre="", email="", activo=1):
        """Crea un nuevo usuario con validaciones."""
        username = self._validate_username(username)
        password = self._validate_password(password)
        self._check_unique_username(username)

        conn = self._connect()
        try:
            cursor = conn.execute(
                """INSERT INTO usuarios (username, password, nombre, email, activo)
                   VALUES (?, ?, ?, ?, ?)""",
                (username, password, nombre, email, activo)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_usuario(self, id_user):
        """Obtiene un usuario por ID."""
        conn = self._connect()
        try:
            return conn.execute(
                "SELECT * FROM usuarios WHERE id_user = ?", (id_user,)
            ).fetchone()
        finally:
            conn.close()

    def get_usuario_by_username(self, username):
        """Obtiene un usuario por nombre de usuario."""
        conn = self._connect()
        try:
            return conn.execute(
                "SELECT * FROM usuarios WHERE username = ?", (username,)
            ).fetchone()
        finally:
            conn.close()

    def get_all_usuarios(self):
        """Lista todos los usuarios con sus roles."""
        conn = self._connect()
        try:
            rows = conn.execute("""
                SELECT u.*, GROUP_CONCAT(r.nombre, ', ') as roles
                FROM usuarios u
                LEFT JOIN usuarios_roles ur ON u.id_user = ur.id_user
                LEFT JOIN roles r ON ur.id_rol = r.id_rol
                GROUP BY u.id_user
                ORDER BY u.username
            """).fetchall()
            return rows
        finally:
            conn.close()

    def update_usuario(self, id_user, username=None, password=None,
                       nombre=None, email=None, activo=None):
        """Actualiza un usuario existente."""
        conn = self._connect()
        try:
            existing = conn.execute(
                "SELECT * FROM usuarios WHERE id_user = ?", (id_user,)
            ).fetchone()
            if not existing:
                raise ValueError(f"Usuario ID {id_user} no encontrado.")

            fields = []
            values = []

            if username is not None:
                username = self._validate_username(username)
                self._check_unique_username(username, exclude_id=id_user)
                fields.append("username = ?")
                values.append(username)

            if password is not None:
                password = self._validate_password(password)
                fields.append("password = ?")
                values.append(password)

            if nombre is not None:
                fields.append("nombre = ?")
                values.append(nombre)

            if email is not None:
                fields.append("email = ?")
                values.append(email)

            if activo is not None:
                fields.append("activo = ?")
                values.append(1 if activo else 0)

            if not fields:
                return  # Nothing to update

            values.append(id_user)
            conn.execute(
                f"UPDATE usuarios SET {', '.join(fields)} WHERE id_user = ?",
                values
            )
            conn.commit()
        finally:
            conn.close()

    def delete_usuario(self, id_user):
        """Elimina un usuario (no permite eliminar admin)."""
        conn = self._connect()
        try:
            user = conn.execute(
                "SELECT username FROM usuarios WHERE id_user = ?", (id_user,)
            ).fetchone()
            if not user:
                raise ValueError("Usuario no encontrado.")
            if user["username"] == "admin":
                raise ValueError("No se puede eliminar el usuario administrador por defecto.")

            conn.execute("DELETE FROM usuarios WHERE id_user = ?", (id_user,))
            conn.commit()
        finally:
            conn.close()

    def authenticate(self, username, password):
        """Autentica un usuario. Retorna el usuario o None."""
        conn = self._connect()
        try:
            user = conn.execute(
                "SELECT * FROM usuarios WHERE username = ? AND password = ? AND activo = 1",
                (username, password)
            ).fetchone()
            if user:
                # Actualizar último acceso
                conn.execute(
                    "UPDATE usuarios SET ultimo_acceso = CURRENT_TIMESTAMP WHERE id_user = ?",
                    (user["id_user"],)
                )
                conn.commit()
            return user
        finally:
            conn.close()

    # ============================================================
    # ROLES
    # ============================================================

    def get_all_roles(self):
        """Lista todos los roles disponibles."""
        conn = self._connect()
        try:
            return conn.execute(
                "SELECT * FROM roles ORDER BY nivel DESC"
            ).fetchall()
        finally:
            conn.close()

    def get_roles_by_usuario(self, id_user):
        """Obtiene los roles asignados a un usuario."""
        conn = self._connect()
        try:
            return conn.execute("""
                SELECT r.* FROM roles r
                JOIN usuarios_roles ur ON r.id_rol = ur.id_rol
                WHERE ur.id_user = ?
                ORDER BY r.nivel DESC
            """, (id_user,)).fetchall()
        finally:
            conn.close()

    def set_usuario_roles(self, id_user, roles_ids):
        """Reemplaza todos los roles de un usuario."""
        conn = self._connect()
        try:
            conn.execute("DELETE FROM usuarios_roles WHERE id_user = ?", (id_user,))
            for rid in roles_ids:
                conn.execute(
                    "INSERT INTO usuarios_roles (id_user, id_rol) VALUES (?, ?)",
                    (id_user, rid)
                )
            conn.commit()
        finally:
            conn.close()

    def create_rol(self, nombre, descripcion="", nivel=0):
        """Crea un nuevo rol."""
        conn = self._connect()
        try:
            cursor = conn.execute(
                "INSERT INTO roles (nombre, descripcion, nivel) VALUES (?, ?, ?)",
                (nombre, descripcion, nivel)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    # ============================================================
    # VERIFICACIÓN
    # ============================================================

    def check_constraints(self):
        """Verifica que no haya duplicados en usuarios (seguridad extra)."""
        conn = self._connect()
        try:
            dups = conn.execute("""
                SELECT username, COUNT(*) as cnt
                FROM usuarios
                GROUP BY username
                HAVING cnt > 1
            """).fetchall()
            if dups:
                return [dict(d) for d in dups]
            return []
        finally:
            conn.close()

    def check_password_lengths(self):
        """Verifica que ninguna contraseña exceda 20 caracteres."""
        conn = self._connect()
        try:
            long_pw = conn.execute("""
                SELECT id_user, username, LENGTH(password) as pw_len
                FROM usuarios
                WHERE LENGTH(password) > 20
            """).fetchall()
            if long_pw:
                return [dict(d) for d in long_pw]
            return []
        finally:
            conn.close()

    # ============================================================
    # UTILIDAD
    # ============================================================

    def ensure_defaults(self):
        """Asegura que existan los datos por defecto."""
        from .schema import SCHEMA_SQL
        conn = self._connect()
        try:
            conn.executescript(SCHEMA_SQL)
            conn.commit()
        finally:
            conn.close()
