from sqlmodel import Session, SQLModel, select

from app.auth.utils import get_password_hash
from app.core.db import engine
from app.models.module import Module, ModuleGroup
from app.models.role import Role, RoleModule
from app.models.user import User, UserRole
from app.util.datetime import get_current_time


def reset_database():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


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


def create_roles(session: Session):
    roles = [
        {"name": "Guest", "description": "Guest role", "is_active": True, "order": 1},
        {
            "name": "Admin",
            "description": "Administrator role",
            "is_active": True,
            "order": 2,
        },
        {
            "name": "Manager Config",
            "description": "Manager role",
            "is_active": True,
            "order": 3,
        },
    ]

    for role_data in roles:
        role = Role(**role_data)
        session.add(role)
    session.commit()


def create_role_modules(session: Session):
    # Fetch the roles and modules to get their IDs
    # guest_role = session.exec(select(Role).where(Role.name == "Guest")).first()
    admin_role = session.exec(select(Role).where(Role.name == "Admin")).first()
    manager_role = session.exec(
        select(Role).where(Role.name == "Manager Config")
    ).first()

    module1 = session.exec(
        select(Module).where(Module.name == "Gestión de usuarios")
    ).first()
    module2 = session.exec(
        select(Module).where(Module.name == "Asignación de roles")
    ).first()
    module3 = session.exec(select(Module).where(Module.name == "Módulos")).first()

    role_modules = [
        {
            "role_id": admin_role.id,
            "module_id": module1.id,
            "can_create": True,
            "can_update": True,
            "can_delete": True,
            "is_active": True,
            "description": module1.description,
        },
        {
            "role_id": admin_role.id,
            "module_id": module2.id,
            "can_create": True,
            "can_update": True,
            "can_delete": True,
            "is_active": True,
            "description": module2.description,
        },
        {
            "role_id": admin_role.id,
            "module_id": module3.id,
            "can_create": True,
            "can_update": True,
            "can_delete": True,
            "is_active": True,
            "description": module3.description,
        },
        {
            "role_id": manager_role.id,
            "module_id": module1.id,
            "can_create": False,
            "can_update": False,
            "can_delete": False,
            "is_active": True,
            "description": module1.description,
        },
        {
            "role_id": manager_role.id,
            "module_id": module2.id,
            "can_create": True,
            "can_update": True,
            "can_delete": False,
            "is_active": True,
            "description": module2.description,
        },
        {
            "role_id": manager_role.id,
            "module_id": module3.id,
            "can_create": False,
            "can_update": False,
            "can_delete": False,
            "is_active": True,
            "description": module3.description,
        },
    ]

    for role_module_data in role_modules:
        role_module = RoleModule(**role_module_data)
        session.add(role_module)
    session.commit()


def create_users(session: Session):
    admin_role = session.exec(select(Role).where(Role.name == "Admin")).first()
    manager_role = session.exec(
        select(Role).where(Role.name == "Manager Config")
    ).first()

    admin_user = User(
        username="admin",
        email="admin@henrytaby.com",
        first_name="Admin",
        last_name="User",
        is_verified=True,
        is_active=True,
        is_superuser=True,
        password_hash=get_password_hash("adminpassword"),
        created_at=get_current_time(),
        updated_at=get_current_time(),
    )
    session.add(admin_user)
    session.commit()

    manager_user = User(
        username="manager",
        email="manager@henrytaby.com",
        first_name="Manager",
        last_name="User",
        is_verified=True,
        is_active=True,
        is_superuser=False,
        password_hash=get_password_hash("managerpassword"),
        created_at=get_current_time(),
        updated_at=get_current_time(),
    )
    session.add(manager_user)
    session.commit()

    # Assign roles to users
    admin_user_role = UserRole(
        user_id=admin_user.id,
        role_id=admin_role.id,
        is_active=True,
        created_at=get_current_time(),
        updated_at=get_current_time(),
    )
    session.add(admin_user_role)

    admin_user_role = UserRole(
        user_id=admin_user.id,
        role_id=manager_role.id,
        is_active=True,
        created_at=get_current_time(),
        updated_at=get_current_time(),
    )
    session.add(admin_user_role)

    manager_user_role = UserRole(
        user_id=manager_user.id,
        role_id=manager_role.id,
        is_active=True,
        created_at=get_current_time(),
        updated_at=get_current_time(),
    )
    session.add(manager_user_role)
    session.commit()


def run_seeders():
    reset_database()
    with Session(engine) as session:
        create_module_groups(session)
        create_modules(session)
        create_roles(session)
        create_role_modules(session)
        create_users(session)


if __name__ == "__main__":
    run_seeders()
