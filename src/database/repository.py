"""
Repository - Capa de acceso a datos para Usuarios y Roles
"""

import sqlite3
import hashlib
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class UsuarioRepository:
    MAX_USERNAME = 20
    MAX_PASSWORD = 20

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    @staticmethod
    def _hash_password(password: str) -> str:
        """Genera hash SHA-256 con salt incluido (formato: salt$hash)."""
        salt = hashlib.sha256(password.encode()).hexdigest()[:8]
        hashed = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"{salt}${hashed}"

    @staticmethod
    def _check_password(password: str, stored: str) -> bool:
        """Verifica contraseña contra hash almacenado (compatible con texto plano y con hash)."""
        # Compatibilidad hacia atrás: texto plano (sin $)
        if "$" not in stored:
            return password == stored
        salt, hashed = stored.split("$", 1)
        return hashlib.sha256((salt + password).encode()).hexdigest() == hashed

    # ============================================================
    # VALIDACIONES
    # ============================================================

    def _validate_username(self, username: str) -> str:
        if not username or not username.strip():
            raise ValueError("El nombre de usuario es obligatorio.")
        username = username.strip()
        if len(username) > self.MAX_USERNAME:
            raise ValueError(f"El nombre de usuario no puede exceder {self.MAX_USERNAME} caracteres.")
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValueError("El nombre de usuario solo puede contener letras, números y guión bajo.")
        return username

    def _validate_password(self, password: str) -> str:
        if not password:
            raise ValueError("La contraseña es obligatoria.")
        if len(password) > self.MAX_PASSWORD:
            raise ValueError(f"La contraseña no puede exceder {self.MAX_PASSWORD} caracteres.")
        return password

    def _check_unique_username(self, username: str, exclude_id: Optional[int] = None):
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

    def create_usuario(self, username: str, password: str, nombre: str = "",
                       email: str = "", activo: int = 1) -> int:
        username = self._validate_username(username)
        password = self._validate_password(password)
        self._check_unique_username(username)

        conn = self._connect()
        try:
            cursor = conn.execute(
                """INSERT INTO usuarios (username, password, nombre, email, activo)
                   VALUES (?, ?, ?, ?, ?)""",
                (username, self._hash_password(password), nombre, email, activo)
            )
            conn.commit()
            logger.info(f"Usuario '{username}' creado (ID {cursor.lastrowid})")
            return cursor.lastrowid
        finally:
            conn.close()

    def get_usuario(self, id_user: int):
        conn = self._connect()
        try:
            return conn.execute(
                "SELECT * FROM usuarios WHERE id_user = ?", (id_user,)
            ).fetchone()
        finally:
            conn.close()

    def get_usuario_by_username(self, username: str):
        conn = self._connect()
        try:
            return conn.execute(
                "SELECT * FROM usuarios WHERE username = ?", (username,)
            ).fetchone()
        finally:
            conn.close()

    def get_all_usuarios(self):
        conn = self._connect()
        try:
            return conn.execute("""
                SELECT u.*, GROUP_CONCAT(r.nombre, ', ') as roles
                FROM usuarios u
                LEFT JOIN usuarios_roles ur ON u.id_user = ur.id_user
                LEFT JOIN roles r ON ur.id_rol = r.id_rol
                GROUP BY u.id_user
                ORDER BY u.username
            """).fetchall()
        finally:
            conn.close()

    def update_usuario(self, id_user: int, username: Optional[str] = None,
                       password: Optional[str] = None, nombre: Optional[str] = None,
                       email: Optional[str] = None, activo: Optional[int] = None):
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
                values.append(self._hash_password(password))

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
                return

            values.append(id_user)
            conn.execute(
                f"UPDATE usuarios SET {', '.join(fields)} WHERE id_user = ?",
                values
            )
            conn.commit()
            logger.info(f"Usuario ID {id_user} actualizado")
        finally:
            conn.close()

    def delete_usuario(self, id_user: int):
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
            logger.info(f"Usuario '{user['username']}' eliminado")
        finally:
            conn.close()

    def authenticate(self, username: str, password: str):
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM usuarios WHERE username = ? AND activo = 1",
                (username,)
            ).fetchone()
            if row and self._check_password(password, row["password"]):
                # Migrar contraseña a hash si estaba en texto plano
                if "$" not in row["password"]:
                    conn.execute(
                        "UPDATE usuarios SET password = ? WHERE id_user = ?",
                        (self._hash_password(password), row["id_user"])
                    )
                conn.execute(
                    "UPDATE usuarios SET ultimo_acceso = CURRENT_TIMESTAMP WHERE id_user = ?",
                    (row["id_user"],)
                )
                conn.commit()
                logger.info(f"Login exitoso: '{username}'")
                return row
            return None
        finally:
            conn.close()

    # ============================================================
    # ROLES
    # ============================================================

    def get_all_roles(self):
        conn = self._connect()
        try:
            return conn.execute("SELECT * FROM roles ORDER BY nivel DESC").fetchall()
        finally:
            conn.close()

    def get_roles_by_usuario(self, id_user: int):
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

    def set_usuario_roles(self, id_user: int, roles_ids: list):
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

    def create_rol(self, nombre: str, descripcion: str = "", nivel: int = 0):
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

    def check_constraints(self) -> list:
        conn = self._connect()
        try:
            dups = conn.execute("""
                SELECT username, COUNT(*) as cnt
                FROM usuarios
                GROUP BY username
                HAVING cnt > 1
            """).fetchall()
            return [dict(d) for d in dups]
        finally:
            conn.close()

    # ============================================================
    # INICIALIZACIÓN
    # ============================================================

    def ensure_defaults(self):
        from .schema import SCHEMA_SQL
        conn = self._connect()
        try:
            conn.executescript(SCHEMA_SQL)
            conn.commit()

            # Migrar contraseñas existentes de texto plano a hash
            rows = conn.execute(
                "SELECT id_user, username, password FROM usuarios WHERE password NOT LIKE '%$%'"
            ).fetchall()
            for row in rows:
                hashed = self._hash_password(row["password"])
                conn.execute(
                    "UPDATE usuarios SET password = ? WHERE id_user = ?",
                    (hashed, row["id_user"])
                )
            if rows:
                conn.commit()
                logger.info(f"Migradas {len(rows)} contraseñas a hash")
        finally:
            conn.close()
