"""Tab de Presupuesto — detalle de obra con cálculos."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QLabel, QComboBox,
    QSplitter, QFormLayout, QDoubleSpinBox, QDialog, QDialogButtonBox,
    QLineEdit, QFileDialog, QGroupBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class PresupuestoTab(QWidget):
    """Panel principal de presupuestos por obra."""

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.current_obra_id = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # ── Selector de obra ──
        top_bar = QHBoxLayout()
        lbl = QLabel("Obra:")
        lbl.setStyleSheet("color: #cdd6f4; font-size: 14px; font-weight: bold;")
        self.obra_combo = QComboBox()
        self.obra_combo.setMinimumWidth(350)
        self.obra_combo.setStyleSheet("""
            QComboBox { background-color: #313244; color: #cdd6f4;
                         border: 1px solid #45475a; border-radius: 4px;
                         padding: 6px; font-size: 13px; }
            QComboBox QAbstractItemView { background-color: #1e1e2e; color: #cdd6f4; }
        """)
        self.obra_combo.currentIndexChanged.connect(self._on_obra_changed)
        top_bar.addWidget(lbl)
        top_bar.addWidget(self.obra_combo, 1)

        self.btn_add_line = QPushButton("➕ Agregar Línea")
        self.btn_del_line = QPushButton("🗑️ Quitar Línea")
        self.btn_import_xlsx = QPushButton("📥 Importar Excel")
        for btn in (self.btn_add_line, self.btn_del_line, self.btn_import_xlsx):
            btn.setStyleSheet("padding: 6px 16px; font-size: 13px;")
            top_bar.addWidget(btn)
        layout.addLayout(top_bar)

        # ── Tabla de detalle ──
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Código", "Nombre", "Unidad", "Cantidad",
            "P.Unit.Mat", "P.Unit.MO", "Subtotal", ""
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e2e; alternate-background-color: #181825;
                color: #cdd6f4; gridline-color: #313244;
                font-size: 13px; border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #313244; color: #cdd6f4;
                padding: 8px; font-weight: bold; border: 1px solid #45475a;
            }
            QTableWidget::item:selected { background-color: #45475a; color: #cdd6f4; }
        """)
        layout.addWidget(self.table, 3)

        # ── Panel de resumen ──
        summary_group = QGroupBox("Resumen del Presupuesto")
        summary_group.setStyleSheet("""
            QGroupBox { color: #cdd6f4; font-size: 14px; font-weight: bold;
                        border: 1px solid #313244; border-radius: 6px;
                        margin-top: 10px; padding-top: 16px; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
        """)
        summary_layout = QVBoxLayout(summary_group)
        self.lbl_resumen = QLabel("Seleccione una obra para ver el resumen.")
        self.lbl_resumen.setStyleSheet("color: #a6adc8; font-size: 13px;")
        self.lbl_total = QLabel("")
        self.lbl_total.setStyleSheet("color: #a6e3a1; font-size: 18px; font-weight: bold;")
        summary_layout.addWidget(self.lbl_resumen)
        summary_layout.addWidget(self.lbl_total)
        layout.addWidget(summary_group, 1)

        # Conexiones
        self.btn_add_line.clicked.connect(self._on_add_line)
        self.btn_del_line.clicked.connect(self._on_del_line)
        self.btn_import_xlsx.clicked.connect(self._on_import_xlsx)

        self._load_obras()

    def _load_obras(self):
        self.obra_combo.blockSignals(True)
        self.obra_combo.clear()
        self.obra_combo.addItem("-- Seleccione una obra --", None)
        obras = self.db.fetch_all("obras", "id DESC")
        for o in obras:
            self.obra_combo.addItem(f"[{o['codigo']}] {o['nombre']}", o["id"])
        self.obra_combo.blockSignals(False)

    def _on_obra_changed(self, idx):
        self.current_obra_id = self.obra_combo.currentData()
        if self.current_obra_id:
            self._load_detalle()
            self._load_resumen()
        else:
            self.table.setRowCount(0)
            self.lbl_resumen.setText("Seleccione una obra para ver el resumen.")
            self.lbl_total.setText("")

    def _load_detalle(self):
        if not self.current_obra_id:
            return
        rows = self.db.get_detalle_obra(self.current_obra_id)
        self.table.setRowCount(0)
        for row_idx, row in enumerate(rows):
            self.table.insertRow(row_idx)
            items_data = [
                (0, row.get("codigo_item", "")),
                (1, row.get("nombre_item", "")),
                (2, row.get("unidad", "")),
                (3, f"{row['cantidad']:,.4f}" if row.get("cantidad") else "0"),
                (4, f"{row['precio_unit_mat']:,.2f}" if row.get("precio_unit_mat") else "0"),
                (5, f"{row['precio_unit_mo']:,.2f}" if row.get("precio_unit_mo") else "0"),
                (6, f"{row.get('subtotal', 0):,.2f}"),
            ]
            for col, val in items_data:
                item = QTableWidgetItem(val)
                item.setData(Qt.UserRole, row.get("id"))
                self.table.setItem(row_idx, col, item)
        self.table.resizeColumnsToContents()

    def _load_resumen(self):
        if not self.current_obra_id:
            return
        rubros = self.db.get_subtotales_por_rubro(self.current_obra_id)
        total = self.db.get_total_presupuesto(self.current_obra_id)

        moneda = "Gs."
        obra = self.db.fetch_one("obras", self.current_obra_id)
        if obra and obra.get("moneda") == "USD":
            moneda = "$"

        lines = []
        for r in rubros:
            lines.append(f"• {r['codigo']} {r['nombre']}: {moneda} {r['subtotal']:,.2f}")
        self.lbl_resumen.setText("\n".join(lines))
        self.lbl_total.setText(f"TOTAL: {moneda} {total:,.2f}")

    def _on_add_line(self):
        if not self.current_obra_id:
            QMessageBox.warning(self, "Atención", "Seleccione una obra primero.")
            return
        dlg = LineaDialog(self.db, self)
        if dlg.exec():
            data = dlg.get_data()
            data["id_obra"] = self.current_obra_id
            self.db.insert("presupuesto_detalle", data)
            self._load_detalle()
            self._load_resumen()

    def _on_del_line(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Seleccionar", "Seleccione una línea.")
            return
        id_detalle = self.table.item(row, 0).data(Qt.UserRole)
        reply = QMessageBox.question(self, "Confirmar", "¿Eliminar esta línea?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete("presupuesto_detalle", id_detalle)
            self._load_detalle()
            self._load_resumen()

    def _on_import_xlsx(self):
        """Importar desde Excel."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Excel", "", "Excel (*.xlsx *.xls)"
        )
        if not path:
            return
        QMessageBox.information(self, "Importar", f"Importando: {path}\n\n(Funcionalidad en desarrollo)")


class LineaDialog(QDialog):
    """Diálogo para agregar una línea al presupuesto detalle."""

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Agregar Línea al Presupuesto")
        self.setMinimumWidth(450)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e2e; }
            QLabel  { color: #cdd6f4; font-size: 13px; }
            QComboBox, QLineEdit, QDoubleSpinBox {
                background-color: #313244; color: #cdd6f4;
                border: 1px solid #45475a; border-radius: 4px;
                padding: 6px; font-size: 13px;
            }
        """)
        form = QFormLayout(self)

        # Tipo: Item o SubItem
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Item (N3)", "SubItem (N4)"])
        self.tipo_combo.currentIndexChanged.connect(self._on_tipo_changed)
        form.addRow("Tipo:", self.tipo_combo)

        # Selector de Item
        self.item_combo = QComboBox()
        items = db.fetch_all("items", "codigo")
        self.item_combo.addItem("-- Seleccionar --", None)
        for i in items:
            self.item_combo.addItem(f"{i['codigo']} - {i['nombre']}", i["id"])
        form.addRow("Item:", self.item_combo)

        # Selector de SubItem
        self.subitem_combo = QComboBox()
        subitems = db.fetch_all("subitems", "codigo")
        self.subitem_combo.addItem("-- Seleccionar --", None)
        for si in subitems:
            self.subitem_combo.addItem(f"{si['codigo']} - {si['nombre']}", si["id"])
        self.subitem_combo.setVisible(False)
        form.addRow("SubItem:", self.subitem_combo)

        # Cantidad
        self.cantidad_spin = QDoubleSpinBox()
        self.cantidad_spin.setDecimals(4)
        self.cantidad_spin.setMaximum(99999999.9999)
        self.cantidad_spin.setValue(1.0)
        form.addRow("Cantidad:", self.cantidad_spin)

        # Precios
        self.precio_mat_spin = QDoubleSpinBox()
        self.precio_mat_spin.setDecimals(2)
        self.precio_mat_spin.setMaximum(999999999.99)
        form.addRow("Precio Unit. Material:", self.precio_mat_spin)

        self.precio_mo_spin = QDoubleSpinBox()
        self.precio_mo_spin.setDecimals(2)
        self.precio_mo_spin.setMaximum(999999999.99)
        form.addRow("Precio Unit. Mano Obra:", self.precio_mo_spin)

        # Descripción de línea
        self.descripcion_linea = QLineEdit()
        form.addRow("Descripción (opcional):", self.descripcion_linea)

        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _on_tipo_changed(self, idx):
        is_subitem = idx == 1  # SubItem (N4)
        self.subitem_combo.setVisible(is_subitem)
        self.item_combo.setVisible(not is_subitem)

    def get_data(self) -> dict:
        is_subitem = self.tipo_combo.currentIndex() == 1
        data = {
            "cantidad": self.cantidad_spin.value(),
            "precio_unit_mat": self.precio_mat_spin.value(),
            "precio_unit_mo": self.precio_mo_spin.value(),
            "descripcion_linea": self.descripcion_linea.text(),
        }
        if is_subitem:
            data["id_subitem"] = self.subitem_combo.currentData()
            data["id_item"] = None
        else:
            data["id_item"] = self.item_combo.currentData()
            data["id_subitem"] = None
        return data
