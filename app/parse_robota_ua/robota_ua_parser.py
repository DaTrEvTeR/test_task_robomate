import logging

from aiohttp import ClientError
import asyncio
from multiprocessing import Pool
from typing import Any

from app.helpers.custom_session import CustomSession
from app.helpers.resume_filter import ResumeFilter
from app.helpers.resume_python_object import ResumeModel
from app.settings import Settings


class RobotaUaParser:
    def __init__(
        self, filter_obj: ResumeFilter, settings: Settings, session: CustomSession
    ):
        self.filter_obj = filter_obj
        self.settings = settings
        self.session = session

    async def get_resumes_page(self, request_data) -> dict[str, Any]:
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
        async with self.session.post(
            self.settings.RESUMES_URL, json=request_data
        ) as response:
            if not response.ok:
                raise ClientError(
                    f"get_resumes_page: {response.status}: {response.reason}"
                )
            res = await response.json()
        return res

    async def get_page_count(self, request_data) -> int:
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
        async with self.session.post(
            self.settings.RESUMES_URL, json=request_data
        ) as response:
            if not response.ok:
                raise ClientError(
                    f"get_page_count: {response.status}: {response.reason}"
                )
            res = await response.json()
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

    async def run_parser(self) -> list[ResumeModel] | None:
        req_data = self.filter_obj.robota_request()
        logging.info(f"Sending request {req_data} to robota.ua api...")
        try:
            page_count = await self.get_page_count(req_data)
            results = []
            for page_num in range(page_count):
                logging.info(f"Parsing {page_num+1} page...")
                req_data["page"] = page_num
                resumes_page = await self.get_resumes_page(req_data)
                resumes_links = []

                for document in resumes_page["documents"]:
                    resumes_links.append(
                        f"{self.settings.ONE_RESUME_URL}{document['resumeId']}"
                    )

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

    def get_resumes_data_from_urls(self, resumes_urls: list[str]) -> list[ResumeModel]:
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


def process_wrapper(args) -> list[ResumeModel]:
    """Wrapper to run asyncio tasks within a process."""
    urls, settings = args
    return asyncio.run(process_urls(urls, settings))


async def process_urls(urls: list[str], settings: Settings) -> list[ResumeModel]:
    """Asynchronously fetch and parse resumes in a given set of URLs."""
    async with CustomSession() as session:
        tasks = [fetch_and_parse(url, session, settings) for url in urls]
        return await asyncio.gather(*tasks)


async def fetch_and_parse(
    url: str, session: CustomSession, settings: Settings
) -> ResumeModel:
    """Fetch json with resume data and parse it"""
    async with asyncio.Semaphore(settings.process_max_connections):
        async with session.get(url) as response:
            if not response.ok:
                raise ClientError(
                    f"fetch_and_parse: {response.status}: {response.reason}"
                )
            res = await response.json()
    model = ResumeModel(**res)
    if isinstance(model, ResumeModel):
        logging.info(f"Parse {url}")
    else:
        raise ValueError(f"Resume {url} didn`t parse: {model}")
    return model
