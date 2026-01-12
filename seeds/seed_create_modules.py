from sqlmodel import Session, select

from app.core.db import engine
from app.models.module import Module, ModuleGroup


def create_module_groups(session: Session):
    module_groups = [
        {
            "name": "Usuarios",
            "description": "Gestión de Usuario & Roles del sistema",
            "order": 1,
            "icon": "tablet-book",
            "is_active": True,
        },
        {
            "name": "Configuración",
            "description": "Configuración de Sistema",
            "order": 2,
            "icon": "tablet-book",
            "is_active": True,
        },
    ]
    for group_data in module_groups:
        group = ModuleGroup(**group_data)
        session.add(group)
    session.commit()


def create_modules(session: Session):
    # Fetch the module groups to get their IDs
    group_1 = session.exec(
        select(ModuleGroup).where(ModuleGroup.name == "Usuarios")
    ).first()
    group_2 = session.exec(
        select(ModuleGroup).where(ModuleGroup.name == "Configuración")
    ).first()

    assert group_1 is not None, "ModuleGroup 'Usuarios' not found"
    assert group_2 is not None, "ModuleGroup 'Configuración' not found"

    modules = [
        {
            "name": "Gestión de usuarios",
            "description": "Administrar usuarios",
            "group_id": group_1.id,
            "is_active": True,
            "can_create": True,
            "can_update": True,
            "can_delete": True,
            "icon": None,
            "route": "/users/management",
            "order": 1,
        },
        {
            "name": "Asignación de roles",
            "description": "Administrar Roles",
            "group_id": group_1.id,
            "is_active": True,
            "can_create": True,
            "can_update": True,
            "can_delete": True,
            "icon": None,
            "route": "/roles/management",
            "order": 2,
        },
        {
            "name": "Módulos",
            "description": "Gestión de Módulos",
            "group_id": group_2.id,
            "is_active": True,
            "can_create": True,
            "can_update": True,
            "can_delete": True,
            "icon": None,
            "route": "/modules/management",
            "order": 1,
        },
    ]
    for module_data in modules:
        module = Module(**module_data)
        session.add(module)
    session.commit()


def run_seeders():
    with Session(engine) as session:
        create_module_groups(session)
        create_modules(session)


if __name__ == "__main__":
    run_seeders()
