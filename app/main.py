from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.1.0",
    description="FastAPI application deployed on AWS EC2 with CI/CD",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "message": "Welcome to FastAPI AWS App with PR Checks", 
        "environment": settings.environment, 
        "version": "1.1.0",
        "api_version": "v1",
        "features": ["API versioning", "Containerized deployment"]
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
