from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.auth import router as auth_router

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="2.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount API v1 Routers
    app.include_router(auth_router, prefix=settings.API_V1_STR)

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "version": "2.0.0"
        }

    return app

app = create_app()
