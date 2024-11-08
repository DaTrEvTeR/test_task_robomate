import logging

from aiohttp import ClientError
import asyncio
from multiprocessing import Pool
from typing import Any
from bs4 import BeautifulSoup

from app.helpers.custom_session import CustomSession
from app.helpers.resume_filter import ResumeFilter
from app.helpers.enums import (
    CityType,
    LangNameType,
    LangLevelType,
)
from app.parse_work_ua.enums import (
    work_salary_dict,
    work_exp_dict,
    work_lang_dict,
    work_lang_level_dict,
)
from app.settings import Settings
from app.parse_work_ua.work_resume_model import WorkResumeModel


class WorkUaParser:
    PER_PAGE = 14
    BASE_URL = "https://www.work.ua"
    RESUMES_URL = "https://www.work.ua/resumes"

    def __init__(
        self, filter_obj: ResumeFilter, settings: Settings, session: CustomSession
    ):
        self.filter_obj = filter_obj
        self.url = self.get_work_link()
        self.settings = settings
        self.session = session

    def get_work_link(self) -> str:
        """Returns a formatted string for request to work ua"""
        if self.filter_obj.city == 0:
            location = "-"
        else:
            location = f"-{CityType(self.filter_obj.city).name.lower()}-"

        speciality = f"{'+'.join(self.filter_obj.speciality.split(" "))}+{("+".join(self.filter_obj.main_skills))}"
        period = (
            self.filter_obj.period - 1
            if self.filter_obj.period in (3, 4)
            else self.filter_obj.period
        )
        employment = (
            0
            if self.filter_obj.schedule == 0
            else 74
            if self.filter_obj.schedule == 1
            else 75
        )

        salary_from = work_salary_dict[
            max(key for key in work_salary_dict if key <= self.filter_obj.salary_from)
        ]
        salary_to = work_salary_dict[
            min(key for key in work_salary_dict if key >= self.filter_obj.salary_to)
        ]
        experience = work_exp_dict[self.filter_obj.experience]
        languages = dict()
        for lang, lev in self.filter_obj.languages.items():
            lang_name = work_lang_dict[LangNameType(lang).value]
            lang_lev = work_lang_level_dict[LangLevelType(lev).value]
            languages[lang_name] = lang_lev
        filters_dict = {
            "notitle": "1",
            "sort": "1",
            "period": period,
            "employment": employment,
            "agefrom": self.filter_obj.age_from,
            "ageto": self.filter_obj.age_to,
            "salaryfrom": salary_from,
            "salaryto": salary_to,
            "education": self.filter_obj.education + 65,
            "experience": experience,
            "language": "+".join(str(k) for k in languages.keys()),
            "language_level": "+".join(
                [f"{lang}-{lev}" for lang, lev in languages.items()]
            ),
            "photo": int(self.filter_obj.photo),
        }
        filters_list = list()
        for k, v in filters_dict.items():
            filters_list.append(f"{k}={v}")
        filters = "&".join(filters_list)
        return f"{self.RESUMES_URL}{location}{speciality}/?{filters}"

    async def get_resumes_page(self, request_link) -> dict[str, Any]:
        """Retrieve a page of resumes from the employer API.

        Parameters
        ----------
        request_data : dict
            A dictionary containing the request parameters for fetching resumes,
            structured according to the API specifications.

        Returns
        -------
        dict
            The JSON response from the API containing the resumes and related data.
        """
        async with self.session.get(request_link) as response:
            if not response.ok:
                raise ClientError(
                    f"get_resumes_page: {response.status}: {response.reason}"
                )
            res = await response.text()
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
        async with self.session.get(self.url) as response:
            if not response.ok:
                raise ClientError(
                    f"get_page_count: {response.status}: {response.reason}"
                )
            res = await response.text()
        soup = BeautifulSoup(res, "lxml")
        total = soup.select_one(
            selector=(
                "#pjax > div > div.row > div.col-md-8 > div.flex.flex-justify-between.flex-align-flex-start "
                "> div.mt-8.text-default-7 > h1"
            )
        )
        total = int(total.text.strip().split(" ")[0])
        if total:
            page_count = (total + self.PER_PAGE - 1) // self.PER_PAGE
            if page_count:
                logging.info(f"Found {total} resumes|{page_count} pages")
                return page_count
            else:
                logging.info(f"Found {total} resumes|1 page")
                return 1
        else:
            raise ValueError("get_page_count: Resumes not found")

    async def run_parser(self) -> list[WorkResumeModel] | None:
        try:
            logging.info(f"Sending request {self.url} to work.ua...")
            page_count = await self.get_page_count()
            results = []
            for page_num in range(1, page_count + 1):
                logging.info(f"Parsing {page_num} page...")
                page_url = f"{self.url}&page={str(page_num)}"
                resumes_page = await self.get_resumes_page(page_url)
                soup = BeautifulSoup(resumes_page, "lxml")
                links = soup.select(selector=("h2.mt-0 > a"))
                resumes_links = [f"{self.BASE_URL}{a['href']}" for a in links]

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
    ) -> list[WorkResumeModel]:
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


def process_wrapper(args) -> list[WorkResumeModel]:
    """Wrapper to run asyncio tasks within a process."""
    urls, settings = args
    return asyncio.run(process_urls(urls, settings))


async def process_urls(urls: list[str], settings: Settings) -> list[WorkResumeModel]:
    """Asynchronously fetch and parse resumes in a given set of URLs."""
    async with CustomSession() as session:
        tasks = [fetch_and_parse(url, session, settings) for url in urls]
        return await asyncio.gather(*tasks)


async def fetch_and_parse(
    url: str, session: CustomSession, settings: Settings
) -> WorkResumeModel:
    """Fetch json with resume data and parse it"""
    async with asyncio.Semaphore(settings.process_max_connections):
        async with session.get(url) as response:
            if not response.ok:
                raise ClientError(
                    f"fetch_and_parse: {response.status}: {response.reason}"
                )
            html = await response.text()
    try:
        model = WorkResumeModel.from_html(html)
        logging.info(f"Parsed {url}")
        return model
    except Exception as e:
        raise ValueError(f"fetch_and_parse - error at parsing {url}: {e}")
