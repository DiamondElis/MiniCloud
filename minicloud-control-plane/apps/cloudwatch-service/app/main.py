from fastapi import FastAPI

from app.api import alarms, audit, events, health, log_groups, log_streams, logs, metrics
from app.db.session import SessionLocal
from app.repositories.events_repo import seed_default_buses


def create_app() -> FastAPI:
    app = FastAPI(title="MiniCloud CloudWatch Service", version="0.1.0")
    app.include_router(health.router)
    app.include_router(log_streams.router)
    app.include_router(logs.router)
    app.include_router(log_groups.router)
    app.include_router(metrics.router)
    app.include_router(events.router)
    app.include_router(alarms.router)
    app.include_router(audit.router)

    @app.on_event("startup")
    def startup() -> None:
        db = SessionLocal()
        try:
            seed_default_buses(db)
        finally:
            db.close()

    return app


app = create_app()
