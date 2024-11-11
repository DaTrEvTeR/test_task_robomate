import logging
import asyncio

from aiohttp import ClientError
from multiprocessing import Pool
from typing import Optional, List
from datetime import datetime
from bs4 import BeautifulSoup

from app.services.custom_session import CustomSession
from app.services.experience import Experience
from app.services.education import Education
from app.services.resume_filter import ResumeFilter
from app.services.resume_python_object import ResumeModel
from app.services.enums import CityType, ScheduleType, LangLevelType, LangNameType
from app.abc.parser import BaseParser
from app.abc.page_parser import BasePageParser


class RobotaUaParser(BaseParser):
    PER_PAGE = 20
    RESUME_URL = "https://employer-api.robota.ua/resume/"
    ALL_RESUMES_URL = "https://employer-api.robota.ua/cvdb/resumes?"

    def get_link(self, resume_filter: ResumeFilter) -> str:
        """Returns a string with all the data needed to perform a request to the robota ua API"""
        filters = self.build_filter_query(resume_filter)
        return f"{self.ALL_RESUMES_URL}{filters}"

    def build_filter_query(self, resume_filter: ResumeFilter):
        filters_dict = {
            "Sort": 0,
            "SearchType": "everywhere",
            "Ukrainian": "true",
            "CityId": resume_filter.city,
            "EducationIds": resume_filter.education if resume_filter.education else "",
            "Age.From": resume_filter.age_from,
            "Age.To": resume_filter.age_to,
            "ScheduleIds": resume_filter.schedule if resume_filter.education else "",
            "Period": resume_filter.period,
            "ExperienceIds": resume_filter.experience
            if resume_filter.education
            else "",
            "KeyWords": f"{'%20'.join(resume_filter.speciality.split(" "))}%20{("%20".join(resume_filter.main_skills))}",
            "Languages": "&".join(
                [f"Languages={k}-{v}" for k, v in resume_filter.languages.items()]
            ),
            "HasPhoto": resume_filter.photo,
        }
        if resume_filter.salary_from:
            filters_dict["Salary.From"] = resume_filter.salary_from
        if resume_filter.salary_to:
            filters_dict["Salary.To"] = resume_filter.salary_to
        return "&".join(f"{k}={v}" for k, v in filters_dict.items())

    async def get_resumes_page(self, request_link: str):
        """Retrieve a page from the url"""
        async with self.session.get(request_link) as response:
            if not response.ok:
                raise ClientError(
                    f"get_resumes_page: {response.status}: {response.reason}"
                )
            res = await response.json()
        return res

    async def get_page_count(self) -> int:
        """Retrieve a page count.

        Parameters
        ----------
        request_data : dict
            A dictionary containing the request parameters for fetching resumes,
            structured according to the API specifications.

        Returns
        -------
        int
            Number of resume pages found using special filters.
        """
        res = await self.get_resumes_page(self.url)
        total = res["total"]
        if total:
            page_count = (total + 19) // 20
            if page_count:
                logging.info(f"Found {total} resumes|{page_count} pages")
                return page_count
            else:
                logging.info(f"Found {total} resumes|1 page")
                return 1
        else:
            raise ValueError("get_page_count: Resumes not found")

    async def run_parser(self) -> List[Optional[ResumeModel]] | None:
        """Asynchronously retrieves and parses resumes from the Robota.ua API.

        This method first determines the total number of pages to parse, then iterates over each page
        to gather resume links and parse the data for each resume link found. Resumes are parsed into
        `ResumeModel` objects.

        Returns:
        -------
        list[ResumeModel] | None
            A list of `ResumeModel` instances containing parsed resume data, or None if no resumes were found.
        """
        try:
            async with CustomSession() as session:
                self.session = session
                logging.info(f"Sending request {self.url} to robota.ua api...")
                page_count = await self.get_page_count()
                results = []
                for page_num in range(page_count):
                    logging.info(f"Parsing {page_num+1} page...")
                    url = f"{self.url}&page={str(page_num)}"
                    resumes_page = await self.get_resumes_page(url)
                    resumes_links = []

                    for document in resumes_page["documents"]:
                        resumes_links.append(f"{self.RESUME_URL}{document['resumeId']}")

                    results.append(
                        self.get_resumes_data_from_urls(resumes_urls=resumes_links)
                    )
            res = []
            for url_group in results:
                res.extend(url_group)
            logging.info(f"Parsing finished\nParsed {len(res)} resumes")
            return res
        except Exception as e:
            logging.error(e)
            return None

    def get_resumes_data_from_urls(
        self, resumes_urls: list[str]
    ) -> list[Optional[ResumeModel]]:
        """Retrieve product data from a list of URLs using multiple processes.

        Parameters
        ----------
        resumes_urls : list of str
            List of resumes URLs to fetch data from.

        Returns
        -------
        list
            Combined list of parsed resumes data from all processes.
        """
        url_groups = self.split_urls(urls=resumes_urls)

        with Pool(processes=self.settings.processes_count) as pool:
            results = pool.map(
                process_wrapper,
                [(url_group, self.settings) for url_group in url_groups],
            )

        res = []
        for url_group in results:
            res.extend(url_group)
        return res

    def split_urls(self, urls: list[str]):
        """Split a list of URLs into smaller chunks.

        Parameters
        ----------
        urls : list of str
            List of URLs to split.

        Returns
        -------
        list of list of str
            A list containing the split chunks of URLs.
        """
        chunk_len = (
            len(urls) + self.settings.processes_count - 1
        ) // self.settings.processes_count
        return (
            [urls[i : i + chunk_len] for i in range(0, len(urls), chunk_len)]
            if chunk_len
            else []
        )


