# ERP Constructora

Sistema de gestión empresarial para constructoras. Escritorio (Windows/Linux/macOS).

## Estado Actual

**v1.1.0** — Módulo de Usuarios y Roles implementado.

### ✅ Implementado
- Login con autenticación (admin / admin)
- CRUD completo de usuarios
- 6 roles jerárquicos (Administrador → Auditor)
- Asignación múltiple de roles por usuario
- Diseño corporativo oscuro premium
- Base de datos SQLite con constraints
- Validaciones: username único, máx 20 chars, password máx 20 chars
- Core Launcher para futuros módulos
- Logging de eventos
- Build .exe para Windows

### 🔄 En desarrollo
- Próximos módulos (Presupuestos, Obras, etc.)

## Requisitos

- Python 3.11+
- Windows, Linux o macOS

## Instalación

```bash
git clone https://github.com/marcoskrauerrr-cpu/erp-constructora.git
cd erp-constructora
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

## Credenciales por defecto

- **Usuario:** `admin`
- **Contraseña:** `admin`

## Roles del sistema

| Rol | Nivel | Descripción |
|-----|-------|-------------|
| Administrador | 100 | Acceso total al sistema |
| Gerente | 80 | Reportes y aprobación de presupuestos |
| Supervisor | 60 | Gestión de obras y asignación de tareas |
| Operador | 40 | Carga de datos y registro de avance |
| Lector | 20 | Solo consulta de informes |
| Auditor | 10 | Solo lectura con trazabilidad |

## Build para Windows (.exe)

```bash
build.bat
```

El ejecutable se genera en `dist\ERP Constructora\ERP Constructora.exe`.

## Estructura del proyecto

```
erp-constructora/
├── main.py                       # Entry point
├── requirements.txt              # Dependencias
├── build.bat                     # Build Windows
├── data/
│   └── erp_constructora.db       # Base de datos SQLite
└── src/
    ├── core/
    │   └── launcher.py           # Core Launcher (gestor de módulos)
    ├── database/
    │   ├── schema.py             # DDL de la base de datos
    │   └── repository.py         # CRUD con validaciones
    ├── gui/
    │   ├── login.py              # Pantalla de login
    │   ├── admin_panel.py        # CRUD de usuarios y roles
    │   └── styles/
    │       └── futuristic_style.py  # Tema oscuro corporativo
    └── __init__.py
```

## Tecnologías

- Python 3.11+
- PySide6 (Qt for Python)
- SQLite
- PyInstaller (build .exe)
