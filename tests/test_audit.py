import json
import os
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.main import app
from app.models.audit import AuditLog
from app.util.datetime import get_current_time
from scripts.archive_audit import archive_audit_logs

# Force enable audit for tests
settings.ENABLE_ACCESS_AUDIT = True
settings.ENABLE_DATA_AUDIT = True


def test_audit_access_log(client: TestClient, session: Session, superuser_token_headers):
    # 1. Perform a request
    # This endpoint should be audited
    response = client.get("/api/auth/users/me/", headers=superuser_token_headers)
    assert response.status_code == 200

    # 2. Check Audit Log
    session.expire_all() # Sync with DB
    
    log = session.exec(select(AuditLog).where(AuditLog.action == "ACCESS").order_by(AuditLog.timestamp.desc())).first()
    assert log is not None
    assert log.entity_id == "/api/auth/users/me/"
    assert log.user_id is not None
    assert log.username is not None


def test_audit_data_update(client: TestClient, session: Session, superuser_token_headers):
    # 1. Create a Task (Should trigger CREATE log)
    task_data = {"title": "Audit Test Task", "description": "Testing Hooks"}
    response = client.post("/api/tasks/", json=task_data, headers=superuser_token_headers)
    assert response.status_code == 201
    task_id = response.json()["id"]

    session.expire_all()

    # Check CREATE log
    log_create = session.exec(select(AuditLog).where(
        AuditLog.entity_type == "Task", 
        AuditLog.entity_id == str(task_id),
        AuditLog.action == "CREATE"
    )).first()
    assert log_create is not None
    session.refresh(log_create)
    assert log_create.user_id is not None # Should capture user from context

    # 2. Update the Task (Should trigger UPDATE log)
    update_data = {"title": "Updated Audit Task"}
    response = client.patch(f"/api/tasks/{task_id}", json=update_data, headers=superuser_token_headers)
    assert response.status_code == 201

    # Check UPDATE log
    log_update = session.exec(select(AuditLog).where(
        AuditLog.entity_type == "Task", 
        AuditLog.entity_id == str(task_id),
        AuditLog.action == "UPDATE"
    )).first()
    assert log_update is not None
    assert log_update.changes is not None
    # Depending on how JSON is stored (string or dict), check content
    # SQLModel with JSON column usually returns dict or list
    changes = log_update.changes
    if isinstance(changes, str):
        changes = json.loads(changes)
    
    assert "title" in changes
    assert changes["title"]["new"] == "Updated Audit Task"


def test_archive_script(session: Session, tmp_path):
    # 1. Insert old logs
    old_time = get_current_time() - timedelta(days=100)
    old_log = AuditLog(
        action="OLD_LOG", 
        entity_type="Test", 
        timestamp=old_time
    )
    session.add(old_log)
    session.commit()
    
    # 2. Run Archive
    archive_dir = tmp_path / "archive"
    archive_audit_logs(days_retention=90, archive_dir=str(archive_dir), engine=session.bind)
    
    # 3. Verify File Created
    files = list(archive_dir.glob("*.json.gz"))
    assert len(files) == 1
    
    # 4. Verify DB deleted
    check = session.exec(select(AuditLog).where(AuditLog.action == "OLD_LOG")).first()
    assert check is None
