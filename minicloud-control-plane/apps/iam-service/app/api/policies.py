from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.engine.policy_parser import PolicyValidationError, validate_policy_document
from app.models.policy import Policy
from app.schemas.requests import CreatePolicyRequest
from app.schemas.responses import PolicyResponse

router = APIRouter(prefix="/iam/policies", tags=["policies"])


@router.post("", response_model=PolicyResponse)
def create_policy(payload: CreatePolicyRequest, db: Session = Depends(get_db)) -> Policy:
    try:
        document = validate_policy_document(payload.document)
    except PolicyValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    policy = Policy(name=payload.name, document=document, version=document.get("Version", "2026-01-01"))
    db.add(policy)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate policy") from exc
    db.refresh(policy)
    return policy


@router.get("", response_model=list[PolicyResponse])
def list_policies(db: Session = Depends(get_db)) -> list[Policy]:
    return list(db.execute(select(Policy).order_by(Policy.name)).scalars())


@router.get("/{policy_id}", response_model=PolicyResponse)
def get_policy(policy_id: str, db: Session = Depends(get_db)) -> Policy:
    policy = db.get(Policy, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

