from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str
    GEMINI_API_KEY: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # .env dosyasını otomatik okuması için
    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()