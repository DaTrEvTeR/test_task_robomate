import asyncio

from abc import ABC, abstractmethod
from typing import Optional

from app.services.resume_python_object import ResumeModel
from app.services.custom_session import CustomSession
from app.settings import Settings


class BasePageParser(ABC):
    """Abstract base class for parsers that fetch and parse resume data."""

    def __init__(self, urls: list[str], settings: Settings):
        self.urls = urls
        self.settings = settings

    async def process_urls(self) -> list[Optional[ResumeModel]]:
        """Asynchronously fetch and parse resumes in a given list of URLs."""
        async with CustomSession() as session:
            self.session = session
            tasks = [self.fetch_and_parse(url) for url in self.urls]
            return list(await asyncio.gather(*tasks))

    @abstractmethod
    async def fetch_and_parse(self, url: str) -> Optional[ResumeModel]:
        """Abstract method to fetch the data and parse it into a ResumeModel.."""
        pass

    @abstractmethod
    def parse_resume_data(self, data) -> dict:
        """Abstract method to parse the resume data and return it as a dictionary."""
        pass
