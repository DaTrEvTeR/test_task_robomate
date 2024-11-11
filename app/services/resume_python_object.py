from pydantic import BaseModel

from app.services.education import Education
from app.services.experience import Experience
from app.services.enums import LangNameType, LangLevelType


class ResumeModel(BaseModel):
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
    educations: list[Education] = list()
    experiences: list[Experience] = list()
    languages: list[dict[LangNameType, LangLevelType]] = list()
