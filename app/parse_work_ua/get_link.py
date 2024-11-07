from app.helpers.resume_filter import ResumeFilter
from app.helpers.enums import (
    CityType,
    LangNameType,
    LangLevelType,
)
from app.parse_work_ua.enums import (
    work_salary_dict,
    work_exp_dict,
    work_lang_dict,
    work_lang_level_dict,
)


def get_work_link(filter_obj: ResumeFilter) -> str:
    """Returns a formatted string for request to work ua"""
    if filter_obj.city == 0:
        location = "-"
    else:
        location = f"-{CityType(filter_obj.city).name.lower()}-"

    speciality = f"{'+'.join(filter_obj.speciality.split(" "))}+{("+".join(filter_obj.main_skills))}"
    period = filter_obj.period - 1 if filter_obj.period in (3, 4) else filter_obj.period
    employment = (
        0 if filter_obj.schedule == 0 else 74 if filter_obj.schedule == 1 else 75
    )

    salary_from = work_salary_dict[
        max(key for key in work_salary_dict if key <= filter_obj.salary_from)
    ]
    salary_to = work_salary_dict[
        min(key for key in work_salary_dict if key >= filter_obj.salary_to)
    ]
    experience = work_exp_dict[filter_obj.experience]
    languages = dict()
    for lang, lev in filter_obj.languages.items():
        lang_name = work_lang_dict[LangNameType(lang).value]
        lang_lev = work_lang_level_dict[LangLevelType(lev).value]
        languages[lang_name] = lang_lev
    filters_dict = {
        "notitle": "1",
        "sort": "1",
        "period": period,
        "employment": employment,
        "agefrom": filter_obj.age_from,
        "ageto": filter_obj.age_to,
        "salaryfrom": salary_from,
        "salaryto": salary_to,
        "education": filter_obj.education + 65,
        "experience": experience,
        "language": "+".join(str(k) for k in languages.keys()),
        "language_level": "+".join(
            [f"{lang}-{lev}" for lang, lev in languages.items()]
        ),
        "photo": int(filter_obj.photo),
    }
    filters_list = list()
    for k, v in filters_dict.items():
        filters_list.append(f"{k}={v}")
    filters = "&".join(filters_list)
    return f"https://www.work.ua/resumes{location}{speciality}/?{filters}"
