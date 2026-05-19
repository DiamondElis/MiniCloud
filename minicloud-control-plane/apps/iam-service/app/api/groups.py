from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.policy import PrincipalPolicy
from app.models.user import Group, User
from app.schemas.requests import AttachPolicyRequest, CreateGroupRequest
from app.schemas.responses import GroupResponse, UserResponse

router = APIRouter(prefix="/iam/groups", tags=["groups"])


@router.post("", response_model=GroupResponse)
def create_group(payload: CreateGroupRequest, db: Session = Depends(get_db)) -> Group:
    group = Group(name=payload.name, description=payload.description)
    db.add(group)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate group") from exc
    db.refresh(group)
    return group


@router.post("/{group_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def add_user_to_group(group_id: str, user_id: str, db: Session = Depends(get_db)) -> None:
    group = db.get(Group, group_id)
    user = db.get(User, user_id)
    if not group or not user:
        raise HTTPException(status_code=404, detail="Group or user not found")
    if user not in group.users:
        group.users.append(user)
    db.commit()


@router.get("/{group_id}/users", response_model=list[UserResponse])
def list_group_users(group_id: str, db: Session = Depends(get_db)) -> list[User]:
    group = db.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group.users


@router.post("/{group_id}/policies", status_code=status.HTTP_204_NO_CONTENT)
def attach_group_policy(group_id: str, payload: AttachPolicyRequest, db: Session = Depends(get_db)) -> None:
    if not db.get(Group, group_id):
        raise HTTPException(status_code=404, detail="Group not found")
    db.add(PrincipalPolicy(principal_type="group", principal_id=group_id, policy_id=payload.policy_id))
    db.commit()

