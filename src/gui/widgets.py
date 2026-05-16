"""Widget base reutilizable con tabla y botones CRUD."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QDialogButtonBox, QComboBox, QLabel, QDateEdit, QDoubleSpinBox,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont


class CrudTableWidget(QWidget):
    """Widget genérico con tabla + botones Nuevo, Editar, Eliminar."""

    TABLE_NAME = ""       # override en subclases
    COLUMNS = []          # [ (field_name, header_text), ... ]
    # Campos editables en el diálogo (por defecto todos menos id y fechas)
    FORM_FIELDS = []

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()
        self.btn_new = QPushButton("➕ Nuevo")
        self.btn_edit = QPushButton("✏️ Editar")
        self.btn_delete = QPushButton("🗑️ Eliminar")
        self.btn_refresh = QPushButton("🔄 Refrescar")
        for btn in (self.btn_new, self.btn_edit, self.btn_delete, self.btn_refresh):
            btn.setStyleSheet("padding: 6px 16px; font-size: 13px;")
            toolbar.addWidget(btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels([h for _, h in self.COLUMNS])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e2e;
                alternate-background-color: #181825;
                color: #cdd6f4;
                gridline-color: #313244;
                font-size: 13px;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #313244;
                color: #cdd6f4;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #45475a;
            }
            QTableWidget::item:selected {
                background-color: #45475a;
                color: #cdd6f4;
            }
        """)
        layout.addWidget(self.table)

        # Conexiones
        self.btn_new.clicked.connect(self._on_new)
        self.btn_edit.clicked.connect(self._on_edit)
        self.btn_delete.clicked.connect(self._on_delete)
        self.btn_refresh.clicked.connect(self.load_data)
        self.table.doubleClicked.connect(self._on_edit)

        self.load_data()

    def load_data(self):
        """Carga datos desde la BD. Override para consultas custom."""
        if not self.TABLE_NAME:
            return
        rows = self.db.fetch_all(self.TABLE_NAME)
        self._populate_table(rows)

    def _populate_table(self, rows: list[dict]):
        self.table.setRowCount(0)
        field_names = [f for f, _ in self.COLUMNS]
        for row_idx, row in enumerate(rows):
            self.table.insertRow(row_idx)
            for col_idx, field in enumerate(field_names):
                val = row.get(field, "")
                item = QTableWidgetItem(str(val) if val is not None else "")
                item.setData(Qt.UserRole, row.get("id"))
                self.table.setItem(row_idx, col_idx, item)
        self.table.resizeColumnsToContents()

    def _get_selected_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Seleccionar", "Seleccione un registro primero.")
            return None
        return self.table.item(row, 0).data(Qt.UserRole)

    def _on_new(self):
        dlg = self._create_form_dialog("Nuevo", None)
        if dlg.exec():
            data = self._form_to_dict(dlg)
            data.pop("id", None)
            self.db.insert(self.TABLE_NAME, data)
            self.load_data()

    def _on_edit(self):
        id_val = self._get_selected_id()
        if not id_val:
            return
        record = self.db.fetch_one(self.TABLE_NAME, id_val)
        if not record:
            return
        dlg = self._create_form_dialog("Editar", record)
        if dlg.exec():
            data = self._form_to_dict(dlg)
            data.pop("id", None)
            self.db.update(self.TABLE_NAME, id_val, data)
            self.load_data()

    def _on_delete(self):
        id_val = self._get_selected_id()
        if not id_val:
            return
        reply = QMessageBox.question(
            self, "Confirmar", "¿Eliminar este registro?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete(self.TABLE_NAME, id_val)
            self.load_data()

    def _create_form_dialog(self, title: str, record: dict | None) -> QDialog:
        """Crea un QDialog con campos del formulario."""
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.setMinimumWidth(400)
        dlg.setStyleSheet("""
            QDialog { background-color: #1e1e2e; }
            QLabel  { color: #cdd6f4; font-size: 13px; }
            QLineEdit, QComboBox { 
                background-color: #313244; color: #cdd6f4; 
                border: 1px solid #45475a; border-radius: 4px; 
                padding: 6px; font-size: 13px;
            }
            QDoubleSpinBox, QDateEdit {
                background-color: #313244; color: #cdd6f4;
                border: 1px solid #45475a; border-radius: 4px;
                padding: 6px; font-size: 13px;
            }
        """)
        form = QFormLayout(dlg)

        # Determinar campos del formulario
        fields = self.FORM_FIELDS or [f for f, _ in self.COLUMNS if f not in ("id", "created_at", "updated_at")]

        self._form_widgets = {}
        for field in fields:
            if field.endswith("_id"):
                # ComboBox para FKs
                combo = QComboBox()
                ref_table = field.replace("_id", "s")
                try:
                    refs = self.db.fetch_all(ref_table)
                    combo.addItem("-- Seleccionar --", None)
                    for r in refs:
                        combo.addItem(f"{r.get('codigo','')} - {r.get('nombre','')}", r["id"])
                except Exception:
                    combo.addItem("-- Sin datos --", None)
                if record and record.get(field):
                    idx = combo.findData(record[field])
                    if idx >= 0:
                        combo.setCurrentIndex(idx)
                form.addRow(field.replace("_", " ").title(), combo)
                self._form_widgets[field] = combo
            elif "fecha" in field.lower():
                de = QDateEdit()
                de.setCalendarPopup(True)
                de.setDate(QDate.currentDate())
                if record and record.get(field):
                    try:
                        de.setDate(QDate.fromString(record[field], "yyyy-MM-dd"))
                    except Exception:
                        pass
                form.addRow(field.replace("_", " ").title(), de)
                self._form_widgets[field] = de
            elif field in ("cantidad",):
                sp = QDoubleSpinBox()
                sp.setDecimals(4)
                sp.setMaximum(99999999.9999)
                if record:
                    sp.setValue(float(record.get(field, 0)))
                form.addRow(field.replace("_", " ").title(), sp)
                self._form_widgets[field] = sp
            elif "precio" in field.lower() or "monto" in field.lower():
                sp = QDoubleSpinBox()
                sp.setDecimals(2)
                sp.setMaximum(999999999.99)
                if record:
                    sp.setValue(float(record.get(field, 0)))
                form.addRow(field.replace("_", " ").title(), sp)
                self._form_widgets[field] = sp
            else:
                le = QLineEdit()
                if record and record.get(field):
                    le.setText(str(record[field]))
                form.addRow(field.replace("_", " ").title(), le)
                self._form_widgets[field] = le

        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        form.addRow(buttons)

        return dlg

    def _form_to_dict(self, dlg: QDialog) -> dict:
        data = {}
        for field, widget in self._form_widgets.items():
            if isinstance(widget, QLineEdit):
                data[field] = widget.text()
            elif isinstance(widget, QComboBox):
                data[field] = widget.currentData()
            elif isinstance(widget, QDoubleSpinBox):
                data[field] = widget.value()
            elif isinstance(widget, QDateEdit):
                data[field] = widget.date().toString("yyyy-MM-dd")
        return data
