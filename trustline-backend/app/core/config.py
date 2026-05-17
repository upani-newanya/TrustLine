# Central settings loader from .env using pydantic-settings.
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TrustLine Backend"
    api_prefix: str = "/api/v1"

    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    upload_dir: str = "app/uploads/evidence"
    max_upload_size_mb: int = 25

    # ML model paths (local Hugging Face models)
    suicide_model_path: str = "./ml_models/suicide_model_distilbert_cpu_v2"
    emotion_model_path: str = "./ml_models/emotion_model_distilbert_cpu_4class_best"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
