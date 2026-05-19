from datetime import datetime
from typing import Any

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    username: str
    email: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GroupResponse(BaseModel):
    id: str
    name: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RoleResponse(BaseModel):
    id: str
    name: str
    description: str | None
    trust_policy: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PolicyResponse(BaseModel):
    id: str
    name: str
    document: dict[str, Any]
    version: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AccessKeyCreateResponse(BaseModel):
    access_key_id: str
    secret_access_key: str
    status: str


class AccessKeyResponse(BaseModel):
    access_key_id: str
    principal_type: str
    principal_id: str
    status: str
    created_at: datetime
    last_used_at: datetime | None
    expires_at: datetime | None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int


class WhoAmIResponse(BaseModel):
    principal_id: str
    principal_type: str
    username: str | None = None
    groups: list[str] = []
    roles: list[str] = []
    assumed_role_id: str | None = None


class AuthorizationResponse(BaseModel):
    decision: str
    reason: str
    matched_policy: str | None = None


class AssumeRoleResponse(BaseModel):
    access_key_id: str
    secret_access_key: str
    session_token: str
    expires_at: datetime
    assumed_role: str


class CallerIdentityResponse(BaseModel):
    principal_id: str
    principal_type: str
    arn: str

