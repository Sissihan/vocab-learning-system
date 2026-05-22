"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, content, context, games, learning, recommend, user
from app.api.learning import knowledge_router
from app.config import settings
from app.database import init_db

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("%s started", settings.app_name)
    yield


app = FastAPI(
    title=settings.app_name,
    description="Context-aware root-semantic fusion vocabulary learning system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(recommend.router)
app.include_router(learning.router)
app.include_router(knowledge_router)
app.include_router(games.router)
app.include_router(content.router)
app.include_router(context.router)


@app.get("/")
def root():
    from app.i18n import SUPPORTED_LANGS

    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "algorithm": "Score = α × R_sim + (1-α) × S_sim",
        "supported_languages": list(SUPPORTED_LANGS),
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
