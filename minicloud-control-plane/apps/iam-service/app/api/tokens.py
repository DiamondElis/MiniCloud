from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.hashing import token_fingerprint, verify_secret
from app.core.jwt import create_access_token
from app.core.resource_ids import role_arn, user_arn
from app.core.security import get_current_principal, session_expiration
from app.db.base import utcnow
from app.db.session import get_db
from app.engine.decision_engine import Principal
from app.models.access_key import AccessKey
from app.models.role import Role
from app.models.session import SessionToken
from app.models.user import User
from app.schemas.requests import RevokeTokenRequest, TokenRequest
from app.schemas.responses import CallerIdentityResponse, TokenResponse, WhoAmIResponse

router = APIRouter(prefix="/iam", tags=["tokens"])


def _issue_token(db: Session, principal_type: str, principal_id: str, assumed_role_id: str | None = None) -> TokenResponse:
    settings = get_settings()
    session = SessionToken(
        session_token_hash="pending",
        principal_type=principal_type,
        principal_id=principal_id,
        assumed_role_id=assumed_role_id,
        expires_at=session_expiration(settings.jwt_expires_seconds),
    )
    db.add(session)
    db.flush()
    token, ttl = create_access_token(
        session_id=session.id,
        principal_type=principal_type,
        principal_id=principal_id,
        assumed_role_id=assumed_role_id,
    )
    session.session_token_hash = token_fingerprint(token)
    db.commit()
    return TokenResponse(access_token=token, expires_in=ttl)


@router.post("/token", response_model=TokenResponse)
def create_token(payload: TokenRequest, db: Session = Depends(get_db)) -> TokenResponse:
    if payload.grant_type == "password":
        user = db.execute(select(User).where(User.username == payload.username)).scalar_one_or_none()
        if not user or not user.password_hash or not payload.password or not verify_secret(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if user.status != "active":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User disabled")
        return _issue_token(db, "user", user.id)

    key = db.execute(select(AccessKey).where(AccessKey.access_key_id == payload.access_key_id)).scalar_one_or_none()
    if not key or not payload.secret_access_key or not verify_secret(payload.secret_access_key, key.secret_key_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if key.status != "active" or (key.expires_at and key.expires_at <= utcnow()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access key disabled or expired")
    key.last_used_at = utcnow()
    token = _issue_token(db, key.principal_type, key.principal_id)
    db.commit()
    return token


@router.post("/token/revoke", status_code=status.HTTP_204_NO_CONTENT)
def revoke_token(
    payload: RevokeTokenRequest,
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
) -> None:
    session = db.get(SessionToken, payload.session_id) if payload.session_id else None
    if not session:
        session = db.execute(
            select(SessionToken).where(
                SessionToken.principal_type == principal.principal_type,
                SessionToken.principal_id == principal.principal_id,
                SessionToken.revoked_at.is_(None),
            )
        ).scalar_one_or_none()
    if session:
        session.revoked_at = utcnow()
        db.commit()


@router.get("/whoami", response_model=WhoAmIResponse)
def whoami(principal: Principal = Depends(get_current_principal), db: Session = Depends(get_db)) -> WhoAmIResponse:
    if principal.principal_type == "user":
        user = db.get(User, principal.principal_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        roles = []
        if principal.assumed_role_id:
            role = db.get(Role, principal.assumed_role_id)
            roles = [role.name] if role else []
        return WhoAmIResponse(
            principal_id=user.id,
            principal_type="user",
            username=user.username,
            groups=[group.name for group in user.groups],
            roles=roles,
            assumed_role_id=principal.assumed_role_id,
        )
    role = db.get(Role, principal.principal_id)
    return WhoAmIResponse(
        principal_id=principal.principal_id,
        principal_type=principal.principal_type,
        roles=[role.name] if role else [],
        assumed_role_id=principal.assumed_role_id,
    )


def caller_identity(principal: Principal, db: Session) -> CallerIdentityResponse:
    if principal.assumed_role_id:
        role = db.get(Role, principal.assumed_role_id)
        arn = role_arn(role.name if role else principal.assumed_role_id)
        return CallerIdentityResponse(principal_id=principal.assumed_role_id, principal_type="role", arn=arn)
    if principal.principal_type == "user":
        user = db.get(User, principal.principal_id)
        arn = user_arn(user.username if user else principal.principal_id)
    else:
        role = db.get(Role, principal.principal_id)
        arn = role_arn(role.name if role else principal.principal_id)
    return CallerIdentityResponse(principal_id=principal.principal_id, principal_type=principal.principal_type, arn=arn)

