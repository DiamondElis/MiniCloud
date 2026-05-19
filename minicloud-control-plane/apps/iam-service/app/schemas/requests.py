from typing import Any, Literal

from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    username: str
    email: str | None = None
    password: str | None = None


class CreateGroupRequest(BaseModel):
    name: str
    description: str | None = None


class CreateRoleRequest(BaseModel):
    name: str
    description: str | None = None
    trust_policy: dict[str, Any] | None = None


class CreatePolicyRequest(BaseModel):
    name: str
    document: dict[str, Any]


class AttachPolicyRequest(BaseModel):
    policy_id: str


class CreateAccessKeyRequest(BaseModel):
    principal_type: Literal["user", "group", "role", "service_account"]
    principal_id: str


class UpdateAccessKeyRequest(BaseModel):
    status: Literal["active", "inactive"]


class TokenRequest(BaseModel):
    grant_type: Literal["password", "access_key"]
    username: str | None = None
    password: str | None = None
    access_key_id: str | None = None
    secret_access_key: str | None = None


class RevokeTokenRequest(BaseModel):
    session_id: str | None = None


class AuthorizeRequest(BaseModel):
    principal_type: Literal["user", "group", "role", "service_account"]
    principal_id: str
    action: str
    resource: str
    context: dict[str, Any] | None = None
    assumed_role_id: str | None = None


class SimulatePrincipalPolicyRequest(BaseModel):
    principal_type: Literal["user", "group", "role", "service_account"]
    principal_id: str
    action: str
    resource: str


class AssumeRoleRequest(BaseModel):
    role_id: str
    session_name: str = Field(min_length=1, max_length=128)
    duration_seconds: int = Field(default=3600, ge=900, le=43200)

