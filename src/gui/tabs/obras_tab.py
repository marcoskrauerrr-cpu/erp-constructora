"""Tab de Obras — con campos completos para construcción."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QComboBox, QDoubleSpinBox, QDialogButtonBox, QLabel,
)
from PySide6.QtCore import Qt


class ObraFormDialog(QDialog):
    """Diálogo para crear/editar una obra."""

    def __init__(self, db, obra=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.obra = obra
        self.setWindowTitle("Nueva Obra" if obra is None else "Editar Obra")
        self.setMinimumWidth(550)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
            }
            QLabel {
                color: #e0e0f0;
                font-size: 13px;
                font-weight: 500;
            }
            QLineEdit, QComboBox, QDoubleSpinBox {
                background-color: #252545;
                color: #e0e0f0;
                border: 1px solid #3a3a6a;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #6c63ff;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a2e;
                color: #e0e0f0;
            }
        """)

        form = QFormLayout(self)
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        # Código
        self.txt_codigo = QLineEdit()
        self.txt_codigo.setPlaceholderText("Ej: LOGIPARK-2025")
        if obra:
            self.txt_codigo.setText(obra.get("codigo", ""))
        form.addRow("Código:", self.txt_codigo)

        # Nombre de la obra
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre del proyecto")
        if obra:
            self.txt_nombre.setText(obra.get("nombre", ""))
        form.addRow("Nombre:", self.txt_nombre)

        # Cliente
        self.cmb_cliente = QComboBox()
        self.cmb_cliente.addItem("-- Sin cliente --", None)
        for c in db.fetch_all("clientes", "nombre"):
            self.cmb_cliente.addItem(c["nombre"], c["id"])
        if obra and obra.get("id_cliente"):
            idx = self.cmb_cliente.findData(obra["id_cliente"])
            if idx >= 0:
                self.cmb_cliente.setCurrentIndex(idx)
        form.addRow("Cliente:", self.cmb_cliente)

        # Propietario / Responsable
        self.txt_propietario = QLineEdit()
        self.txt_propietario.setPlaceholderText("Nombre del propietario/responsable")
        if obra:
            self.txt_propietario.setText(obra.get("responsable", ""))
        form.addRow("Propietario/Resp.:", self.txt_propietario)

        # Dirección
        self.txt_direccion = QLineEdit()
        self.txt_direccion.setPlaceholderText("Ubicación de la obra")
        if obra:
            self.txt_direccion.setText(obra.get("direccion", ""))
        form.addRow("Dirección:", self.txt_direccion)

        # Área (M2)
        self.txt_area = QLineEdit()
        self.txt_area.setPlaceholderText("Ej: 434 m²")
        if obra:
            self.txt_area.setText(obra.get("dimension_area", ""))
        form.addRow("Área (M²):", self.txt_area)

        # Coordenadas UTM
        self.txt_utm = QLineEdit()
        self.txt_utm.setPlaceholderText("Ej: 21J 654321 7654321")
        if obra:
            self.txt_utm.setText(obra.get("coordenadas_utm", ""))
        form.addRow("Coordenadas UTM:", self.txt_utm)

        # Estado
        self.cmb_estado = QComboBox()
        estados = ["activo", "en_ejecucion", "finalizado", "cancelado"]
        self.cmb_estado.addItems(estados)
        if obra:
            idx = self.cmb_estado.findText(obra.get("estado", "activo"))
            if idx >= 0:
                self.cmb_estado.setCurrentIndex(idx)
        form.addRow("Estado:", self.cmb_estado)

        # Moneda
        self.cmb_moneda = QComboBox()
        self.cmb_moneda.addItems(["GS", "USD"])
        if obra:
            idx = self.cmb_moneda.findText(obra.get("moneda", "GS"))
            if idx >= 0:
                self.cmb_moneda.setCurrentIndex(idx)
        form.addRow("Moneda:", self.cmb_moneda)

        # Patente profesional
        self.txt_patente = QLineEdit()
        self.txt_patente.setPlaceholderText("N° de patente profesional")
        if obra:
            self.txt_patente.setText(obra.get("patente_prof", ""))
        form.addRow("Patente Prof.:", self.txt_patente)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_guardar = QPushButton("💾 Guardar")
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #6c63ff; color: #fff;
                border: none; border-radius: 8px;
                padding: 10px 30px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #7c73ff; }
        """)
        self.btn_guardar.clicked.connect(self._validate)
        btn_layout.addWidget(self.btn_guardar)

        self.btn_cancelar = QPushButton("❌ Cancelar")
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; color: #fff;
                border: none; border-radius: 8px;
                padding: 10px 30px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #ff5a4a; }
        """)
        self.btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancelar)

        form.addRow(btn_layout)

    def _validate(self):
        if not self.txt_codigo.text().strip():
            QMessageBox.warning(self, "Validación", "El código de la obra es obligatorio.")
            return
        if not self.txt_nombre.text().strip():
            QMessageBox.warning(self, "Validación", "El nombre de la obra es obligatorio.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "codigo": self.txt_codigo.text().strip(),
            "nombre": self.txt_nombre.text().strip(),
            "id_cliente": self.cmb_cliente.currentData(),
            "responsable": self.txt_propietario.text().strip(),
            "direccion": self.txt_direccion.text().strip(),
            "dimension_area": self.txt_area.text().strip(),
            "coordenadas_utm": self.txt_utm.text().strip(),
            "estado": self.cmb_estado.currentText(),
            "moneda": self.cmb_moneda.currentText(),
            "patente_prof": self.txt_patente.text().strip(),
        }


