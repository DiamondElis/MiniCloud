from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.engine.policy_matcher import statement_matches
from app.models.audit_event import AuditEvent
from app.models.policy import Policy, PrincipalPolicy
from app.models.user import User


@dataclass(frozen=True)
class Principal:
    principal_type: str
    principal_id: str
    assumed_role_id: str | None = None


@dataclass(frozen=True)
class Decision:
    decision: str
    reason: str
    matched_policy: str | None


def load_effective_policies(db: Session, principal: Principal) -> list[Policy]:
    targets: list[tuple[str, str]] = [(principal.principal_type, principal.principal_id)]
    if principal.principal_type == "user":
        user = db.get(User, principal.principal_id)
        if user:
            targets.extend(("group", group.id) for group in user.groups)
    if principal.assumed_role_id:
        targets.append(("role", principal.assumed_role_id))

    policies: list[Policy] = []
    for ptype, pid in targets:
        rows = db.execute(
            select(Policy)
            .join(PrincipalPolicy, PrincipalPolicy.policy_id == Policy.id)
            .where(PrincipalPolicy.principal_type == ptype, PrincipalPolicy.principal_id == pid)
        ).scalars()
        policies.extend(rows.all())
    return policies


def evaluate_policies(
    policies: list[Policy], action: str, resource: str, context: dict[str, Any] | None = None
) -> Decision:
    """Evaluate MiniCloud IAM policy documents.

    Matching Deny statements are checked before Allows. If no statement matches,
    the result is the default implicit deny.
    """
    allow_policy_id: str | None = None
    for policy in policies:
        statements = policy.document.get("Statement", [])
        if isinstance(statements, dict):
            statements = [statements]
        for statement in statements:
            if statement.get("Effect") == "Deny" and statement_matches(statement, action, resource, context):
                return Decision("Deny", "ExplicitDeny", policy.id)

    for policy in policies:
        statements = policy.document.get("Statement", [])
        if isinstance(statements, dict):
            statements = [statements]
        for statement in statements:
            if statement.get("Effect") == "Allow" and statement_matches(statement, action, resource, context):
                allow_policy_id = policy.id
                return Decision("Allow", "ExplicitAllow", allow_policy_id)

    return Decision("Deny", "ImplicitDeny", None)


def authorize(
    db: Session,
    principal: Principal,
    action: str,
    resource: str,
    context: dict[str, Any] | None = None,
) -> Decision:
    policies = load_effective_policies(db, principal)
    decision = evaluate_policies(policies, action, resource, context)
    db.add(
        AuditEvent(
            principal_type=principal.principal_type,
            principal_id=principal.principal_id,
            action=action,
            resource=resource,
            decision=decision.decision,
            reason=decision.reason,
            matched_policy_id=decision.matched_policy,
            source_ip=(context or {}).get("source_ip"),
            user_agent=(context or {}).get("user_agent"),
            service=(context or {}).get("service"),
            request_id=(context or {}).get("request_id"),
        )
    )
    db.commit()
    return decision

