from fastapi import Request


def context_from_request(request: Request) -> dict[str, str | None]:
    return {
        "source_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "request_id": request.headers.get("x-request-id"),
        "service": request.headers.get("x-minicloud-service"),
    }

