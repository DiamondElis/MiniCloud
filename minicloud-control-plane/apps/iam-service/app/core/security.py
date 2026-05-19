from datetime import timedelta

import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.hashing import token_fingerprint
from app.core.jwt import decode_access_token
from app.db.base import utcnow
from app.db.session import get_db
from app.engine.decision_engine import Principal
from app.models.session import SessionToken


def extract_bearer_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return authorization.split(" ", 1)[1]


def get_current_principal(
    token: str = Depends(extract_bearer_token),
    db: Session = Depends(get_db),
) -> Principal:
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    session_id = payload.get("sid")
    session = db.get(SessionToken, session_id)
    if not session or session.session_token_hash != token_fingerprint(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    if session.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session revoked")
    if session.expires_at <= utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    return Principal(
        principal_type=session.principal_type,
        principal_id=session.principal_id,
        assumed_role_id=session.assumed_role_id,
    )


def session_expiration(seconds: int) -> object:
    return utcnow() + timedelta(seconds=seconds)