def process_wrapper(args) -> list[Optional[ResumeModel]]:
    """Wrapper to run asyncio tasks within a process."""
    urls, settings = args
    page_parser = RobotaUaPageParser(urls=urls, settings=settings)
    return asyncio.run(page_parser.process_urls())


class RobotaUaPageParser(BasePageParser):
    """A class to fetch, parse, and convert resumes from the Robota.ua platform into structured data models.

    This parser asynchronously retrieves resume data from given URLs, processes each response into
    a `ResumeModel`, and handles errors gracefully. It uses a configurable session and settings to manage
    connection limits and timeout values.

    Attributes:
    ----------
    CANDIDATES_URL : str
        Base URL for accessing candidate profiles on Robota.ua.

    urls : list[str]
        A list of URLs from which resume data will be fetched.

    settings : Settings
        Configuration settings, such as maximum connections, to control the request behavior."""

    CANDIDATES_URL = "https://robota.ua/candidates/"

    async def fetch_and_parse(self, url: str) -> Optional[ResumeModel]:
        """Fetch json with resume data and parse it"""
        async with asyncio.Semaphore(self.settings.process_max_connections):
            async with self.session.get(url) as response:
                if not response.ok:
                    logging.error(
                        f"fetch_and_parse: {response.status}: {response.reason}"
                    )
                    return None
                response = await response.json()
        try:
            res = self.parse_resume_data(response)
            model = ResumeModel(**res)
            logging.info(f"Parsed {url}")
            return model
        except Exception as e:
            logging.error(f"fetch_and_parse - error at parsing {url}: {e}")
            return None

    def parse_resume_data(self, data: dict) -> dict:
        """Parses all the data needed to create a ResumeModel from json and returns a dict"""
        educations = list()
        education = 5
        for edu in data.get("educations", []):
            educations.append(
                Education(
                    name=edu.get("name", ""),
                    comment=BeautifulSoup(edu["comment"], "html.parser").text,
                    location=edu.get("location", ""),
                    speciality=edu.get("speciality", ""),
                    year_of_graduation=edu.get("yearOfGraduation", 0),
                )
            )
            ed_id = edu["educationId"]
            if ed_id != 0 and ed_id < education:
                education = ed_id
        if education == 5:
            education = 0
        return {
            "cv_link": f"{self.CANDIDATES_URL}{data["resumeId"]}",
            "last_name": data.get("surname", ""),
            "first_name": data.get("name", ""),
            "father_name": data.get("fatherName", ""),
            "age": int(data["age"].split(" ")[0] if data["age"] else 0),
            "speciality": data.get("speciality", ""),
            "city": str(CityType(data["cityId"])) if data["cityId"] in CityType else "",
            "schedule": str(ScheduleType(data["scheduleId"])),
            "salary_expectation": int(data.get("salary", 0)),
            "currency": data.get("currencySign", "")
            if int(data.get("salary", 0)) != 0
            else "",
            "resume_filling": data.get("fillingPercentage", 0),
            "skills": ", ".join(
                [skill.get("description") for skill in data.get("skills", [])]
            ),
            "educations": [
                Education(
                    name=edu.get("name", ""),
                    comment=BeautifulSoup(edu["comment"], "html.parser").text,
                    location=edu.get("location", ""),
                    speciality=edu.get("speciality", ""),
                    year_of_graduation=edu.get("yearOfGraduation", 0),
                )
                for edu in data.get("educations", [])
            ],
            "experiences": [
                Experience(
                    position=exp.get("position", ""),
                    company=exp.get("company", ""),
                    description=BeautifulSoup(exp["description"], "html.parser").text,
                    period=round(
                        (
                            (
                                datetime.fromisoformat(exp["endWork"])
                                if exp["endWork"]
                                else datetime.now()
                            )
                            - datetime.fromisoformat(exp["startWork"])
                        ).days
                        / 365.25,
                        1,
                    ),
                )
                for exp in data.get("experiences", [])
            ],
            "languages": [
                {
                    LangNameType(lang["languageId"]).value: LangLevelType(
                        lang["languageSkillId"]
                    ).value
                }
                for lang in data.get("languageSkills", [])
            ],
            "education": education,
        }
