from abc import ABC, abstractmethod
from typing import List

from app.services.resume_filter import ResumeFilter
from app.services.resume_python_object import ResumeModel
from app.settings import Settings


class BaseParser(ABC):
    """Abstract class for the main parser class"""

    def __init__(self, filter_obj: ResumeFilter, settings: Settings):
        """
        Initializes the BaseParser with the given filter and settings.

        Args:
            filter_obj (ResumeFilter): The filter object containing the filter criteria for resumes.
            settings (Settings): The settings object containing configuration options.
        """
        self.url = self.get_link(
            filter_obj
        )  # Calls the get_link method to generate the URL
        self.settings = settings

    @abstractmethod
    def get_link(self, resume_filter: ResumeFilter) -> str:
        """
        Abstract method to generate the URL based on the given filter.

        Args:
            resume_filter (ResumeFilter): The filter object containing search criteria.

        Returns:
            str: The URL generated based on the filter.
        """
        pass

    @abstractmethod
    async def run_parser(self) -> List[ResumeModel] | None:
        """
        Abstract method for running the parsing process. This method will be
        implemented in subclasses to handle the actual parsing logic.

        Returns:
            List[ResumeModel] | None: A list of parsed resumes or None if no data is found or parsing fails.
        """
        pass
