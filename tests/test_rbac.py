
import pytest
from fastapi import HTTPException
from sqlmodel import Session

from app.auth.permissions import PermissionAction, PermissionChecker
from app.models.module import Module, ModuleGroup
from app.models.role import Role, RoleModule
from app.models.user import User, UserRole


def create_test_data(session: Session):
    # Create Module Group
    group = ModuleGroup(name="Test Group", slug="test-group", sort_order=1)
    session.add(group)
    session.commit()
    session.refresh(group)

    # Create Module
    module = Module(
        name="Test Module",
        slug="test-module",
        group_id=group.id,
        is_active=True,
        sort_order=1
    )
    session.add(module)
    session.commit()
    session.refresh(module)

    # Create Roles
    role_admin = Role(name="Admin Role", sort_order=1, is_active=True)
    role_guest = Role(name="Guest Role", sort_order=2, is_active=True)
    session.add(role_admin)
    session.add(role_guest)
    session.commit()
    session.refresh(role_admin)
    session.refresh(role_guest)

    # Assign Module to Roles
    # Admin Role: CREATE, UPDATE
    rm_admin = RoleModule(
        role_id=role_admin.id,
        module_id=module.id,
        is_active=True,
        can_create=True,
        can_update=True,
        can_delete=False
    )
    # Guest Role: ACTIVE (Implicit Read), but no write
    rm_guest = RoleModule(
        role_id=role_guest.id,
        module_id=module.id,
        is_active=True,
        can_create=False,
        can_update=False,
        can_delete=False
    )
    session.add(rm_admin)
    session.add(rm_guest)
    session.commit()

    return module, role_admin, role_guest


def test_superuser_access(session: Session):
    _, _, _ = create_test_data(session)
    
    superuser = User(username="super", email="super@test.com", password_hash="hash", is_superuser=True)
    session.add(superuser)
    session.commit()

    checker = PermissionChecker(module_slug="test-module", required_permission=PermissionAction.CREATE)
    perms = checker(user=superuser)
    
    assert perms.can_create is True
    assert perms.can_read is True
    assert perms.module_slug == "test-module"


def test_no_access(session: Session):
    module, _, _ = create_test_data(session)
    
    user = User(username="user", email="user@test.com", password_hash="hash", is_superuser=False)
    session.add(user)
    session.commit()
    session.refresh(user)

    checker = PermissionChecker(module_slug="test-module", required_permission=PermissionAction.READ)
    
    with pytest.raises(HTTPException) as excinfo:
        checker(user=user)
    
    assert excinfo.value.status_code == 403


def test_read_access(session: Session):
    _, _, role_guest = create_test_data(session)
    
    user = User(username="guest", email="guest@test.com", password_hash="hash", is_superuser=False)
    session.add(user)
    session.commit()
    session.refresh(user)

    # Assign Guest Role
    ur = UserRole(user_id=user.id, role_id=role_guest.id, is_active=True)
    session.add(ur)
    session.commit()
    session.refresh(user) # Reload relationships

    checker = PermissionChecker(module_slug="test-module", required_permission=PermissionAction.READ)
    perms = checker(user=user)
    
    assert perms.can_read is True
    assert perms.can_create is False


def test_create_access_allowed(session: Session):
    _, role_admin, _ = create_test_data(session)
    
    user = User(username="admin", email="admin@test.com", password_hash="hash", is_superuser=False)
    session.add(user)
    session.commit()
    session.refresh(user)

    # Assign Admin Role
    ur = UserRole(user_id=user.id, role_id=role_admin.id, is_active=True)
    session.add(ur)
    session.commit()
    session.refresh(user)

    checker = PermissionChecker(module_slug="test-module", required_permission=PermissionAction.CREATE)
    perms = checker(user=user)
    
    assert perms.can_create is True


def test_create_access_denied(session: Session):
    _, _, role_guest = create_test_data(session)
    
    user = User(username="guest_fail", email="guest_fail@test.com", password_hash="hash", is_superuser=False)
    session.add(user)
    session.commit()
    session.refresh(user)

    # Assign Guest Role (Read only)
    ur = UserRole(user_id=user.id, role_id=role_guest.id, is_active=True)
    session.add(ur)
    session.commit()
    session.refresh(user)

    checker = PermissionChecker(module_slug="test-module", required_permission=PermissionAction.CREATE)
    
    with pytest.raises(HTTPException) as excinfo:
        checker(user=user)
    
    assert excinfo.value.status_code == 403


def test_aggregated_access(session: Session):
    # Scenario: User has Role A (Create only) and Role B (Delete only). Should have both.
    module, _, _ = create_test_data(session)
    
    # Create Role A (Create)
    role_a = Role(name="Role A", sort_order=10, is_active=True)
    session.add(role_a)
    
    # Create Role B (Delete)
    role_b = Role(name="Role B", sort_order=11, is_active=True)
    session.add(role_b)
    session.commit()
    session.refresh(role_a)
    session.refresh(role_b)

    # Assign Module Permissions
    rm_a = RoleModule(role_id=role_a.id, module_id=module.id, is_active=True, can_create=True, can_update=False, can_delete=False)
    rm_b = RoleModule(role_id=role_b.id, module_id=module.id, is_active=True, can_create=False, can_update=False, can_delete=True)
    session.add(rm_a)
    session.add(rm_b)
    session.commit()

    # Create User with both roles
    user = User(username="multi", email="multi@test.com", password_hash="hash", is_superuser=False)
    session.add(user)
    session.commit()
    session.refresh(user)

    ur_a = UserRole(user_id=user.id, role_id=role_a.id, is_active=True)
    ur_b = UserRole(user_id=user.id, role_id=role_b.id, is_active=True)
    session.add(ur_a)
    session.add(ur_b)
    session.commit()
    session.refresh(user)

    # Check Create
    checker_create = PermissionChecker(module_slug="test-module", required_permission=PermissionAction.CREATE)
    perms_create = checker_create(user=user)
    assert perms_create.can_create is True

    # Check Delete
    checker_delete = PermissionChecker(module_slug="test-module", required_permission=PermissionAction.DELETE)
    perms_delete = checker_delete(user=user)
    assert perms_delete.can_delete is True

    # Check combined object
    assert perms_create.can_delete is True # Object should have all flags
