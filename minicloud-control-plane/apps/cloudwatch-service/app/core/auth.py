from dataclasses import dataclass

import httpx
from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.clients.iam_client import IamClient
from app.core.config import get_settings
from app.db.session import get_db
from app.repositories.audit_repo import write_audit


@dataclass(frozen=True)
class Caller:
    principal: str
    decision: str = "Allow"


def get_iam_client() -> IamClient:
    return IamClient(get_settings().iam_base_url)


def bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return authorization.split(" ", 1)[1]


def require_cloudwatch_auth(action: str, resource: str, skip_audit: bool = False):
    def dependency(
        request: Request,
        authorization: str | None = Header(default=None),
        db: Session = Depends(get_db),
        iam: IamClient = Depends(get_iam_client),
    ) -> Caller:
        settings = get_settings()
        if not settings.iam_auth_enabled:
            request.state.cloudwatch_action = action
            request.state.cloudwatch_resource = resource
            request.state.cloudwatch_principal = "system/dev"
            request.state.skip_audit = skip_audit
            return Caller("system/dev")

        token = bearer_token(authorization)
        try:
            identity = iam.whoami(token)
            ptype = identity.get("principal_type")
            pid = identity.get("principal_id")
            allowed = iam.authorize(token, ptype, pid, action, resource)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in {401, 403}:
                raise HTTPException(status_code=exc.response.status_code, detail="IAM authorization failed") from exc
            raise HTTPException(status_code=502, detail="IAM unavailable") from exc
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail="IAM unavailable") from exc

        principal = f"{ptype}/{pid}"
        request.state.cloudwatch_action = action
        request.state.cloudwatch_resource = resource
        request.state.cloudwatch_principal = principal
        request.state.skip_audit = skip_audit
        if not allowed:
            if not skip_audit:
                write_audit(db, principal=principal, action=action, resource=resource, status="Denied", decision="Deny")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="IAM denied")
        return Caller(principal)

    return dependency


def audit_success(request: Request, db: Session, detail: dict | None = None) -> None:
    if getattr(request.state, "skip_audit", False):
        return
    write_audit(
        db,
        principal=getattr(request.state, "cloudwatch_principal", "system/dev"),
        action=getattr(request.state, "cloudwatch_action", "cloudwatch:Unknown"),
        resource=getattr(request.state, "cloudwatch_resource", None),
        status="Success",
        decision="Allow",
        detail=detail or {},
    )

