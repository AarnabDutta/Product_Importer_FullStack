# Settings (DB, Redis, env vars)
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    celery_broker_url: str
    celery_result_backend: str
    upload_dir: str = "./uploads"
    max_upload_size: int = 524288000
    chunk_size: int = 10000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
