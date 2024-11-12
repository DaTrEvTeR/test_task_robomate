from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from pathlib import Path


env_file = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    processes_count: int = 4
    process_max_connections: int = 2

    BOT_TOKEN: str

    BOT_PULL_CMD: str = "pull"
    BOT_SEARCH_CMD: str = "search"

    model_config = ConfigDict(
        extra="ignore",
        env_file=env_file if env_file.exists() else None,
        env_file_encoding="utf-8",
    )

    @property
    def start_msg(self) -> str:
        return (
            "Hi, this bot will help you find the perfect candidate for your vacancy, "
            f"use the /{self.BOT_PULL_CMD} command to start searching"
        )


settings = Settings()
