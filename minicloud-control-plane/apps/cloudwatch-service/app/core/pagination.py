from fastapi import Query


def limit_query(default: int = 100) -> int:
    return Query(default=default, ge=1, le=1000)


def offset_query() -> int:
    return Query(default=0, ge=0)

