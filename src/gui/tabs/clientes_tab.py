"""Tab de Clientes."""

from src.gui.widgets import CrudTableWidget


class ClientesTab(CrudTableWidget):

    TABLE_NAME = "clientes"
    COLUMNS = [
        ("id", "ID"),
        ("nombre", "Nombre"),
        ("ruc", "RUC"),
        ("telefono", "Teléfono"),
        ("email", "Email"),
    ]
    FORM_FIELDS = ["nombre", "ruc", "telefono", "email", "direccion"]
