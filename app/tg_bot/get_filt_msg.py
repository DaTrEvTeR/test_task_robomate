from app.services.resume_filter import ResumeFilter
from app.services.enums import (
    CityType,
    EducationType,
    ScheduleType,
    LangNameType,
    LangLevelType,
    PeriodType,
    ExperienceType,
)


def get_filt_msg(filt_obj: ResumeFilter) -> str:
    languages = []
    if filt_obj.languages:
        for lang, lev in filt_obj.languages:  # type: ignore[misc]
            languages.append(
                f"{str(LangNameType(lang))} - {str(LangLevelType(lev[0]))}"  # type: ignore[has-type]
            )
        languages_str = "\n  * ".join(languages)
    msg_text = (
        "Current Filters:\n\n"
        f"<B>Speciality</B>: {filt_obj.speciality.replace("_", " ").title()}\n"
        f"<B>Required skills</B>: {"; ".join(skill.replace("_", " ").title() for skill in filt_obj.main_skills)}\n"
        f"<B>Location</B>: {str(CityType(filt_obj.city)).title()}\n"
        f"<B>Education</B>: {EducationType(filt_obj.education)}\n"
        f"<B>Age</B>: from {filt_obj.age_from if filt_obj.age_from else 'Any'} to {filt_obj.age_to if filt_obj.age_to else 'Any'}\n"
        f"<B>Salary expectation</B>: from {filt_obj.salary_from if filt_obj.salary_from else 'Any'} to {filt_obj.salary_to if filt_obj.salary_to else 'Any'}\n"
        f"<B>Schedule type</B>: {ScheduleType(filt_obj.schedule)}\n"
        f"<B>Languages</B>: {languages_str if languages_str else "Any"}\n"
        f"<B>Search period</B>: {PeriodType(filt_obj.period)}\n"
        f"<B>Expirience</B>: {ExperienceType(filt_obj.experience)}\n"
        f"<B>Photo</B>: {"required" if filt_obj.photo else "not required"}\n"
        f"<B>Keywords in text</B>: {"; ".join(skill.replace("_", " ").title() for skill in filt_obj.keywords)}\n"
    )
    return msg_text
