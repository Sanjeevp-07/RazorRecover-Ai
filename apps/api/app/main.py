from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.webhooks import router as webhooks_router
from app.api.v1.payments import router as payments_router
from app.api.v1.recovery_cases import router as cases_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.backtests import router as backtests_router
from app.api.v1.customers import router as customers_router
from app.api.v1.system import router as system_router

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="3.0.0",
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
            "http://localhost:3001",
            "http://127.0.0.1:3001",
        ],
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:[0-9]+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "INTERNAL_SERVER_ERROR", "message": str(exc)}},
        )

    # Mount API v1 Routers
    app.include_router(auth_router, prefix=settings.API_V1_STR)
    app.include_router(webhooks_router, prefix=settings.API_V1_STR)
    app.include_router(payments_router, prefix=settings.API_V1_STR)
    app.include_router(cases_router, prefix=settings.API_V1_STR)
    app.include_router(dashboard_router, prefix=settings.API_V1_STR)
    app.include_router(analytics_router, prefix=settings.API_V1_STR)
    app.include_router(backtests_router, prefix=settings.API_V1_STR)
    app.include_router(customers_router, prefix=settings.API_V1_STR)
    app.include_router(system_router, prefix=settings.API_V1_STR)

    @app.middleware("http")
    async def correlation_id_middleware(request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID") or request.headers.get("x-correlation-id")
        if correlation_id:
            from app.core.observability import correlation_id_ctx
            correlation_id_ctx.set(correlation_id)
        response = await call_next(request)
        if correlation_id:
            response.headers["X-Correlation-ID"] = correlation_id
        return response

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "version": "2.0.0"
        }

    @app.get("/metrics", tags=["Observability"])
    async def prometheus_metrics():
        from fastapi.responses import PlainTextResponse
        from app.core.observability import metrics
        return PlainTextResponse(
            content=metrics.generate_prometheus_metrics(),
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )

    return app

app = create_app()
