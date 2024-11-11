import logging
import re

from aiohttp import ClientError
import asyncio
from multiprocessing import Pool
from bs4 import BeautifulSoup
from typing import Optional, List

from app.services.custom_session import CustomSession
from app.services.experience import Experience
from app.services.education import Education
from app.services.resume_filter import ResumeFilter
from app.services.resume_python_object import ResumeModel
from app.services.enums import (
    CityType,
    LangNameType,
    LangLevelType,
)
from app.parse_work_ua.enums import (
    work_salary_dict,
    work_exp_dict,
    work_lang_dict,
    work_lang_level_dict,
    work_str_lang_dict,
    work_str_lang_level_dict,
    work_str_education_dict,
)
from app.abc.parser import BaseParser
from app.abc.page_parser import BasePageParser


class WorkUaParser(BaseParser):
    PER_PAGE = 14
    BASE_URL = "https://www.work.ua"
    RESUMES_URL = "https://www.work.ua/resumes"

    def get_link(self, resume_filter: ResumeFilter) -> str:
        """Returns a formatted string for request to work ua"""
        location, speciality, filters = self.build_filter_query(resume_filter)
        return f"{self.RESUMES_URL}{location}{speciality}/?{filters}"

    def build_filter_query(self, resume_filter: ResumeFilter):
        if resume_filter.city == 0:
            location = "-"
        else:
            location = f"-{CityType(resume_filter.city).name.lower()}-"

        speciality = f"{'+'.join(resume_filter.speciality.split(" "))}+{("+".join(resume_filter.main_skills))}"
        period = (
            resume_filter.period - 1
            if resume_filter.period in (3, 4)
            else resume_filter.period
        )
        employment = (
            0
            if resume_filter.schedule == 0
            else 74
            if resume_filter.schedule == 1
            else 75
        )

        salary_from = work_salary_dict[
            max(key for key in work_salary_dict if key <= resume_filter.salary_from)
        ]
        salary_to = work_salary_dict[
            min(key for key in work_salary_dict if key >= resume_filter.salary_to)
        ]
        experience = work_exp_dict[resume_filter.experience]
        languages = dict()
        for lang, lev in resume_filter.languages.items():
            lang_name = work_lang_dict[LangNameType(lang).value]
            lang_lev = work_lang_level_dict[LangLevelType(lev).value]
            languages[lang_name] = lang_lev
        filters_dict = {
            "notitle": "1",
            "sort": "1",
            "period": period,
            "employment": employment,
            "agefrom": resume_filter.age_from,
            "ageto": resume_filter.age_to,
            "salaryfrom": salary_from,
            "salaryto": salary_to,
            "education": resume_filter.education + 65,
            "experience": experience,
            "language": "+".join(str(k) for k in languages.keys()),
            "language_level": "+".join(
                [f"{lang}-{lev}" for lang, lev in languages.items()]
            ),
            "photo": int(resume_filter.photo),
        }
        filters_list = list()
        for k, v in filters_dict.items():
            filters_list.append(f"{k}={v}")
        filters = "&".join(filters_list)
        return location, speciality, filters

    async def get_resumes_page(self, request_link):
        """Retrieve a page from the url"""
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
        res = await self.get_resumes_page(self.url)
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

    async def run_parser(self) -> List[Optional[ResumeModel]] | None:
        try:
            async with CustomSession() as session:
                self.session = session
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
    page_parser = WorkUaPageParser(urls=urls, settings=settings)
    return asyncio.run(page_parser.process_urls())


class WorkUaPageParser(BasePageParser):
    """A class for parsing resume pages from Work.ua. It fetches the page data asynchronously,
    processes the content, and returns a `ResumeModel` based on the parsed data

    Attributes:
    ----------
    urls : list[str]
        A list of URLs from which resume data will be fetched.

    settings : Settings
        Configuration settings, such as maximum connections, to control the request behavior"""

    async def fetch_and_parse(self, url: str) -> ResumeModel | None:
        """Fetch json with resume data and parse it"""
        async with asyncio.Semaphore(self.settings.process_max_connections):
            async with self.session.get(url) as response:
                if not response.ok:
                    raise ClientError(
                        f"fetch_and_parse: {response.status}: {response.reason}"
                    )
                html = await response.text()
        try:
            res = self.parse_resume_data(html)
            model = ResumeModel(**res)
            logging.info(f"Parsed {url}")
            return model
        except Exception as e:
            logging.error(f"fetch_and_parse - error at parsing {url}: {e}")
            return None

    def parse_resume_data(self, html: str) -> dict:
        """Parses all the data needed to create a ResumeModel from html and returns a dict"""
        soup = BeautifulSoup(html, "lxml")

        resume_filling = 0

        cv_link = soup.select_one("head > link[rel='canonical']")["href"]
        first_name = soup.select_one("div.row > div > div > h1.mt-0.mb-0").text.strip()

        age = 0
        if age_title := soup.find("dt", string="Вік:"):
            age_text = age_title.find_next_sibling("dd").text.strip()
            age = int(age_text.split("\xa0")[0] if age_text else 0)

        speciality = (
            soup.select_one("div.row > div > div > h2")
            .find(string=True, recursive=False)
            .strip()
        )

        city_title = soup.find("dt", string=re.compile(r"Місто(:| проживання:)"))
        city = city_title.find_next_sibling("dd").text.strip() if city_title else None

        schedule_title = soup.find("dt", string="Зайнятість:")
        schedule = (
            schedule_title.find_next_sibling("dd").text.strip()
            if schedule_title
            else ""
        )

        salary_expectation, currency = 0, ""
        if salary_block := soup.select_one(
            "div.row > div > div > h2 > span.text-muted-print"
        ):
            salary_block = salary_block.text[2:].split("\xa0")
            salary_expectation = int("".join(salary_block[:-1]))
            currency = salary_block[-1]

        skills = ", ".join([skill.text for skill in soup.select("span.ellipsis")])
        resume_filling += (
            len(skills.split(", ")) * 4 if len(skills.split(", ")) < 10 else 40
        )
        if soup.find("span", attrs={"class": "label label-violet-light"}):
            add_info = soup.select_one("div#add_info")
            if add_info:
                skills = re.sub(
                    r"\[відкрити контакти\]\(див\. вище в блоці «контактна інформація»\)",
                    "",
                    re.sub(r"\s+", " ", add_info.text.strip()),
                )

        siblings: list = []
        if ed_title := soup.find("h2", string="Освіта"):
            list_ind = -1
            for sibling in ed_title.find_next_siblings():
                if sibling.name == "h2" and sibling.get(
                    "class"
                ) != "h4 strong-600 mt-lg sm:mt-xl".split(" "):
                    break
                if sibling.get("class") == "h4 strong-600 mt-lg sm:mt-xl".split(" "):
                    siblings.append([])
                    list_ind += 1
                siblings[list_ind].append(sibling)

        educations = []
        education = 5
        for ed in siblings:
            name = ed[0].text
            comment = ed[2].text if len(ed) == 3 else ""
            desc_split = ed[1].get_text(" ", strip=True)
            spec = desc_split.split(",")[0].strip()
            ed_str = desc_split.split(",")[1].split("з")[0].strip()
            year_of_graduation = desc_split.split("по")[-1].strip()
            educations.append(
                Education(
                    name=name,
                    comment=comment,
                    speciality=spec,
                    year_of_graduation=int(year_of_graduation),
                )
            )
            ed_id = work_str_education_dict[ed_str]
            if ed_id != 0 and ed_id < education:
                education = ed_id
        if education == 5:
            education = 0
        resume_filling += 20 if educations else 0

        ex_siblings: list = []
        if ex_title := soup.find("h2", string="Досвід роботи"):
            list_ind = -1
            for sibling in ex_title.find_next_siblings():
                if sibling.name == "h2" and sibling.get(
                    "class"
                ) != "h4 strong-600 mt-lg sm:mt-xl".split(" "):
                    break
                if sibling.get("class") == "h4 strong-600 mt-lg sm:mt-xl".split(" "):
                    ex_siblings.append([])
                    list_ind += 1
                ex_siblings[list_ind].append(sibling)

        experiences = []
        for ex in ex_siblings:
            position = ex[0].text
            description = ex[2].text if len(ex) == 3 else ""
            period_str = (
                ex[1].select_one("span.text-default-7").text[1:-1].split("\xa0")
            )
            if len(period_str) == 4:
                period = round(int(period_str[0]) + int(period_str[2]) / 12, 1)
            elif len(period_str) == 1:
                period = round(1 / 12, 1)
            elif "м" == period_str[1][0]:
                period = round(int(period_str[0]) / 12, 1)
            else:
                period = round(int(period_str[0]), 1)
            company = ex[1].text.split("\n")[-1].strip()
            experiences.append(
                Experience(
                    position=position,
                    company=company,
                    description=description,
                    period=period,
                )
            )
        resume_filling += 20 if experiences else 0

        languages = []
        if langs := soup.find("h2", string="Знання мов"):
            if (
                langs.find_next_sibling("ul")
                and langs.find_next_sibling("ul").get("class") is None
            ):
                langs = langs.find_next_sibling("ul").select("li")
                for lang in langs:
                    t = lang.text.split(" — ")
                    languages.append({t[0]: t[1]})
            else:
                t = langs.find_next_sibling("p").text.split(" — ")
                languages.append(
                    {work_str_lang_dict[t[0]]: work_str_lang_level_dict[t[1]]}
                )
        resume_filling += 20 if languages else 0

        return {
            "cv_link": cv_link,
            "last_name": "",
            "first_name": first_name,
            "father_name": "",
            "age": age,
            "speciality": speciality,
            "city": city,
            "schedule": schedule,
            "salary_expectation": salary_expectation,
            "currency": currency,
            "resume_filling": resume_filling,
            "skills": skills,
            "educations": educations,
            "experiences": experiences,
            "languages": languages,
            "education": education,
        }
