from pydantic import BaseModel

from app.services.education import Education
from app.services.experience import Experience
from app.services.enums import EducationType, CityType


class ResumeModel(BaseModel):
    cv_link: str
    last_name: str = ""
    first_name: str
    father_name: str = ""
    age: int = 0
    speciality: str
    city: int = CityType.ALL_UKRAINE.value
    schedule: int = 0
    salary_expectation: int = 0
    currency: str = ""
    resume_filling: int
    skills: str = ""
    educations: list[Education] = list()
    experiences: list[Experience] = list()
    languages: dict[int, int] = dict()
    education: int = EducationType.ANY.value
