"""
Launcher del Core - Punto de conexión entre módulo Usuarios y futuros módulos
"""

import os


class CoreLauncher:
    """
    Puente entre el módulo de Usuarios/Roles y el resto de módulos del ERP.
    Cada módulo funcional se registrará aquí cuando se implemente.
    """

    def __init__(self, db_repo, user):
        self.db = db_repo
        self.user = user  # Usuario logueado (dict con id_user, username, etc.)
        self.modules = {}

    def get_user_info(self):
        """Retorna información del usuario logueado."""
        roles = self.db.get_roles_by_usuario(self.user['id_user'])
        return {
            'id': self.user['id_user'],
            'username': self.user['username'],
            'nombre': self.user.get('nombre', ''),
            'roles': [r['nombre'] for r in roles],
            'max_nivel': max([r['nivel'] for r in roles]) if roles else 0,
        }

    def has_permission(self, min_level=0):
        """Verifica si el usuario tiene el nivel mínimo de permiso."""
        info = self.get_user_info()
        return info['max_nivel'] >= min_level

    def register_module(self, name, widget_class, min_level=0):
        """Registra un módulo funcional para usar desde el dashboard."""
        self.modules[name] = {
            'class': widget_class,
            'min_level': min_level,
        }

    def get_available_modules(self):
        """Retorna los módulos que el usuario puede acceder."""
        info = self.get_user_info()
        available = []
        for name, mod in self.modules.items():
            if info['max_nivel'] >= mod['min_level']:
                available.append(name)
        return available

    def launch_module(self, name, parent_widget):
        """Lanza un módulo registrado."""
        if name not in self.modules:
            raise ValueError(f"Módulo '{name}' no registrado.")

        info = self.get_user_info()
        mod = self.modules[name]
        if info['max_nivel'] < mod['min_level']:
            raise PermissionError(f"No tienes permiso para acceder al módulo '{name}'.")

        return mod['class'](self.db, parent=parent_widget)
