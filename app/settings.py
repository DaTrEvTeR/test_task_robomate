from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from pathlib import Path


env_file = (Path(__file__).parent.parent / ".env")


class Settings(BaseSettings):
    RESUMES_URL: str = "https://employer-api.robota.ua/resume/search"
    ONE_RESUME_URL: str = "https://employer-api.robota.ua/resume/"
    processes_count: int = 4,
    process_max_connections: int = 2

    model_config = ConfigDict(extra="ignore",
        env_file=env_file if env_file.exists() else None,
        env_file_encoding = "utf-8")


settings = Settings()
