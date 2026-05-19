from typing import Any


class PolicyValidationError(ValueError):
    pass


def normalize_list(value: str | list[str], field: str) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    raise PolicyValidationError(f"{field} must be a string or list of strings")


def validate_policy_document(document: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise PolicyValidationError("Policy document must be an object")
    statements = document.get("Statement")
    if isinstance(statements, dict):
        statements = [statements]
    if not isinstance(statements, list) or not statements:
        raise PolicyValidationError("Statement must be a non-empty list")

    for statement in statements:
        if not isinstance(statement, dict):
            raise PolicyValidationError("Each Statement must be an object")
        effect = statement.get("Effect")
        if effect not in {"Allow", "Deny"}:
            raise PolicyValidationError("Effect must be Allow or Deny")
        if "Action" not in statement:
            raise PolicyValidationError("Action is required")
        if "Resource" not in statement:
            raise PolicyValidationError("Resource is required")
        normalize_list(statement["Action"], "Action")
        normalize_list(statement["Resource"], "Resource")
    return document

