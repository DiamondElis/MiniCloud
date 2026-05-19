from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.engine.context_builder import context_from_request
from app.engine.decision_engine import Principal, authorize
from app.schemas.requests import AuthorizeRequest, SimulatePrincipalPolicyRequest
from app.schemas.responses import AuthorizationResponse

router = APIRouter(prefix="/iam", tags=["authorization"])


@router.post("/authorize", response_model=AuthorizationResponse)
def authorize_endpoint(payload: AuthorizeRequest, request: Request, db: Session = Depends(get_db)) -> AuthorizationResponse:
    context = context_from_request(request)
    context.update(payload.context or {})
    decision = authorize(
        db,
        Principal(payload.principal_type, payload.principal_id, payload.assumed_role_id),
        payload.action,
        payload.resource,
        context,
    )
    return AuthorizationResponse(decision=decision.decision, reason=decision.reason, matched_policy=decision.matched_policy)


@router.post("/simulate-principal-policy", response_model=AuthorizationResponse)
def simulate_endpoint(payload: SimulatePrincipalPolicyRequest, db: Session = Depends(get_db)) -> AuthorizationResponse:
    decision = authorize(db, Principal(payload.principal_type, payload.principal_id), payload.action, payload.resource, {})
    return AuthorizationResponse(decision=decision.decision, reason=decision.reason, matched_policy=decision.matched_policy)

