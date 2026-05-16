"""Tab de Obras."""

from src.gui.widgets import CrudTableWidget


class ObrasTab(CrudTableWidget):

    TABLE_NAME = "obras"
    COLUMNS = [
        ("id", "ID"),
        ("codigo", "Código"),
        ("nombre", "Nombre"),
        ("id_cliente", "Cliente"),
        ("estado", "Estado"),
        ("moneda", "Moneda"),
        ("created_at", "Creado"),
    ]
    FORM_FIELDS = ["codigo", "nombre", "id_cliente", "direccion",
                   "coordenadas_utm", "dimension_area", "responsable",
                   "patente_prof", "estado", "moneda"]

    def __init__(self, db, parent=None):
        # Inyectamos nombre de cliente en COLUMNS
        self.COLUMNS = [
            ("id", "ID"),
            ("codigo", "Código"),
            ("nombre", "Nombre"),
            ("cliente_nombre", "Cliente"),
            ("estado", "Estado"),
            ("moneda", "Moneda"),
            ("created_at", "Creado"),
        ]
        super().__init__(db, parent)

    def load_data(self):
        query = """
            SELECT o.*, COALESCE(c.nombre, '') AS cliente_nombre
            FROM obras o
            LEFT JOIN clientes c ON o.id_cliente = c.id
            ORDER BY o.id DESC
        """
        cur = self.db.conn.execute(query)
        rows = [dict(r) for r in cur.fetchall()]
        self._populate_table(rows)
