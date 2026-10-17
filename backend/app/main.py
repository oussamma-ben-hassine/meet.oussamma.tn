from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, AsyncSessionLocal
from app.core.seed import seed_places
from app.api.v1.endpoints.api import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_places(session)
    yield
    # Shutdown actions

app = FastAPI(
    title=settings.APP_NAME,
    description="MeetSpot — Le meilleur compromis de rencontre entre amis (Écosystème oussamma.tn)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
@app.get("/ready", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "sso": settings.SSO_BASE_URL,
        "ai_gateway": settings.LITELLM_BASE_URL
    }

app.include_router(api_router, prefix="/api/v1")
