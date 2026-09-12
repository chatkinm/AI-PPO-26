from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import List
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    # Google AI Studio API
    google_api_key: str = ""
    llm_model: str = "gemma-4-31b-it"
    llm_fallback_model: str = "gemini-2.5-flash"

    # Groq Cloud API
    groq_api_key: str = ""
    groq_whisper_model: str = "whisper-large-v3"

    # Figma / FigJam API
    figma_access_token: str = ""

    # Server settings
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    debug: bool = True

    # CORS
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    # Paths
    base_dir: Path = BASE_DIR
    storage_dir: Path = BASE_DIR / "backend" / "storage"
    uploads_dir: Path = BASE_DIR / "backend" / "storage" / "uploads"
    output_dir: Path = BASE_DIR / "backend" / "storage" / "output"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

settings = Settings()

# Ensure directories exist
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
settings.output_dir.mkdir(parents=True, exist_ok=True)
