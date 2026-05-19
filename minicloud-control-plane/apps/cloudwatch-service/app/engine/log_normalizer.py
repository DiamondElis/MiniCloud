from typing import Any


def extract_field(event: dict[str, Any] | None, *names: str) -> str | None:
    if not event:
        return None
    for name in names:
        value = event.get(name)
        if value is not None:
            return str(value)
    return None


def readable_message(event: dict[str, Any] | None) -> str | None:
    if not event:
        return None
    event_name = extract_field(event, "event_name", "action")
    status = extract_field(event, "status")
    resource = extract_field(event, "resource", "instance_id", "bucket", "resource_id")
    parts = [part for part in [event_name, status, resource] if part]
    return " ".join(parts) if parts else None


def normalize_log_event(event: dict[str, Any] | None, message: str | None) -> dict[str, str | None]:
    return {
        "message": message or readable_message(event),
        "request_id": extract_field(event, "request_id"),
        "principal": extract_field(event, "principal"),
        "service": extract_field(event, "service"),
        "action": extract_field(event, "action", "event_name"),
        "resource": extract_field(event, "resource", "resource_id", "instance_id"),
        "status": extract_field(event, "status"),
        "level": extract_field(event, "level") or "INFO",
    }

