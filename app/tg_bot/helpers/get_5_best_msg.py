from app.services.enums import (
    EducationType,
    CityType,
    LangNameType,
    LangLevelType,
    ScheduleType,
)
from app.settings import settings


def get_5_best_msg(sorted_resumes):
    best_5 = [resume[0] for resume in sorted_resumes[:5]]
    msg_text = ""
    for resume in best_5:
        resume_short = ""
        resume_short += f"\n<B>Speciality:</B> {resume.speciality}"
        resume_short += f"\n<B>Schedule:</B> {ScheduleType(resume.schedule)}"
        resume_short += f"\n<B>Education:</B> {EducationType(resume.education)}"
        resume_short += f"\n<B>Experience:</B> {round(sum(ex.period for ex in resume.experiences), 1)} year(s)"
        resume_short += f"\n<B>City:</B> {CityType(resume.city)}"
        resume_short += f"\n<B>Age:</B> {resume.age}"
        resume_short += f"\n<B>Summary:</B> {f"{resume.skills[:100]}..." if len(resume.skills) > 100 else resume.skills}"
        langs = []
        for lang, lev in resume.languages.items():
            langs.append(f"\n  * {LangNameType(lang)} - {LangLevelType(lev)}")
        resume_short += "\n<B>Languages skills:</B> " + "".join(langs)
        resume_short += f"\n<B>Salary expectation:</B> {resume.salary_expectation} {resume.currency}"
        resume_short += f"\n<B>Filling:</B> {resume.resume_filling}%"
        msg_text += f'<a href="{resume.cv_link}">{resume.first_name if resume.first_name else "Name hidden"}</a><blockquote>{resume_short}</blockquote>\n\n\n'
    return msg_text + f"/{settings.BOT_PULL_CMD} to repeat search"
