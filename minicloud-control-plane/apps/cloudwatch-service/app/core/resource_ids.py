from uuid import uuid4


def new_uuid() -> str:
    return str(uuid4())


def log_group_resource(name: str) -> str:
    return f"log-group/{name}"


def log_stream_resource(group: str, stream: str) -> str:
    return f"log-stream/{group}/{stream}"


def metric_resource(namespace: str, metric_name: str) -> str:
    return f"metric/{namespace}/{metric_name}"


def event_bus_resource(name: str) -> str:
    return f"event-bus/{name}"


def alarm_resource(name: str) -> str:
    return f"alarm/{name}"

