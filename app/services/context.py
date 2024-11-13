import logging

from typing import Type

from app.abc.parser import BaseParser
from app.services.resume_filter import ResumeFilter
from app.services.resume_python_object import ResumeModel
from app.settings import Settings, settings


class ParseContext:
    def __init__(
        self,
        parser_cls: Type[BaseParser] | None = None,
        filter_obj: ResumeFilter = ResumeFilter(),
        settings: Settings = settings,
    ) -> None:
        self._parser_cls = parser_cls
        self._filter_obj = filter_obj
        self._settings = settings

    @property
    def parser_cls(self) -> Type[BaseParser] | None:
        return self._parser_cls

    @parser_cls.setter
    def parser_cls(self, parser_cls: Type[BaseParser]) -> None:
        if issubclass(parser_cls, BaseParser):
            self._parser_cls = parser_cls
            logging.info(f"Parser class changed to {parser_cls}")
        else:
            logging.warning(f"{parser_cls} is invalid parser class type")

    @property
    def filter_obj(self) -> ResumeFilter:
        return self._filter_obj

    @filter_obj.setter
    def filter_obj(self, filter_obj: ResumeFilter) -> None:
        if isinstance(filter_obj, ResumeFilter):
            self._filter_obj = filter_obj
            logging.info(f"Filter changed to {filter_obj}")
        else:
            logging.warning(f"{filter_obj} is invalid filter type")

    @property
    def settings(self) -> Settings:
        return self._settings

    @settings.setter
    def settings(self, settings: Settings) -> None:
        if isinstance(settings, Settings):
            self._settings = settings
            logging.info(f"Settings changed to {settings}")
        else:
            logging.warning(f"{settings} is invalid settings type")

    async def parse(self) -> list[ResumeModel] | None:
        # Create an instance of the parser class
        if self._parser_cls and self._filter_obj.speciality:
            parser_instance = self._parser_cls(self._filter_obj, self._settings)
            return await parser_instance.run_parser()
        else:
            raise ValueError("Speciality in filter or parser class is not specified")
