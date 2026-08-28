from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import build_router
from app.config import Settings
from app.core.adapters.registry import AdapterRegistry
from app.core.errors import AppError
from app.core.file_store import JsonFileStore

logger = logging.getLogger("log_parser")


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()
    app = FastAPI(title="Log Parser API", version="1.0.0")
    app.state.settings = config
    app.state.store = JsonFileStore(config.store_dir)
    app.state.registry = AdapterRegistry(
        trade_script=None,
        timeout_seconds=config.script_timeout_seconds,
    )
    app.state.sample_source_dir = config.sample_source_dir
    app.state.search_roots = config.search_roots

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppError)
    async def handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
        logger.warning("app_error", extra={"code": exc.code, "detail": exc.message})
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.code, "message": exc.message},
        )

    app.include_router(build_router(), prefix="/api")
    return app


app = create_app()
