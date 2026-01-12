from datetime import timedelta

from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from sqlmodel import select

from app.auth import schemas, utils
from app.core.db import SessionDep
from app.models.user import User, UserLogLogin, UserRevokedToken
from app.util.datetime import get_current_time


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

        access_token_expires = timedelta(minutes=utils.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = utils.create_access_token(
            data={
                "sub": user.username,
                "id": user.id,
                "email": user.email,
            },
            expires_delta=access_token_expires,
        )

        return {"access_token": access_token, "token_type": "bearer"}

    def logout(self, db: SessionDep, token: str):
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

        # Check if the token is already revoked
        query = select(UserRevokedToken).where(UserRevokedToken.token == token)
        revoked_token = db.exec(query).first()
        if not revoked_token:
            revoked_token = UserRevokedToken(token=token, user_id=user_id)
            db.add(revoked_token)

        # Update the log with logout time
        log_query = select(UserLogLogin).where(UserLogLogin.token == token)
        log = db.exec(log_query).first()
        if log:
            log.logged_out_at = get_current_time()
            db.add(log)

        db.commit()
