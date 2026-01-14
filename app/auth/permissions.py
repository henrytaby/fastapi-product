from enum import Enum
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth.schemas import UserModulePermission
from app.auth.utils import get_current_user
from app.core.db import get_session
from app.models.module import Module
from app.models.role import RoleModule
from app.models.user import User


class PermissionAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


class PermissionChecker:
    def __init__(self, module_slug: str, required_permission: PermissionAction):
        self.module_slug = module_slug
        self.required_permission = required_permission

    def __call__(self, user: User = Depends(get_current_user)) -> UserModulePermission:
        if user.is_superuser:
            return UserModulePermission(
                module_slug=self.module_slug,
                can_create=True,
                can_update=True,
                can_delete=True,
                can_read=True,
            )

        # Initialize permissions
        can_create = False
        can_update = False
        can_delete = False
        has_module_access = False

        # Iterate over user roles and aggregate permissions
        # user.user_roles -> role -> role_modules
        
        # Note: We assume user.user_roles is available (lazy loaded)
        for user_role in user.user_roles:
            if not user_role.is_active or not user_role.role.is_active:
                continue
                
            role = user_role.role
            for role_module in role.role_modules:
                # Check if this role_module corresponds to the requested module slug
                # Use greedy loading or check module relationship
                if role_module.module.slug == self.module_slug:
                    
                    # Check active status
                    if not role_module.is_active or not role_module.module.is_active:
                        continue

                    has_module_access = True
                    if role_module.can_create:
                        can_create = True
                    if role_module.can_update:
                        can_update = True
                    if role_module.can_delete:
                        can_delete = True

        # Determine READ permission (Implicit)
        can_read = has_module_access

        # Construct permission object
        user_permissions = UserModulePermission(
            module_slug=self.module_slug,
            can_create=can_create,
            can_update=can_update,
            can_delete=can_delete,
            can_read=can_read,
        )

        # Validate required permission
        is_allowed = False
        if self.required_permission == PermissionAction.READ:
            is_allowed = can_read
        elif self.required_permission == PermissionAction.CREATE:
            is_allowed = can_create
        elif self.required_permission == PermissionAction.UPDATE:
            is_allowed = can_update
        elif self.required_permission == PermissionAction.DELETE:
            is_allowed = can_delete

        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have '{self.required_permission}' permission for module '{self.module_slug}'",
            )

        return user_permissions
