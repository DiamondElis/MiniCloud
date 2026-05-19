from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.hashing import hash_secret
from app.db.session import get_db
from app.models.policy import PrincipalPolicy
from app.models.user import User
from app.schemas.requests import AttachPolicyRequest, CreateUserRequest
from app.schemas.responses import UserResponse

router = APIRouter(prefix="/iam/users", tags=["users"])


@router.post("", response_model=UserResponse)
def create_user(payload: CreateUserRequest, db: Session = Depends(get_db)) -> User:
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_secret(payload.password) if payload.password else None,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate user") from exc
    db.refresh(user)
    return user


@router.get("", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)) -> list[User]:
    return list(db.execute(select(User).order_by(User.username)).scalars())


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/{user_id}/policies", status_code=status.HTTP_204_NO_CONTENT)
def attach_user_policy(user_id: str, payload: AttachPolicyRequest, db: Session = Depends(get_db)) -> None:
    if not db.get(User, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    db.add(PrincipalPolicy(principal_type="user", principal_id=user_id, policy_id=payload.policy_id))
    db.commit()

