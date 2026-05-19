from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.policy import PrincipalPolicy
from app.models.role import Role
from app.schemas.requests import AttachPolicyRequest, CreateRoleRequest
from app.schemas.responses import RoleResponse

router = APIRouter(prefix="/iam/roles", tags=["roles"])


@router.post("", response_model=RoleResponse)
def create_role(payload: CreateRoleRequest, db: Session = Depends(get_db)) -> Role:
    role = Role(name=payload.name, description=payload.description, trust_policy=payload.trust_policy)
    db.add(role)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate role") from exc
    db.refresh(role)
    return role


@router.get("", response_model=list[RoleResponse])
def list_roles(db: Session = Depends(get_db)) -> list[Role]:
    return list(db.execute(select(Role).order_by(Role.name)).scalars())


@router.post("/{role_id}/policies", status_code=status.HTTP_204_NO_CONTENT)
def attach_role_policy(role_id: str, payload: AttachPolicyRequest, db: Session = Depends(get_db)) -> None:
    if not db.get(Role, role_id):
        raise HTTPException(status_code=404, detail="Role not found")
    db.add(PrincipalPolicy(principal_type="role", principal_id=role_id, policy_id=payload.policy_id))
    db.commit()

