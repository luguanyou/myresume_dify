from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "portfolio-api"
    api_version: str = "1.0"
    api_title: str = "AI Resume Portfolio API"
    app_root_path: str = ""
    cors_origins: str = "http://localhost:5173"

    dify_api_base_url: str = "https://api.dify.ai/v1"
    dify_api_key: str = ""

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_database: str = "portfolio"
    mysql_user: str = "portfolio_user"
    mysql_password: str = "123456"

    admin_jwt_secret: str = ""
    admin_token_expire_seconds: int = 86400

    upload_dir: str = "uploads"
    public_api_base_url: str = "/api"
    public_upload_base_url: str = "/uploads"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{quote_plus(self.mysql_password)}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
            "?charset=utf8mb4"
        )

    @property
    def token_secret(self) -> str:
        return self.admin_jwt_secret or "dev-only-admin-token-secret"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
