"""Application configuration."""
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


class Settings(BaseSettings):
    """App settings loaded from environment or defaults."""

    app_name: str = "VocabFusion Learning System"
    secret_key: str = "vocab-fusion-demo-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = f"sqlite:///{DATA_DIR / 'vocab.db'}"
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    log_level: str = "INFO"
    default_alpha: float = 0.6
    embedding_dim: int = 64

    class Config:
        env_file = ".env"


settings = Settings()
