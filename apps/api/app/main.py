from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.webhooks import router as webhooks_router
from app.api.v1.payments import router as payments_router
from app.api.v1.recovery_cases import router as cases_router
from app.api.v1.dashboard import router as dashboard_router

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="2.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Configure CORS with explicit allowed origins & regex
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ],
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:[0-9]+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount API v1 Routers
    app.include_router(auth_router, prefix=settings.API_V1_STR)
    app.include_router(webhooks_router, prefix=settings.API_V1_STR)
    app.include_router(payments_router, prefix=settings.API_V1_STR)
    app.include_router(cases_router, prefix=settings.API_V1_STR)
    app.include_router(dashboard_router, prefix=settings.API_V1_STR)

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "version": "2.0.0"
        }

    return app

app = create_app()
