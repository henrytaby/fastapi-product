from fastapi import Request
from sqlmodel import Session
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth.utils import decode_token
from app.core import db
from app.core.config import settings
from app.models.audit import AuditLog

from .context import set_audit_context


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Check Global Disable
        if not settings.ENABLE_ACCESS_AUDIT:
            return await call_next(request)

        # 2. Check Global Enpoint Exclusions (Fastest check)
        path = request.url.path
        method = request.method
        for excluded in settings.AUDIT_EXCLUDED_PATHS:
            # Case 1: "METHOD:/path"
            if ":" in excluded:
                ex_method, ex_path = excluded.split(":", 1)
                if method.upper() == ex_method.upper() and path.startswith(ex_path):
                    return await call_next(request)
            # Case 2: "/path" (All methods)
            elif path.startswith(excluded):
                return await call_next(request)

        # 3. Process Request (We need to run this to get dependencies
        # resolved like skip_audit)
        # Note: Middleware runs BEFORE dependencies, so populating ContextVars
        # here is tricky if we depend on deps.
        # However, for JWT extraction we can do it manually here.

        # Extract User ID from Token (Manual decode to avoid interfering
        # with Auth Dependencies)
        user_id = None
        username = "Anonymous"

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                # We reuse the util but handle errors gracefully
                payload = decode_token(token)
                user_id = payload.get("id")
                username = payload.get("sub", "Unknown")
            except Exception:
                pass  # Use anonymous if token is invalid

        # Set ContextVars for Hooks
        ip_address = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent")
        set_audit_context(user_id, ip_address, username, user_agent)

        response = await call_next(request)

        # 4. Check Request State (set by dependencies)
        if hasattr(request.state, "skip_audit") and request.state.skip_audit:
            return response

        # 5. Log Access (Async Fire & Forget ideally, but for now
        # Synchronous or BackgroundTask)
        # Since we are in middleware, we should be careful about blocking.
        # Writing to DB is fast enough for this scale.
        try:
            with Session(db.engine) as session:
                log = AuditLog(
                    user_id=user_id,
                    username=username,
                    action="ACCESS",
                    entity_type="Endpoint",
                    entity_id=path,
                    changes={"method": method, "status_code": response.status_code},
                    ip_address=ip_address,
                    user_agent=request.headers.get("user-agent"),
                )
                session.add(log)
                session.commit()
        except Exception as e:
            print(f"Audit Log Error: {e}")

        return response
