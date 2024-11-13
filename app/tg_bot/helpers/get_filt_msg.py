from app.services.context import ParseContext
from app.services.enums import (
    CityType,
    EducationType,
    ScheduleType,
    LangNameType,
    LangLevelType,
    PeriodType,
    ExperienceType,
)
from app.tg_bot.helpers.enums import parsers_to_str
from app.settings import settings


def get_filt_msg_text(context: ParseContext) -> str:
    filt_obj = context.filter_obj
    languages = []
    languages_str = ""
    if filt_obj.languages:
        for lang, lev in filt_obj.languages.items():  # type: ignore[misc]
            languages.append(
                f"{str(LangNameType(lang))} - {str(LangLevelType(lev[0]))}"  # type: ignore[has-type]
            )
        languages_str = "\n  * " + "\n  * ".join(languages)
    msg_text = (
        "Current Filters:\n\n"
        f"<blockquote>👷‍♂️<B>Speciality</B>: {filt_obj.speciality.replace("_", " ").title()}\n"
        f"📝<B>Required skills</B>: {"\n  > " + "\n  > ".join(skill.replace("_", " ").title() for skill in filt_obj.main_skills) if filt_obj.main_skills else ""}\n"
        f"🏙<B>Location</B>: {str(CityType(filt_obj.city)).title()}\n"
        f"👩‍🎓<B>Education</B>: {EducationType(filt_obj.education)}\n"
        f"👴<B>Age</B>: from {filt_obj.age_from if filt_obj.age_from else "any"} to {filt_obj.age_to if filt_obj.age_to else "any"}\n"
        f"💰<B>Salary expectation</B>: from {filt_obj.salary_from if filt_obj.salary_from else "any"} to {filt_obj.salary_to if filt_obj.salary_to else "any"}\n"
        f"⏳️<B>Schedule type</B>: {ScheduleType(filt_obj.schedule)}\n"
        f"🗣<B>Languages</B>: {languages_str if languages_str else "any"}\n"
        f"📅<B>Search period</B>: {PeriodType(filt_obj.period)}\n"
        f"💪<B>Expirience</B>: {ExperienceType(filt_obj.experience)}\n"
        f"📸<B>Photo</B>: {"required" if filt_obj.photo else "not required"}\n"
        f"🔑<B>Keywords in text</B>: {"\n  - " + "\n  - ".join(skill.replace("_", " ").title() for skill in filt_obj.keywords) if filt_obj.keywords else ""}</blockquote>\n"
        f"🌐<B>Site:</B> {f"<u>{parsers_to_str[context.parser_cls]}</u>" if context.parser_cls else "<u>select a site from the corresponding menu</u>"}"
        f"\nUse <B>/{settings.BOT_SEARCH_CMD}</B> to start searching (don't forget to specify the specialization and site before that)"
    )
    return msg_text
