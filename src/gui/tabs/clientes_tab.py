"""Tab de Clientes."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QDialogButtonBox, QLabel,
)
from PySide6.QtCore import Qt


class ClienteFormDialog(QDialog):
    def __init__(self, db, cliente=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.cliente = cliente
        self.setWindowTitle("Nuevo Cliente" if cliente is None else "Editar Cliente")
        self.setMinimumWidth(450)
        self.setStyleSheet("""
            QDialog { background-color: #1a1a2e; }
            QLabel { color: #e0e0f0; font-size: 13px; font-weight: 500; }
            QLineEdit {
                background-color: #252545; color: #e0e0f0;
                border: 1px solid #3a3a6a; border-radius: 6px;
                padding: 8px; font-size: 13px;
            }
            QLineEdit:focus { border: 2px solid #6c63ff; }
        """)

        form = QFormLayout(self)
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre completo o razón social")
        if cliente:
            self.txt_nombre.setText(cliente.get("nombre", ""))
        form.addRow("Nombre:", self.txt_nombre)

        self.txt_ruc = QLineEdit()
        self.txt_ruc.setPlaceholderText("N° de RUC")
        if cliente:
            self.txt_ruc.setText(cliente.get("ruc", ""))
        form.addRow("RUC:", self.txt_ruc)

        self.txt_telefono = QLineEdit()
        self.txt_telefono.setPlaceholderText("Teléfono/Celular")
        if cliente:
            self.txt_telefono.setText(cliente.get("telefono", ""))
        form.addRow("Teléfono:", self.txt_telefono)

        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("correo@ejemplo.com")
        if cliente:
            self.txt_email.setText(cliente.get("email", ""))
        form.addRow("Email:", self.txt_email)

        self.txt_direccion = QLineEdit()
        self.txt_direccion.setPlaceholderText("Dirección fiscal")
        if cliente:
            self.txt_direccion.setText(cliente.get("direccion", ""))
        form.addRow("Dirección:", self.txt_direccion)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_guardar = QPushButton("💾 Guardar")
        self.btn_guardar.setStyleSheet("""
            QPushButton { background-color: #6c63ff; color: #fff;
                border: none; border-radius: 8px;
                padding: 10px 30px; font-size: 13px; font-weight: bold; }
            QPushButton:hover { background-color: #7c73ff; }
        """)
        self.btn_guardar.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_guardar)

        self.btn_cancelar = QPushButton("❌ Cancelar")
        self.btn_cancelar.setStyleSheet("""
            QPushButton { background-color: #e74c3c; color: #fff;
                border: none; border-radius: 8px;
                padding: 10px 30px; font-size: 13px; font-weight: bold; }
            QPushButton:hover { background-color: #ff5a4a; }
        """)
        self.btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancelar)
        form.addRow(btn_layout)

    def get_data(self) -> dict:
        return {
            "nombre": self.txt_nombre.text().strip(),
            "ruc": self.txt_ruc.text().strip(),
            "telefono": self.txt_telefono.text().strip(),
            "email": self.txt_email.text().strip(),
            "direccion": self.txt_direccion.text().strip(),
        }


class ClientesTab(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        header = QHBoxLayout()
        lbl_title = QLabel("👥 Gestión de Clientes")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #6c63ff;")
        header.addWidget(lbl_title)
        header.addStretch()

        self.lbl_count = QLabel("")
        self.lbl_count.setStyleSheet("color: #8888aa; font-size: 13px; padding-right: 12px;")
        header.addWidget(self.lbl_count)

        self.btn_new = QPushButton("➕ Nuevo Cliente")
        self.btn_new.clicked.connect(self._on_new)
        header.addWidget(self.btn_new)
        self.btn_edit = QPushButton("✏️ Editar")
        self.btn_edit.clicked.connect(self._on_edit)
        header.addWidget(self.btn_edit)
        self.btn_delete = QPushButton("🗑️ Eliminar")
        self.btn_delete.setObjectName("btn_danger")
        self.btn_delete.setStyleSheet("""
            QPushButton { background-color: #e74c3c; color: #fff;
                border: none; border-radius: 8px;
                padding: 8px 20px; font-size: 13px; font-weight: 600; }
            QPushButton:hover { background-color: #ff5a4a; }
        """)
        self.btn_delete.clicked.connect(self._on_delete)
        header.addWidget(self.btn_delete)
        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "RUC", "Teléfono", "Email", "Dirección"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        self.table.doubleClicked.connect(self._on_edit)

        self.load_data()

    def load_data(self):
        rows = self.db.fetch_all("clientes", "nombre")
        self.table.setRowCount(0)
        for row_idx, row in enumerate(rows):
            self.table.insertRow(row_idx)
            for col, field in enumerate(["id", "nombre", "ruc", "telefono", "email", "direccion"]):
                val = row.get(field, "")
                item = QTableWidgetItem(str(val) if val else "")
                item.setData(Qt.UserRole, row["id"])
                self.table.setItem(row_idx, col, item)
        self.table.resizeColumnsToContents()
        self.lbl_count.setText(f"Total: {len(rows)} clientes")

    def _get_selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Seleccionar", "Seleccione un cliente primero.")
            return None
        return self.table.item(row, 0).data(Qt.UserRole)

    def _on_new(self):
        dlg = ClienteFormDialog(self.db, parent=self)
        if dlg.exec():
            self.db.insert("clientes", dlg.get_data())
            self.load_data()

    def _on_edit(self):
        id_val = self._get_selected_id()
        if not id_val:
            return
        c = self.db.fetch_one("clientes", id_val)
        if not c:
            return
        dlg = ClienteFormDialog(self.db, cliente=c, parent=self)
        if dlg.exec():
            self.db.update("clientes", id_val, dlg.get_data())
            self.load_data()

    def _on_delete(self):
        id_val = self._get_selected_id()
        if not id_val:
            return
        c = self.db.fetch_one("clientes", id_val)
        reply = QMessageBox.question(
            self, "Confirmar", f"¿Eliminar cliente '{c['nombre']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete("clientes", id_val)
            self.load_data()
