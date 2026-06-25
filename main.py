import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown logic."""
    logger.info("Application starting up...")
    # e.g. initialise DB connection pool, warm caches, etc.
    yield
    logger.info("Application shutting down...")
    # e.g. close DB connections, flush queues, etc.


# ─────────────────────────────────────────────
# App factory
# ─────────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title="My FastAPI App",
        description="FastAPI application running with Gunicorn + UvicornWorker",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware ───────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],   # restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ─────────────────────────────
    # from app.api.v1 import router as v1_router
    # app.include_router(v1_router, prefix="/api/v1")

    # ── Exception handlers ───────────────────
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    return app


app = create_app()


# Health endpoint  (used by Docker HEALTHCHECK)
@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    status_code=status.HTTP_200_OK,
)
async def health() -> dict:
    return {"status": "ok"}