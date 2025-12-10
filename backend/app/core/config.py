from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache
from typing import List, Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    # App settings
    APP_NAME: str = "Strands Agents GUI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 58431

    # Domain settings (for custom domain deployment)
    DOMAIN_NAME: Optional[str] = None
    USE_HTTPS: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://strands:strands@db:5432/strands_gui"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT settings
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS - stored as string, parsed to list
    CORS_ORIGINS: str = "http://localhost:58431,http://127.0.0.1:58431"

    # Strands SDK settings
    DEFAULT_MODEL_PROVIDER: str = "bedrock"
    TOOLS_DIRECTORY: str = "/app/tools"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list and add domain if configured."""
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

        # Add domain-based origins if DOMAIN_NAME is configured
        if self.DOMAIN_NAME:
            domain = self.DOMAIN_NAME.strip()
            if domain:
                protocol = "https" if self.USE_HTTPS else "http"
                domain_origin = f"{protocol}://{domain}"
                if domain_origin not in origins:
                    origins.append(domain_origin)
                # Also add without port for flexibility
                if self.USE_HTTPS:
                    # Add http variant as well for flexibility
                    http_origin = f"http://{domain}"
                    if http_origin not in origins:
                        origins.append(http_origin)

        return origins

    @property
    def base_url(self) -> str:
        """Get the base URL for the application."""
        if self.DOMAIN_NAME:
            protocol = "https" if self.USE_HTTPS else "http"
            return f"{protocol}://{self.DOMAIN_NAME}"
        return f"http://localhost:{self.PORT}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
