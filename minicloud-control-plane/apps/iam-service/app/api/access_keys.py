from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.hashing import hash_secret
from app.core.resource_ids import generate_access_key_id, generate_secret_key
from app.db.session import get_db
from app.models.access_key import AccessKey
from app.schemas.requests import CreateAccessKeyRequest, UpdateAccessKeyRequest
from app.schemas.responses import AccessKeyCreateResponse, AccessKeyResponse

router = APIRouter(prefix="/iam/access-keys", tags=["access-keys"])


@router.post("", response_model=AccessKeyCreateResponse)
def create_access_key(payload: CreateAccessKeyRequest, db: Session = Depends(get_db)) -> AccessKeyCreateResponse:
    secret = generate_secret_key()
    access_key = AccessKey(
        access_key_id=generate_access_key_id(),
        secret_key_hash=hash_secret(secret),
        principal_type=payload.principal_type,
        principal_id=payload.principal_id,
    )
    db.add(access_key)
    db.commit()
    return AccessKeyCreateResponse(
        access_key_id=access_key.access_key_id,
        secret_access_key=secret,
        status=access_key.status,
    )


@router.get("", response_model=list[AccessKeyResponse])
def list_access_keys(db: Session = Depends(get_db)) -> list[AccessKey]:
    return list(db.execute(select(AccessKey).order_by(AccessKey.created_at)).scalars())


@router.patch("/{access_key_id}", response_model=AccessKeyResponse)
def update_access_key(
    access_key_id: str, payload: UpdateAccessKeyRequest, db: Session = Depends(get_db)
) -> AccessKey:
    key = db.execute(select(AccessKey).where(AccessKey.access_key_id == access_key_id)).scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="Access key not found")
    key.status = payload.status
    db.commit()
    db.refresh(key)
    return key


@router.delete("/{access_key_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_access_key(access_key_id: str, db: Session = Depends(get_db)) -> None:
    key = db.execute(select(AccessKey).where(AccessKey.access_key_id == access_key_id)).scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="Access key not found")
    db.delete(key)
    db.commit()

