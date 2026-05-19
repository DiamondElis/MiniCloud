import secrets


def generate_access_key_id(prefix: str = "MCAKIA") -> str:
    return f"{prefix}{secrets.token_urlsafe(18).replace('-', '').replace('_', '')[:24].upper()}"


def generate_secret_key(prefix: str = "mcsk_live_") -> str:
    return f"{prefix}{secrets.token_urlsafe(36)}"


def user_arn(username: str) -> str:
    return f"minicloud:iam::local:user/{username}"


def role_arn(name: str) -> str:
    return f"minicloud:iam::local:role/{name}"

