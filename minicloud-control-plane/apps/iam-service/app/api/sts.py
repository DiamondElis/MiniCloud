from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.hashing import token_fingerprint
from app.core.jwt import create_access_token
from app.core.resource_ids import generate_access_key_id, generate_secret_key
from app.core.security import get_current_principal
from app.db.base import utcnow
from app.db.session import get_db
from app.engine.decision_engine import Principal, authorize
from app.models.role import Role
from app.models.session import SessionToken
from app.schemas.requests import AssumeRoleRequest
from app.schemas.responses import AssumeRoleResponse, CallerIdentityResponse
from app.api.tokens import caller_identity

router = APIRouter(prefix="/sts", tags=["sts"])


def _trust_allows(role: Role, caller: Principal) -> bool:
    if role.trust_policy is None:
        return True
    allowed = role.trust_policy.get("Principal")
    if allowed == "*":
        return True
    if isinstance(allowed, dict):
        values = allowed.get(caller.principal_type)
        if isinstance(values, str):
            values = [values]
        return caller.principal_id in (values or [])
    return False


@router.post("/assume-role", response_model=AssumeRoleResponse)
def assume_role(
    payload: AssumeRoleRequest,
    caller: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
) -> AssumeRoleResponse:
    role = db.get(Role, payload.role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    decision = authorize(db, caller, "sts:AssumeRole", f"role/{role.id}", {"service": "sts"})
    if decision.decision != "Allow":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to assume role")
    if not _trust_allows(role, caller):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role trust policy denied caller")

    expires_at = utcnow() + timedelta(seconds=payload.duration_seconds)
    session = SessionToken(
        session_token_hash="pending",
        principal_type=caller.principal_type,
        principal_id=caller.principal_id,
        assumed_role_id=role.id,
        expires_at=expires_at,
    )
    db.add(session)
    db.flush()
    token, _ = create_access_token(
        session_id=session.id,
        principal_type=caller.principal_type,
        principal_id=caller.principal_id,
        assumed_role_id=role.id,
        expires_seconds=payload.duration_seconds,
    )
    session.session_token_hash = token_fingerprint(token)
    db.commit()
    return AssumeRoleResponse(
        access_key_id=generate_access_key_id("MCASIA_TEMP_"),
        secret_access_key=generate_secret_key("temporary-secret-"),
        session_token=token,
        expires_at=expires_at,
        assumed_role=role.name,
    )


@router.get("/get-caller-identity", response_model=CallerIdentityResponse)
def get_caller_identity(
    principal: Principal = Depends(get_current_principal), db: Session = Depends(get_db)
) -> CallerIdentityResponse:
    return caller_identity(principal, db)

