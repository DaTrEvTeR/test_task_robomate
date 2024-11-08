from app.helpers.resume_filter import ResumeFilter


def get_robota_link(resume_filter: ResumeFilter) -> str:
    """Returns a string with all the data needed to perform a request to the robota ua API"""
    filters_dict = {
        "Sort": 0,
        "SearchType": "everywhere",
        "Ukrainian": "true",
        "CityId": resume_filter.city,
        "EducationIds": resume_filter.education if resume_filter.education else "",
        "Age.From": resume_filter.age_from,
        "Age.To": resume_filter.age_to,
        "ScheduleIds": resume_filter.schedule if resume_filter.education else "",
        "Period": resume_filter.period,
        "ExperienceIds": resume_filter.experience if resume_filter.education else "",
        "KeyWords": f"{'%20'.join(resume_filter.speciality.split(" "))}%20{("%20".join(resume_filter.main_skills))}",
        "Languages": "&".join(
            [f"Languages={k}-{v}" for k, v in resume_filter.languages.items()]
        ),
        "HasPhoto": resume_filter.photo,
    }
    if resume_filter.salary_from:
        filters_dict["Salary.From"] = resume_filter.salary_from
    if resume_filter.salary_to:
        filters_dict["Salary.To"] = resume_filter.salary_to
    filters = "&".join(f"{k}={v}" for k, v in filters_dict.items())
    return f"https://employer-api.robota.ua/cvdb/resumes?{filters}"
