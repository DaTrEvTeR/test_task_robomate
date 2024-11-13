from pydantic import BaseModel, Field, field_validator

from app.services.enums import (
    CityType,
    EducationType,
    ScheduleType,
    PeriodType,
    ExperienceType,
)


class ResumeFilter(BaseModel):
    speciality: str = Field(default="")
    # main skills for request
    main_skills: list[str] = Field(default=[], max_length=3)
    city: int = Field(default=CityType.ALL_UKRAINE.value)
    education: int = Field(default=EducationType.ANY.value)
    age_from: int = Field(default=0, ge=0, le=100)
    age_to: int = Field(default=0, ge=0, le=100)
    salary_from: int = Field(default=0, ge=0)
    salary_to: int = Field(default=0, ge=0)
    schedule: int = Field(default=ScheduleType.ANY.value)
    languages: dict[int, tuple[int, ...]] = Field(default_factory=dict)
    period: int = Field(default=PeriodType.YEAR.value)
    experience: int = Field(default=ExperienceType.ANY.value)
    photo: bool = Field(default=False)
    # keywords for gaining scores
    keywords: list[str] = Field(default=[])

    @field_validator("languages", mode="after")
    @classmethod
    def validate_lang(cls, languages):
        validated_languages = {}
        for lang, level in languages.items():
            validated_languages[lang] = tuple(range(level, 8))
        return validated_languages

    def update_language(self, value: tuple[int, int]):
        """Updates or appends the language in languages with validation."""
        if isinstance(value, tuple) and len(value) == 2:
            lang, level = value
            self.languages[lang] = tuple(range(level, 8))
        else:
            raise ValueError(
                "Invalid format for language. Expected tuple (lang, level)"
            )
