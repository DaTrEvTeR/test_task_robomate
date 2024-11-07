from pydantic import BaseModel
from typing import Any


class BaseResumeModel(BaseModel):
    cv_link: str
    last_name: str
    first_name: str
    father_name: str
    age: int
    speciality: str
    city: str
    schedule: str
    salary_expectation: int
    currency: str
    resume_filling: int
    skills: str
    educations: list[dict[str, Any]]
    experiences: list[dict[str, Any]]
    languages: list[dict[str, str]]
