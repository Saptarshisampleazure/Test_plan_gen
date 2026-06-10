from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
STORAGE_DIR = BASE_DIR / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
EXPORT_DIR = STORAGE_DIR / "exports"


class Settings(BaseSettings):
    app_name: str = "SRS QA Forge API"
    app_env: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    frontend_origin: str = "http://127.0.0.1:5173"
    jwt_secret_key: str = Field(default="change-this-secret-for-production")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480
    default_username: str = "admin"
    default_password: str = "admin123"
    max_upload_size_mb: int = 25
    colab_srs_base_url: str = Field(default="")
    colab_srs_generate_path: str = Field(default="/generate-srs")
    colab_srs_fallback_paths: str = Field(default="/generate-srs,/generate,/api/generate,/")
    colab_srs_local_fallback: bool = Field(default=True)
    colab_srs_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("COLAB_SRS_API_KEY", "SRS_API_KEY"),
    )
    colab_srs_model: str = Field(default="qwen2.5:7b")
    colab_srs_temperature: float = Field(default=0.2)
    colab_srs_num_predict: int | None = Field(default=2500)
    colab_srs_num_ctx: int | None = Field(default=8192)
    colab_srs_format: str = Field(default="json")
    colab_srs_timeout_seconds: int | None = Field(default=600)
    max_prompt_document_chars: int = Field(default=24000)

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
