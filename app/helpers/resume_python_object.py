import re

from pydantic import BaseModel, model_validator, field_validator
from typing import Any
from datetime import datetime

from app.helpers.enums import *


class ResumeModel(BaseModel):
    cv_link: str
    last_name: str
    first_name: str
    father_name: str
    age: int
    speciality: str
    city: str
    schedule: str
    salary_expectation: int
    currency: str
    resume_filling: int
    skills: str
    educations: list[dict[str, Any]]
    experiences: list[dict[str, Any]]
    languages: list[dict[str, str]]

    @field_validator('age', mode="before")
    def parse_age(cls, value):
        if isinstance(value, str):
            value = value.split(" ")[0]
            if value:
                return int(value)
        return value

    @field_validator('skills', mode="before")
    def clean_skills(cls, value):
        if isinstance(value, list) and value:
            skill = value[0].get('description', '')
            return re.sub(r'\s{2,}', ' ', re.sub(r'<[^>]*>', ' ', skill))
        return ""

    @model_validator(mode="before")
    def check_required_fields(cls, values):
        # Mapping additional required fields from the raw input to the model's attributes
        values['cv_link'] = f"https://robota.ua/candidates/{values['resumeId']}"
        values['last_name'] = values.get('surname', '')
        values['first_name'] = values.get('name', '')
        values['father_name'] = values.get('fatherName', '')
        values['salary_expectation'] = int(values.get('salary', 0))
        values['currency'] = values.get('currencySign', '') if values['salary_expectation'] != 0 else ''
        values['city'] = str(CityType(values["cityId"]))
        values['schedule'] = str(ScheduleType(values['scheduleId']))
        values["resume_filling"] = values.get('fillingPercentage', 0)
        values["languages"] = list()
        for lang in values.get('languageSkills', []):
            language = str(LangNameType(lang["languageId"]))
            language_lvl = str(LangLevelType(lang["languageSkillId"]))
            values["languages"].append({language: language_lvl})
        temp = list()
        for ed in values.get("educations", []):
            comment = re.sub(r'\s{2,}', ' ', re.sub(r'<[^>]*>', ' ', ed["comment"]))
            temp.append({
                "name": ed["name"],
                "comment": comment,
                "location": ed["location"],
                "speciality": ed["speciality"],
                "yearOfGraduation": ed["yearOfGraduation"],
            })
        values["educations"] = temp
        temp = list()
        for ex in values.get("experiences", []):
            start_work, end_work = datetime.fromisoformat(ex["startWork"]), datetime.fromisoformat(ex["endWork"]) if ex["endWork"] else datetime.now()
            rounded_years = round((end_work - start_work).days / 365.25, 1)
            desc = re.sub(r'\s{2,}', ' ', re.sub(r'<[^>]*>', ' ', ex["description"]))
            temp.append({
                "position": ex["position"],
                "company": ex["company"],
                "description": desc,
                "period": rounded_years,
            })
        values["experiences"] = temp
        return values

if __name__ == "__main__":
    from enums import *
    import json
    with open("a.json") as f:
        res = json.load(f)

    a = ResumeModel(**res)
    print(a)