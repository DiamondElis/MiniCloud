from fastapi import FastAPI

from app.api import access_keys, authorization, groups, policies, roles, sts, tokens, users


def create_app() -> FastAPI:
    app = FastAPI(title="MiniCloud IAM Service", version="0.1.0")
    app.include_router(users.router)
    app.include_router(groups.router)
    app.include_router(roles.router)
    app.include_router(policies.router)
    app.include_router(access_keys.router)
    app.include_router(tokens.router)
    app.include_router(sts.router)
    app.include_router(authorization.router)
    return app


app = create_app()

