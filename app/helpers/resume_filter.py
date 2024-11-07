from pydantic import BaseModel, Field
from typing import Any

from app.helpers.enums import (
    CityType,
    EducationType,
    ScheduleType,
    PeriodType,
    ExperienceType,
)


class ResumeFilter(BaseModel):
    speciality: str
    # main skills for request
    main_skills: list[str] = Field(default=[""], max_length=3)
    city: int = Field(default=CityType.ALL_UKRAINE.value)
    moveability: bool = Field(default=False)
    education: int = Field(default=EducationType.ANY.value)
    age_from: int = Field(default=0, ge=0, le=100)
    age_to: int = Field(default=0, ge=0, le=100)
    salary_from: int = Field(default=0, ge=0)
    salary_to: int = Field(default=0, ge=0)
    schedule: int = Field(default=ScheduleType.ANY.value)
    languages: dict[int, int] = Field(default=dict())
    period: int = Field(default=PeriodType.YEAR.value)
    experience: int = Field(default=ExperienceType.ANY.value)
    photo: bool = Field(default=False)
    # keywords for gaining scores
    keywords: list[str] = Field(default=[""])

    def robota_request(self) -> dict[str, Any]:
        """Returns a dictionary with all the data needed to perform a request to the robota ua API"""
        main_skills = " ".join(kw for kw in self.main_skills)
        return {
            "sort": "0",
            "page": 0,
            "ukrainian": True,
            "cityId": self.city,
            "moveability": self.moveability,
            "educationId": self.education,
            "ageFrom": self.age_from,
            "ageTo": self.age_to,
            "salaryFrom": self.salary_from,
            "salaryTo": self.salary_to,
            "scheduleId": self.schedule,
            "languages": self.languages,
            "period": self.period,
            "experienceId": self.experience,
            "hasPhoto": self.photo,
            "keyWords": f"{self.speciality} {main_skills}",
            "searchType": "everywhere",
            "lastSort": "",
        }
