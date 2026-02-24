import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from config.app_settings import AppSettings
from src.logging.logger_factory import setup_logging
from src.repositories.sqlite.database import DatabaseManager
from src.repositories.sqlite.migrations import run_migrations

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings: AppSettings = app.state.settings
    setup_logging(settings.logging)

    db_manager = DatabaseManager(settings.database)
    db = await db_manager.connect()
    await run_migrations(db)

    app.state.db_manager = db_manager
    app.state.db = db

    logger.info("Application started: %s", settings.app_name)
    yield

    await db_manager.disconnect()
    logger.info("Application shutdown")
