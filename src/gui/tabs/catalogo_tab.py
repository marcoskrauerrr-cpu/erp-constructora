"""Tab de Catálogo — Rubros, SubRubros, Items, SubItems."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget, QDialog,
    QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QTextEdit,
)
from PySide6.QtCore import Qt
from src.gui.widgets import CrudTableWidget


class CatalogoTab(QWidget):
    """Tabs anidados: Rubros | SubRubros | Items | SubItems."""

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tabs.addTab(RubrosTab(db), "Rubros")
        self.tabs.addTab(SubRubrosTab(db), "SubRubros")
        self.tabs.addTab(ItemsTab(db), "Items")
        self.tabs.addTab(SubItemsTab(db), "SubItems")
        layout.addWidget(self.tabs)


class RubrosTab(CrudTableWidget):
    TABLE_NAME = "rubros"
    COLUMNS = [("id", "ID"), ("codigo", "Código"), ("nombre", "Nombre"), ("orden", "Orden")]
    FORM_FIELDS = ["codigo", "nombre", "descripcion", "orden"]

    def load_data(self):
        rows = self.db.fetch_all("rubros", "orden")
        self._populate_table(rows)


class SubRubrosTab(CrudTableWidget):
    TABLE_NAME = "subrubros"
    COLUMNS = [("id", "ID"), ("codigo", "Código"), ("nombre", "Nombre"), ("rubro_nombre", "Rubro Padre"), ("orden", "Orden")]
    FORM_FIELDS = ["codigo", "nombre", "descripcion", "id_rubro", "orden"]

    def load_data(self):
        query = """
            SELECT sr.*, COALESCE(r.nombre, '') AS rubro_nombre
            FROM subrubros sr
            LEFT JOIN rubros r ON sr.id_rubro = r.id
            ORDER BY sr.codigo
        """
        cur = self.db.conn.execute(query)
        rows = [dict(r) for r in cur.fetchall()]
        self._populate_table(rows)


class ItemsTab(CrudTableWidget):
    TABLE_NAME = "items"
    COLUMNS = [
        ("id", "ID"), ("codigo", "Código"), ("nombre", "Nombre"),
        ("unidad", "Unidad"), ("rubro_nombre", "Rubro"), ("subrubro_nombre", "SubRubro"),
    ]
    FORM_FIELDS = ["codigo", "nombre", "unidad", "id_rubro", "id_subrubro", "descripcion_ext"]

    def load_data(self):
        query = """
            SELECT i.*, COALESCE(r.nombre, '') AS rubro_nombre,
                   COALESCE(sr.nombre, '') AS subrubro_nombre
            FROM items i
            LEFT JOIN rubros r   ON i.id_rubro    = r.id
            LEFT JOIN subrubros sr ON i.id_subrubro = sr.id
            ORDER BY i.codigo
        """
        cur = self.db.conn.execute(query)
        rows = [dict(r) for r in cur.fetchall()]
        self._populate_table(rows)


class SubItemsTab(CrudTableWidget):
    TABLE_NAME = "subitems"
    COLUMNS = [
        ("id", "ID"), ("codigo", "Código"), ("nombre", "Nombre"),
        ("unidad", "Unidad"), ("item_nombre", "Item Padre"),
    ]
    FORM_FIELDS = ["codigo", "nombre", "unidad", "id_item", "descripcion_ext"]

    def load_data(self):
        query = """
            SELECT si.*, COALESCE(i.nombre, '') AS item_nombre
            FROM subitems si
            LEFT JOIN items i ON si.id_item = i.id
            ORDER BY si.codigo
        """
        cur = self.db.conn.execute(query)
        rows = [dict(r) for r in cur.fetchall()]
        self._populate_table(rows)
