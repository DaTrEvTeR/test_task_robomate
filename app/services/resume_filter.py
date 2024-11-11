from pydantic import BaseModel, Field, field_validator

from app.services.enums import (
    CityType,
    EducationType,
    ScheduleType,
    PeriodType,
    ExperienceType,
)


class ResumeFilter(BaseModel):
    speciality: str
    # main skills for request
    main_skills: list[str] = Field(default=[], max_length=3)
    city: int = Field(default=CityType.ALL_UKRAINE.value)
    education: int = Field(default=EducationType.ANY.value)
    age_from: int = Field(default=0, ge=0, le=100)
    age_to: int = Field(default=0, ge=0, le=100)
    salary_from: int = Field(default=0, ge=0)
    salary_to: int = Field(default=0, ge=0)
    schedule: int = Field(default=ScheduleType.ANY.value)
    languages: dict[int, tuple[int]] = Field(default=dict())
    period: int = Field(default=PeriodType.YEAR.value)
    experience: int = Field(default=ExperienceType.ANY.value)
    photo: bool = Field(default=False)
    # keywords for gaining scores
    keywords: list[str] = Field(default=[])

    @field_validator("languages", mode="before")
    def validate_lang(cls, languages):
        for lang, level in languages.items():
            level = int(level[0])
            if level == 7:
                languages[lang] = (7,)
            elif level != 6:
                if level < 4:
                    languages[lang] = tuple(range(level, 8))
                else:
                    t = list(range(level, 8))
                    t.remove(6)
                    languages[lang] = tuple(t)
            else:
                languages[lang] = (6, 4, 5, 7)
        return languages
