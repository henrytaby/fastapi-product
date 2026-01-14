from sqlalchemy import event, inspect
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine

from app.core.audit import (
    get_audit_user_id, 
    get_audit_ip_address, 
    get_audit_username, 
    get_audit_user_agent
)
from app.core.config import settings
from app.models.audit import AuditLog

# Import models you want to track to ensure they are loaded
# Or track generic SQLModel 
from sqlmodel import SQLModel


def register_audit_hooks(engine: Engine):
    if not settings.ENABLE_DATA_AUDIT:
        return

    event.listen(Session, "after_flush", audit_changes)


def audit_changes(session: Session, flush_context):
    # This hook runs after flush but before commit
    # We collect changes and insert audit logs into the SAME transaction
    
    user_id = get_audit_user_id()
    ip_address = get_audit_ip_address()
    username = get_audit_username()
    user_agent = get_audit_user_agent()

    # Iterate over new, changed, and deleted objects
    for obj in session.new:
        if isinstance(obj, AuditLog): continue
        create_log(session, obj, "CREATE", user_id, ip_address, username, user_agent)

    for obj in session.dirty:
        if isinstance(obj, AuditLog): continue
        create_log(session, obj, "UPDATE", user_id, ip_address, username, user_agent)

    for obj in session.deleted:
        if isinstance(obj, AuditLog): continue
        create_log(session, obj, "DELETE", user_id, ip_address, username, user_agent)


def create_log(session: Session, obj, action: str, user_id, ip_address, username, user_agent):
    if not isinstance(obj, SQLModel):
        return

    state = inspect(obj)
    mapper = state.mapper
    pk = mapper.primary_key[0]
    entity_id = getattr(obj, pk.name)
    entity_type = obj.__class__.__name__
    
    changes = {}
    
    if action == "UPDATE":
        for attr in state.attrs:
            history = attr.history
            if history.has_changes():
                # Get old value (deleted[0] usually holds old value)
                old_val = history.deleted[0] if history.deleted else None
                new_val = history.added[0] if history.added else None
                if old_val != new_val:
                    changes[attr.key] = {"old": str(old_val), "new": str(new_val)}
    
    elif action == "CREATE":
        # Log initial values for CREATE
        # We try to use model_dump() if it's a Pydantic/SQLModel
        if hasattr(obj, "model_dump"):
            changes = obj.model_dump(mode="json")
        else:
            # Fallback for generic SQLAlchemy models if needed
            changes = {c.key: getattr(obj, c.key) for c in mapper.column_attrs}

    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        changes=changes if changes else None,
        ip_address=ip_address,
        username=username,
        user_agent=user_agent
    )
    session.add(log)
