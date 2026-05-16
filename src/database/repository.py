"""Repositorio de base de datos — capa de acceso a datos."""

import sqlite3
from pathlib import Path
from typing import Any

from src.database.schema import init_database


class Database:
    """Maneja la conexión y operaciones básicas de BD."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.conn: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        """Abre conexión e inicializa esquema si es primera vez."""
        if self.conn is None:
            self.conn = init_database(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    # ── Genéricos CRUD ──────────────────────────────────────────────────────

    def fetch_all(self, table: str, order_by: str = "id") -> list[dict]:
        cur = self.conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}")
        return [dict(r) for r in cur.fetchall()]

    def fetch_one(self, table: str, id_val: int) -> dict | None:
        cur = self.conn.execute(f"SELECT * FROM {table} WHERE id = ?", (id_val,))
        row = cur.fetchone()
        return dict(row) if row else None

    def insert(self, table: str, data: dict) -> int:
        cols = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data)
        cur = self.conn.execute(
            f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",
            tuple(data.values()),
        )
        self.conn.commit()
        return cur.lastrowid

    def update(self, table: str, id_val: int, data: dict):
        data["updated_at"] = data.get("updated_at", "datetime('now','localtime')")
        sets = ", ".join(f"{k} = ?" for k in data)
        self.conn.execute(
            f"UPDATE {table} SET {sets} WHERE id = ?",
            tuple(data.values()) + (id_val,),
        )
        self.conn.commit()

    def delete(self, table: str, id_val: int):
        self.conn.execute(f"DELETE FROM {table} WHERE id = ?", (id_val,))
        self.conn.commit()

    # ── Consultas de Presupuesto ────────────────────────────────────────────

    def get_detalle_obra(self, id_obra: int) -> list[dict]:
        """Retorna todas las líneas del detalle con códigos y nombres."""
        query = """
            SELECT
                pd.id,
                pd.id_item,
                pd.id_subitem,
                pd.cantidad,
                pd.precio_unit_mat,
                pd.precio_unit_mo,
                pd.descripcion_linea,
                (pd.cantidad * (pd.precio_unit_mat + pd.precio_unit_mo)) AS subtotal,
                COALESCE(i.codigo, si.codigo) AS codigo_item,
                COALESCE(i.nombre, si.nombre) AS nombre_item,
                COALESCE(i.unidad, si.unidad) AS unidad,
                COALESCE(i.id_rubro, sii.id_rubro) AS id_rubro,
                COALESCE(i.id_subrubro, sii.id_subrubro) AS id_subrubro
            FROM presupuesto_detalle pd
            LEFT JOIN items i     ON pd.id_item    = i.id
            LEFT JOIN subitems si ON pd.id_subitem = si.id
            LEFT JOIN items sii   ON si.id_item    = sii.id
            WHERE pd.id_obra = ?
            ORDER BY codigo_item
        """
        cur = self.conn.execute(query, (id_obra,))
        return [dict(r) for r in cur.fetchall()]

    def get_subtotales_por_rubro(self, id_obra: int) -> list[dict]:
        query = """
            SELECT
                r.id,
                r.codigo,
                r.nombre,
                ROUND(SUM(pd.cantidad * (pd.precio_unit_mat + pd.precio_unit_mo)), 2) AS subtotal,
                COUNT(pd.id) AS items_count
            FROM presupuesto_detalle pd
            LEFT JOIN items i       ON pd.id_item    = i.id
            LEFT JOIN subitems si   ON pd.id_subitem = si.id
            LEFT JOIN items sii     ON si.id_item    = sii.id
            JOIN rubros r           ON r.id = COALESCE(i.id_rubro, sii.id_rubro)
            WHERE pd.id_obra = ?
            GROUP BY r.id, r.codigo, r.nombre
            ORDER BY r.orden
        """
        cur = self.conn.execute(query, (id_obra,))
        return [dict(r) for r in cur.fetchall()]

    def get_subtotales_por_subrubro(self, id_obra: int) -> list[dict]:
        query = """
            SELECT
                sr.id,
                sr.codigo,
                sr.nombre,
                ROUND(SUM(pd.cantidad * (pd.precio_unit_mat + pd.precio_unit_mo)), 2) AS subtotal,
                COUNT(pd.id) AS items_count
            FROM presupuesto_detalle pd
            LEFT JOIN items i       ON pd.id_item    = i.id
            LEFT JOIN subitems si   ON pd.id_subitem = si.id
            LEFT JOIN items sii     ON si.id_item    = sii.id
            JOIN subrubros sr       ON sr.id = COALESCE(i.id_subrubro, sii.id_subrubro)
            WHERE pd.id_obra = ?
            GROUP BY sr.id, sr.codigo, sr.nombre
            ORDER BY sr.codigo
        """
        cur = self.conn.execute(query, (id_obra,))
        return [dict(r) for r in cur.fetchall()]

    def get_total_presupuesto(self, id_obra: int) -> float:
        cur = self.conn.execute(
            "SELECT ROUND(SUM(cantidad * (precio_unit_mat + precio_unit_mo)), 2) "
            "FROM presupuesto_detalle WHERE id_obra = ?",
            (id_obra,),
        )
        return cur.fetchone()[0] or 0.0
