import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

  REDIS_URL: str = "redis://localhost:6379"

  MAX_RETRIES: int = 3
  WORKER_COUNT: int = Field(default_factory=lambda: max(1, os.cpu_count() - 1), ge=1, le=100)

  DELAYED_KEY: str = "delayed_tasks"
  EXECUTING_KEY: str = "execution_queue"
  DEAD_LETTER_KEY: str = "dead_letter_queue"


config = Settings()