class ObrasTab(QWidget):
    """Tab de gestión de obras — versión profesional."""

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # Header
        header = QHBoxLayout()
        lbl_title = QLabel("📋 Gestión de Obras")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #6c63ff;")
        header.addWidget(lbl_title)
        header.addStretch()

        # Contador de obras
        self.lbl_count = QLabel("")
        self.lbl_count.setStyleSheet("color: #8888aa; font-size: 13px; padding-right: 12px;")
        header.addWidget(self.lbl_count)

        self.btn_new = QPushButton("➕ Nueva Obra")
        self.btn_new.setStyleSheet("padding: 8px 20px; font-size: 13px;")
        self.btn_new.clicked.connect(self._on_new)
        header.addWidget(self.btn_new)

        self.btn_edit = QPushButton("✏️ Editar")
        self.btn_edit.setStyleSheet("padding: 8px 20px; font-size: 13px;")
        self.btn_edit.clicked.connect(self._on_edit)
        header.addWidget(self.btn_edit)

        self.btn_delete = QPushButton("🗑️ Eliminar")
        self.btn_delete.setObjectName("btn_danger")
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; color: #fff;
                border: none; border-radius: 8px;
                padding: 8px 20px; font-size: 13px; font-weight: 600;
            }
            QPushButton:hover { background-color: #ff5a4a; }
        """)
        self.btn_delete.clicked.connect(self._on_delete)
        header.addWidget(self.btn_delete)

        layout.addLayout(header)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Cliente", "Propietario",
            "Área", "Estado", "Moneda", "Creado"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        # Doble click para editar
        self.table.doubleClicked.connect(self._on_edit)

        self.load_data()

    def load_data(self):
        query = """
            SELECT o.*, COALESCE(c.nombre, '') AS cliente_nombre
            FROM obras o
            LEFT JOIN clientes c ON o.id_cliente = c.id
            ORDER BY o.id DESC
        """
        cur = self.db.conn.execute(query)
        rows = [dict(r) for r in cur.fetchall()]

        self.table.setRowCount(0)
        for row_idx, row in enumerate(rows):
            self.table.insertRow(row_idx)

            fields = [
                ("id", str(row["id"])),
                ("codigo", row["codigo"]),
                ("nombre", row["nombre"]),
                ("cliente_nombre", row["cliente_nombre"]),
                ("responsable", row.get("responsable", "")),
                ("dimension_area", row.get("dimension_area", "")),
                ("estado", row["estado"]),
                ("moneda", row["moneda"]),
            ]
            for col, val in fields:
                item = QTableWidgetItem(val)
                item.setData(Qt.UserRole, row["id"])
                self.table.setItem(row_idx, col, item)

            # Fecha
            item = QTableWidgetItem(row.get("created_at", ""))
            item.setData(Qt.UserRole, row["id"])
            self.table.setItem(row_idx, 8, item)

        self.table.resizeColumnsToContents()
        self.lbl_count.setText(f"Total: {len(rows)} obras")

    def _get_selected_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Seleccionar", "Seleccione una obra primero.")
            return None
        return self.table.item(row, 0).data(Qt.UserRole)

    def _on_new(self):
        dlg = ObraFormDialog(self.db, parent=self)
        if dlg.exec():
            data = dlg.get_data()
            self.db.insert("obras", data)
            self.load_data()

    def _on_edit(self):
        id_val = self._get_selected_id()
        if not id_val:
            return
        obra = self.db.fetch_one("obras", id_val)
        if not obra:
            return
        dlg = ObraFormDialog(self.db, obra=obra, parent=self)
        if dlg.exec():
            data = dlg.get_data()
            self.db.update("obras", id_val, data)
            self.load_data()

    def _on_delete(self):
        id_val = self._get_selected_id()
        if not id_val:
            return
        obra = self.db.fetch_one("obras", id_val)
        reply = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Eliminar la obra '{obra['nombre']}'?\n\n"
            "Se eliminarán también todos los datos asociados (presupuestos, etc.)",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            # Eliminar datos relacionados
            self.db.conn.execute("DELETE FROM presupuesto_detalle WHERE id_obra = ?", (id_val,))
            self.db.conn.execute("DELETE FROM obras WHERE id = ?", (id_val,))
            self.db.conn.commit()
            self.load_data()
