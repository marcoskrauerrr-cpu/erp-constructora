# 🏗️ ERP Constructora

Sistema de Gestión para Empresas Constructoras — modular, escalable, código abierto.

## Arquitectura

```
erp-constructora/
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias Python
├── build.bat               # Build para Windows (.exe)
├── src/
│   ├── database/
│   │   ├── schema.py       # DDL — 4 niveles jerárquicos
│   │   └── repository.py   # Capa de datos (CRUD + consultas)
│   └── gui/
│       ├── widgets.py      # Widgets base reutilizables
│       └── tabs/
│           ├── obras_tab.py
│           ├── clientes_tab.py
│           ├── catalogo_tab.py
│           └── presupuesto_tab.py
└── data/                   # Base de datos SQLite (auto-creada)
```

## Jerarquía del Presupuesto

```
N1 — Rubro:       1.00,  2.00,  3.00...
N2 — SubRubro:    1.01,  2.01,  8.01...
N3 — Item:        1.01.01,  2.01.02,  8.01.01...
N4 — SubItem:     1.01.01.01,  8.01.01.01...
```

Cada línea en el detalle tiene: **Cantidad × (Precio Material + Precio Mano de Obra)**

## Requisitos

- Python 3.11 o superior
- Windows, Linux o macOS

## Instalación y ejecución

```bash
# 1. Clonar
git clone <repo-url>
cd erp-constructora

# 2. Crear entorno virtual
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
python main.py
```

## Build para Windows (.exe)

```bash
build.bat
# Genera: dist/ERP Constructora.exe
```

## Módulos

| Módulo | Estado |
|--------|--------|
| Obras (CRUD) | ✅ Implementado |
| Clientes (CRUD) | ✅ Implementado |
| Catálogo (Rubros, SubRubros, Items, SubItems) | ✅ Implementado |
| Presupuesto Detalle | ✅ Implementado |
| Cálculos (subtotales por rubro + total) | ✅ Implementado |
| Importación Excel | 🔜 Próximo |
| Órdenes de Compra | 🔜 Próximo |
| Avance de Obra | 🔜 Próximo |
