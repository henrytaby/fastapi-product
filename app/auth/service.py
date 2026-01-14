from datetime import timedelta

from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from sqlmodel import select

from app.auth import schemas, utils
from app.core.db import SessionDep
from app.models.user import User, UserLogLogin, UserRevokedToken
from app.util.datetime import get_current_time
from app.models.role import Role, RoleModule
from app.models.module import Module, ModuleGroup
from app.auth.schemas import RoleInfo, ModuleGroupMenu, ModuleMenu, UserModulePermission


class AuthService:
    # CREATE USER
    # ----------------------
    def create_user(self, user: schemas.UserCreate, db: SessionDep):
        query = select(User).where(User.username == user.username)
        db_user = db.exec(query).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        hashed_password = utils.get_password_hash(user.password)
        user_data_dict = user.model_dump(exclude_unset=True)
        del user_data_dict["password"]
        user_data_dict["password_hash"] = hashed_password
        new_user = User(**user_data_dict)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    def login_for_access_token(
        self,
        db: SessionDep,
        form_data: OAuth2PasswordRequestForm,
        request: Request,
    ):
        ip_address = request.client.host if request and request.client else "unknown"
        user_agent = request.headers.get("user-agent") if request else "unknown"

        user = utils.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            # Log the failed login attempt
            log = UserLogLogin(
                user_id=None,
                username=form_data.username,
                password=form_data.password,
                token=None,
                token_expiration=None,
                ip_address=ip_address,
                host_info=user_agent,
                is_successful=False,
            )
            db.add(log)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=utils.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=utils.REFRESH_TOKEN_EXPIRE_DAYS)

        access_token = utils.create_access_token(
            data={
                "sub": user.username,
                "id": user.id,
                "email": user.email,
            },
            expires_delta=access_token_expires,
        )

        refresh_token = utils.create_access_token(
            data={
                "sub": user.username,
                "id": user.id,
                "email": user.email,
            },
            expires_delta=refresh_token_expires,
        )

        # Log the login attempt
        log = UserLogLogin(
            user_id=user.id,
            username=user.username,
            token=access_token,
            token_expiration=get_current_time() + access_token_expires,
            ip_address=ip_address,
            host_info=user_agent,
            is_successful=True,
        )
        db.add(log)
        db.commit()
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token,
        }

    def refresh_access_token(self, db: SessionDep, refresh_token: str):
        try:
            payload = utils.decode_token(refresh_token)
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            ) from None

        user = utils.get_user(db, username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        # Check if the refresh token is already revoked
        query_revoked = select(UserRevokedToken).where(
            UserRevokedToken.token == refresh_token
        )
        revoked_token = db.exec(query_revoked).first()
        if revoked_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        # Revoke the old refresh token (Rotate)
        # Using 0 as user_id temporarily, or accurate user_id if we want
        # stricter validation earlier used_id for the record.
        new_revoked_token = UserRevokedToken(token=refresh_token, user_id=user.id)
        db.add(new_revoked_token)
        db.commit()

        access_token_expires = timedelta(minutes=utils.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=utils.REFRESH_TOKEN_EXPIRE_DAYS)

        access_token = utils.create_access_token(
            data={
                "sub": user.username,
                "id": user.id,
                "email": user.email,
            },
            expires_delta=access_token_expires,
        )

        new_refresh_token = utils.create_access_token(
            data={
                "sub": user.username,
                "id": user.id,
                "email": user.email,
            },
            expires_delta=refresh_token_expires,
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": new_refresh_token,
        }

    def logout(self, db: SessionDep, token: str, refresh_token: str | None = None):
        try:
            payload = utils.decode_token(token)
            user_id: int = payload.get("id")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            ) from None

        # Check if the access token is already revoked
        query = select(UserRevokedToken).where(UserRevokedToken.token == token)
        revoked_token = db.exec(query).first()
        if not revoked_token:
            revoked_token = UserRevokedToken(token=token, user_id=user_id)
            db.add(revoked_token)

        # Revoke Refresh Token if provided
        if refresh_token:
            query_rf = select(UserRevokedToken).where(
                UserRevokedToken.token == refresh_token
            )
            revoked_rf = db.exec(query_rf).first()
            if not revoked_rf:
                revoked_rf = UserRevokedToken(token=refresh_token, user_id=user_id)
                db.add(revoked_rf)

        # Update the log with logout time
        log_query = select(UserLogLogin).where(UserLogLogin.token == token)
        log = db.exec(log_query).first()
        if log:
            log.logged_out_at = get_current_time()
            db.add(log)

        db.commit()

    def get_user_roles(self, user: User, db: SessionDep) -> list[RoleInfo]:
        if user.is_superuser:
            # Superuser sees all active roles
            query = select(Role).where(Role.is_active == True).order_by(Role.sort_order)
            roles = db.exec(query).all()
        else:
            # Normal user sees their assigned active roles
            # We filter by Role.is_active AND UserRole.is_active
            roles = []
            for ur in user.user_roles:
                if ur.is_active and ur.role.is_active:
                    roles.append(ur.role)
            # Sort manually since we iterated
            roles.sort(key=lambda r: r.sort_order if r.sort_order else 0)

        return [RoleInfo(id=r.id, name=r.name, icon=r.icon) for r in roles]

    def get_role_menu(self, user: User, role_id: int, db: SessionDep) -> list[ModuleGroupMenu]:
        # 1. Validate Access to Role
        target_role = None
        if user.is_superuser:
            target_role = db.get(Role, role_id)
            if not target_role or not target_role.is_active:
                raise HTTPException(status_code=404, detail="Role not found or inactive")
        else:
            # Check if user has this role active
            has_role = False
            for ur in user.user_roles:
                if ur.role_id == role_id and ur.is_active and ur.role.is_active:
                    target_role = ur.role
                    has_role = True
                    break
            
            if not has_role:
                raise HTTPException(status_code=403, detail="User does not have access to this role")

        # 2. Fetch Modules for this Role
        # Structure: Group -> Modules
        groups_map = {} # {group_id: ModuleGroup}
        modules_by_group = {} # {group_id: [ModuleMenu]}

        for rm in target_role.role_modules:
            if not rm.is_active:
                continue
            
            module = rm.module
            if not module.is_active:
                continue
            
            # Found valid module
            group = module.group
            if group.id not in groups_map:
                groups_map[group.id] = group
                modules_by_group[group.id] = []
            
            # Create Permission Object
            perms = UserModulePermission(
                module_slug=module.slug,
                can_create=rm.can_create,
                can_update=rm.can_update,
                can_delete=rm.can_delete,
                can_read=True # Implied
            )

            # Create ModuleMenu Object
            mod_menu = ModuleMenu(
                name=module.name,
                slug=module.slug,
                route=module.route,
                icon=module.icon,
                sort_order=module.sort_order,
                permissions=perms
            )
            modules_by_group[group.id].append(mod_menu)

        # 3. Build Result List
        result = []
        # Sort groups
        sorted_groups = sorted(groups_map.values(), key=lambda g: g.sort_order if g.sort_order else 0)

        for group in sorted_groups:
            # Sort modules in group
            modules = modules_by_group[group.id]
            modules.sort(key=lambda m: m.sort_order if m.sort_order else 0)

            group_menu = ModuleGroupMenu(
                group_name=group.name,
                slug=group.slug,
                icon=group.icon,
                sort_order=group.sort_order,
                modules=modules
            )
            result.append(group_menu)

        return result
