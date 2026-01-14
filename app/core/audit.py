from contextvars import ContextVar
from typing import Optional

from fastapi import Request

# ContextVar to store current user_id for logging/CDC
audit_user_id_cv: ContextVar[Optional[int]] = ContextVar("audit_user_id", default=None)
# ContextVar to store current username
audit_username_cv: ContextVar[Optional[str]] = ContextVar(
    "audit_username", default=None
)
# ContextVar to store current IP address
audit_ip_address_cv: ContextVar[Optional[str]] = ContextVar(
    "audit_ip_address", default=None
)
# ContextVar to store current user_agent
audit_user_agent_cv: ContextVar[Optional[str]] = ContextVar(
    "audit_user_agent", default=None
)


def set_audit_context(
    user_id: Optional[int],
    ip_address: Optional[str],
    username: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    """Set context variables for the current request"""
    audit_user_id_cv.set(user_id)
    audit_ip_address_cv.set(ip_address)
    audit_username_cv.set(username)
    audit_user_agent_cv.set(user_agent)


def get_audit_user_id() -> Optional[int]:
    return audit_user_id_cv.get()


def get_audit_ip_address() -> Optional[str]:
    return audit_ip_address_cv.get()


def get_audit_username() -> Optional[str]:
    return audit_username_cv.get()


def get_audit_user_agent() -> Optional[str]:
    return audit_user_agent_cv.get()


async def skip_access_audit(request: Request):
    """
    Dependency to skip access audit for specific endpoints.
    Usage: @router.get("/", dependencies=[Depends(skip_access_audit)])
    """
    request.state.skip_audit = True
