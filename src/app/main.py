from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from config.app_settings import AppSettings
from src.app.lifespan import lifespan
from src.exceptions.handlers import register_exception_handlers
from src.routers import admin_router, auth_router, match_router, token_router, user_router


def create_app() -> FastAPI:
    settings = AppSettings()

    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
    )
    app.state.settings = settings

    register_exception_handlers(app)

    app.include_router(auth_router.router)
    app.include_router(user_router.router)
    app.include_router(match_router.router)
    app.include_router(token_router.router)
    app.include_router(admin_router.router)

    app.mount("/", StaticFiles(directory="static", html=True), name="static")

    return app
