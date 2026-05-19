from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import Caller, audit_success, require_cloudwatch_auth
from app.core.errors import conflict, not_found
from app.core.resource_ids import log_group_resource
from app.db.session import get_db
from app.models.log_group import LogGroup
from app.schemas.requests import CreateLogGroupRequest
from app.schemas.responses import LogGroupResponse

router = APIRouter(prefix="/cloudwatch/log-groups", tags=["log-groups"])


@router.post("", response_model=LogGroupResponse)
def create_log_group(
    payload: CreateLogGroupRequest,
    request: Request,
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:CreateLogGroup", "log-group/*")),
    db: Session = Depends(get_db),
) -> LogGroup:
    group = LogGroup(name=payload.name, retention_days=payload.retention_days, kms_key_id=payload.kms_key_id, tags=payload.tags)
    db.add(group)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("Duplicate log group") from exc
    db.refresh(group)
    audit_success(request, db, {"log_group": group.name})
    return group


@router.get("", response_model=list[LogGroupResponse])
def list_log_groups(
    request: Request,
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:GetLogEvents", "log-group/*")),
    db: Session = Depends(get_db),
) -> list[LogGroup]:
    groups = list(db.execute(select(LogGroup).order_by(LogGroup.name)).scalars())
    audit_success(request, db)
    return groups


@router.get("/{group_name:path}", response_model=LogGroupResponse)
def get_log_group(
    group_name: str,
    request: Request,
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:GetLogEvents", "log-group/*")),
    db: Session = Depends(get_db),
) -> LogGroup:
    group = db.execute(select(LogGroup).where(LogGroup.name == group_name)).scalar_one_or_none()
    if not group:
        raise not_found("Log group not found")
    audit_success(request, db, {"log_group": group.name})
    return group


@router.delete("/{group_name:path}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log_group(
    group_name: str,
    request: Request,
    _: Caller = Depends(require_cloudwatch_auth("cloudwatch:DeleteLogGroup", "log-group/*")),
    db: Session = Depends(get_db),
) -> None:
    group = db.execute(select(LogGroup).where(LogGroup.name == group_name)).scalar_one_or_none()
    if not group:
        raise not_found("Log group not found")
    db.delete(group)
    db.commit()
    audit_success(request, db, {"log_group": group_name})

