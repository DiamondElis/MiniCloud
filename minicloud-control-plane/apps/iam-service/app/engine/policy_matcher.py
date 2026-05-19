from fnmatch import fnmatchcase
from typing import Any

from app.engine.policy_parser import normalize_list


def conditions_match(condition: dict[str, Any] | None, context: dict[str, Any] | None) -> bool:
    """Return True only for policies without conditions in v1.

    MiniCloud intentionally leaves AWS-style condition operators for a later phase.
    """
    return condition is None


def statement_matches(statement: dict[str, Any], action: str, resource: str, context: dict[str, Any] | None) -> bool:
    """Check action/resource wildcards and the v1 condition placeholder."""
    actions = normalize_list(statement["Action"], "Action")
    resources = normalize_list(statement["Resource"], "Resource")
    action_ok = any(fnmatchcase(action, pattern) for pattern in actions)
    resource_ok = any(fnmatchcase(resource, pattern) for pattern in resources)
    return action_ok and resource_ok and conditions_match(statement.get("Condition"), context)

