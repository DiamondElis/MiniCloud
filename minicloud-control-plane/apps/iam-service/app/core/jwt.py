import calendar
from datetime import timedelta
from typing import Any

import jwt

from app.core.config import get_settings
from app.db.base import utcnow


def create_access_token(
    *,
    session_id: str,
    principal_type: str,
    principal_id: str,
    assumed_role_id: str | None = None,
    expires_seconds: int | None = None,
) -> tuple[str, int]:
    settings = get_settings()
    ttl = expires_seconds or settings.jwt_expires_seconds
    now = utcnow()
    payload: dict[str, Any] = {
        "sid": session_id,
        "sub": principal_id,
        "ptype": principal_type,
        "iat": calendar.timegm(now.utctimetuple()),
        "exp": calendar.timegm((now + timedelta(seconds=ttl)).utctimetuple()),
    }
    if assumed_role_id:
        payload["assumed_role_id"] = assumed_role_id
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm), ttl


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
