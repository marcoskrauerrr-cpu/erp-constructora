"""
Schema SQLite - Módulo Usuarios y Roles
ERP Constructora - Diseño futurista
"""

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ============================================================
-- ROLES
-- ============================================================
CREATE TABLE IF NOT EXISTS roles (
    id_rol      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      VARCHAR(50)  NOT NULL UNIQUE,
    descripcion VARCHAR(200),
    nivel       INTEGER      NOT NULL DEFAULT 0
        CHECK (nivel BETWEEN 0 AND 100),
    created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- USUARIOS
-- - username: único, máx 20 caracteres
-- - password: máx 20 caracteres (para esta versión)
-- ============================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id_user     INTEGER PRIMARY KEY AUTOINCREMENT,
    username    VARCHAR(20)  NOT NULL UNIQUE,
    password    VARCHAR(20)  NOT NULL,
    nombre      VARCHAR(100),
    email       VARCHAR(100),
    activo      INTEGER      NOT NULL DEFAULT 1
        CHECK (activo IN (0, 1)),
    ultimo_acceso TIMESTAMP,
    created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índice único para búsqueda rápida
CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);

-- ============================================================
-- USUARIOS_ROLES (relación muchos a muchos)
-- ============================================================
CREATE TABLE IF NOT EXISTS usuarios_roles (
    id_user     INTEGER NOT NULL,
    id_rol      INTEGER NOT NULL,
    PRIMARY KEY (id_user, id_rol),
    FOREIGN KEY (id_user) REFERENCES usuarios(id_user) ON DELETE CASCADE,
    FOREIGN KEY (id_rol)  REFERENCES roles(id_rol)     ON DELETE CASCADE
);

-- ============================================================
-- Datos por defecto
-- ============================================================
-- Roles base
INSERT OR IGNORE INTO roles (nombre, descripcion, nivel) VALUES
    ('Administrador',   'Acceso total al sistema. Gestiona usuarios, roles y configuración.', 100),
    ('Gerente',         'Visión general de obras, reportes y aprobación de presupuestos.',      80),
    ('Supervisor',      'Gestiona obras, asigna tareas y supervisa avance.',                    60),
    ('Operador',        'Carga datos, registra avance de obra y emite comprobantes.',           40),
    ('Lector',          'Solo consulta informes y presupuestos, sin modificar.',                 20),
    ('Auditor',         'Acceso de solo lectura con trazabilidad de cambios.',                   10);

-- Usuario admin por defecto
INSERT OR IGNORE INTO usuarios (id_user, username, password, nombre, activo) VALUES
    (1, 'admin', 'admin', 'Administrador del Sistema', 1);

-- Asignar rol Admin al usuario admin
INSERT OR IGNORE INTO usuarios_roles (id_user, id_rol) VALUES
    (1, (SELECT id_rol FROM roles WHERE nombre = 'Administrador'));
"""


def init_database(db_path):
    """Inicializa la base de datos con el schema."""
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
    return db_path
