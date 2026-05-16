"""Esquema DDL del ERP Constructora — 4 niveles jerárquicos."""

import sqlite3
from pathlib import Path

SCHEMA_SQL = """
-- ============================================================
-- Clientes
-- ============================================================
CREATE TABLE IF NOT EXISTS clientes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT    NOT NULL,
    ruc         TEXT,
    telefono    TEXT,
    email       TEXT,
    direccion   TEXT,
    created_at  TEXT    DEFAULT (datetime('now','localtime')),
    updated_at  TEXT    DEFAULT (datetime('now','localtime'))
);

-- ============================================================
-- Obras
-- ============================================================
CREATE TABLE IF NOT EXISTS obras (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo          TEXT    NOT NULL UNIQUE,
    nombre          TEXT    NOT NULL,
    id_cliente      INTEGER REFERENCES clientes(id),
    direccion       TEXT,
    coordenadas_utm TEXT,
    dimension_area  TEXT,
    responsable     TEXT,
    patente_prof    TEXT,
    estado          TEXT    NOT NULL DEFAULT 'activo'
                    CHECK (estado IN ('activo','en_ejecucion','finalizado','cancelado')),
    moneda          TEXT    NOT NULL DEFAULT 'GS'
                    CHECK (moneda IN ('GS','USD')),
    created_at      TEXT    DEFAULT (datetime('now','localtime')),
    updated_at      TEXT    DEFAULT (datetime('now','localtime'))
);

-- ============================================================
-- Rubros (N1: 1.00, 2.00, 3.00...)
-- ============================================================
CREATE TABLE IF NOT EXISTS rubros (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo      TEXT    NOT NULL UNIQUE,
    nombre      TEXT    NOT NULL,
    descripcion TEXT,
    orden       INTEGER NOT NULL DEFAULT 0
);

-- ============================================================
-- SubRubros (N2: 1.01, 2.01, 8.01...)
-- ============================================================
CREATE TABLE IF NOT EXISTS subrubros (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo      TEXT    NOT NULL,
    nombre      TEXT    NOT NULL,
    descripcion TEXT,
    id_rubro    INTEGER NOT NULL REFERENCES rubros(id),
    orden       INTEGER NOT NULL DEFAULT 0,
    UNIQUE(codigo, id_rubro)
);

-- ============================================================
-- Items (N3: 1.01.01, 2.01.02, 8.01.01...)
-- ============================================================
CREATE TABLE IF NOT EXISTS items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo          TEXT    NOT NULL UNIQUE,
    nombre          TEXT    NOT NULL,
    unidad          TEXT    NOT NULL DEFAULT 'un'
                    CHECK (unidad IN ('m2','m3','m²','m³','kg','glb','ml','un','unid.','m','lt','h')),
    id_subrubro     INTEGER REFERENCES subrubros(id),
    id_rubro        INTEGER NOT NULL REFERENCES rubros(id),
    descripcion_ext TEXT,
    created_at      TEXT    DEFAULT (datetime('now','localtime'))
);

-- ============================================================
-- SubItems (N4: 1.01.01.01, 8.01.01.01...)
-- ============================================================
CREATE TABLE IF NOT EXISTS subitems (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo          TEXT    NOT NULL UNIQUE,
    nombre          TEXT    NOT NULL,
    unidad          TEXT    NOT NULL DEFAULT 'un'
                    CHECK (unidad IN ('m2','m3','m²','m³','kg','glb','ml','un','unid.','m','lt','h')),
    id_item         INTEGER NOT NULL REFERENCES items(id),
    descripcion_ext TEXT,
    created_at      TEXT    DEFAULT (datetime('now','localtime'))
);

-- ============================================================
-- Presupuesto_Detalle (Tabla transaccional)
-- ============================================================
CREATE TABLE IF NOT EXISTS presupuesto_detalle (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    id_obra             INTEGER NOT NULL REFERENCES obras(id),
    id_item             INTEGER REFERENCES items(id),
    id_subitem          INTEGER REFERENCES subitems(id),
    cantidad            REAL    NOT NULL DEFAULT 1.0
                            CHECK (cantidad > 0),
    precio_unit_mat     REAL    NOT NULL DEFAULT 0.0
                            CHECK (precio_unit_mat >= 0),
    precio_unit_mo      REAL    NOT NULL DEFAULT 0.0
                            CHECK (precio_unit_mo >= 0),
    descripcion_linea   TEXT,
    created_at          TEXT    DEFAULT (datetime('now','localtime')),
    updated_at          TEXT    DEFAULT (datetime('now','localtime')),
    CHECK (
        (id_item IS NOT NULL AND id_subitem IS NULL) OR
        (id_item IS NULL AND id_subitem IS NOT NULL)
    )
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_detalle_obra    ON presupuesto_detalle(id_obra);
CREATE INDEX IF NOT EXISTS idx_items_rubro     ON items(id_rubro);
CREATE INDEX IF NOT EXISTS idx_items_subrubro  ON items(id_subrubro);
CREATE INDEX IF NOT EXISTS idx_subitems_item   ON subitems(id_item);
"""


def init_database(db_path: str | Path) -> sqlite3.Connection:
    """Inicializa BD y crea tablas si no existen. Retorna conexión."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn
