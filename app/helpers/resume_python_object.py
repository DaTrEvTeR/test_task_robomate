from pydantic import BaseModel
from typing import Any


class BaseResumeModel(BaseModel):
    cv_link: str
    last_name: str = ""
    first_name: str
    father_name: str = ""
    age: int = 0
    speciality: str
    city: str = ""
    schedule: str = ""
    salary_expectation: int = 0
    currency: str = ""
    resume_filling: int
    skills: str = ""
    educations: list[dict[str, Any]] = list()
    experiences: list[dict[str, Any]] = list()
    languages: list[dict[str, str]] = list()
