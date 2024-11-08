import re

from bs4 import BeautifulSoup

from app.helpers.resume_python_object import BaseResumeModel


class WorkResumeModel(BaseResumeModel):
    @classmethod
    def from_html(cls, html: str):
        soup = BeautifulSoup(html, "lxml")

        resume_filling = 0

        cv_link = soup.select_one("head > link[rel='canonical']")["href"]
        first_name = soup.select_one("div.row > div > div > h1.mt-0.mb-0").text.strip()

        age = 0
        if age_title := soup.find("dt", string="Вік:"):
            age_text = age_title.find_next_sibling("dd").text.strip()
            age = int(age_text.split("\xa0")[0] if age_text else 0)

        speciality = (
            soup.select_one("div.row > div > div > h2")
            .find(string=True, recursive=False)
            .strip()
        )

        city_title = soup.find("dt", string=re.compile(r"Місто(:| проживання:)"))
        city = city_title.find_next_sibling("dd").text.strip() if city_title else None

        schedule_title = soup.find("dt", string="Зайнятість:")
        schedule = (
            schedule_title.find_next_sibling("dd").text.strip()
            if schedule_title
            else ""
        )

        salary_expectation, currency = 0, ""
        if salary_block := soup.select_one(
            "div.row > div > div > h2 > span.text-muted-print"
        ):
            salary_block = salary_block.text[2:].split("\xa0")
            salary_expectation = int("".join(salary_block[:-1]))
            currency = salary_block[-1]

        skills = ", ".join([skill.text for skill in soup.select("span.ellipsis")])
        resume_filling += (
            len(skills.split(", ")) * 4 if len(skills.split(", ")) < 10 else 40
        )
        if soup.find("span", attrs={"class": "label label-violet-light"}):
            skills = re.sub(
                r"\[відкрити контакти\]\(див\. вище в блоці «контактна інформація»\)",
                "",
                re.sub(r"\s+", " ", soup.select_one("div#add_info").text.strip()),
            )

        siblings: list = []
        if ed_title := soup.find("h2", string="Освіта"):
            list_ind = -1
            for sibling in ed_title.find_next_siblings():
                if sibling.name == "h2" and sibling.get(
                    "class"
                ) != "h4 strong-600 mt-lg sm:mt-xl".split(" "):
                    break
                if sibling.get("class") == "h4 strong-600 mt-lg sm:mt-xl".split(" "):
                    siblings.append([])
                    list_ind += 1
                siblings[list_ind].append(sibling)

        educations = []
        for ex in siblings:
            name = ex[0].text
            comment = ex[2].text if len(ex) == 3 else ""
            desc_split = ex[1].text.strip().split(", з ")
            spec = desc_split[0]
            year_of_graduation = (
                desc_split[-1].split(" ")[2] if len(desc_split) != 1 else 0
            )
            educations.append(
                {
                    "name": name,
                    "comment": comment,
                    "speciality": spec.strip(),
                    "yearOfGraduation": int(year_of_graduation),
                }
            )
        resume_filling += 20 if educations else 0

        ex_siblings: list = []
        if ex_title := soup.find("h2", string="Досвід роботи"):
            list_ind = -1
            for sibling in ex_title.find_next_siblings():
                if sibling.name == "h2" and sibling.get(
                    "class"
                ) != "h4 strong-600 mt-lg sm:mt-xl".split(" "):
                    break
                if sibling.get("class") == "h4 strong-600 mt-lg sm:mt-xl".split(" "):
                    ex_siblings.append([])
                    list_ind += 1
                ex_siblings[list_ind].append(sibling)

        experiences = []
        for ex in ex_siblings:
            position = ex[0].text
            description = ex[2].text if len(ex) == 3 else ""
            period_str = (
                ex[1].select_one("span.text-default-7").text[1:-1].split("\xa0")
            )
            if len(period_str) == 4:
                period = round(int(period_str[0]) + int(period_str[2]) / 12, 1)
            elif len(period_str) == 1:
                period = round(1 / 12, 1)
            elif "м" == period_str[1][0]:
                period = round(int(period_str[0]) / 12, 1)
            else:
                period = round(int(period_str[0]), 1)
            company = ex[1].text.split("\n")[-1].strip()
            experiences.append(
                {
                    "position": position,
                    "company": company,
                    "description": description,
                    "period": period,
                }
            )
        resume_filling += 20 if experiences else 0

        languages = []
        if langs := soup.find("h2", string="Знання мов"):
            if (
                langs.find_next_sibling("ul")
                and langs.find_next_sibling("ul").get("class") is None
            ):
                langs = langs.find_next_sibling("ul").select("li")
                for lang in langs:
                    t = lang.text.split(" — ")
                    languages.append({t[0]: t[1]})
            else:
                t = langs.find_next_sibling("p").text.split(" — ")
                languages.append({t[0]: t[1]})
        resume_filling += 20 if languages else 0

        return cls(
            cv_link=cv_link,
            last_name="",
            first_name=first_name,
            father_name="",
            age=age,
            speciality=speciality,
            city=city,
            schedule=schedule,
            salary_expectation=salary_expectation,
            currency=currency,
            resume_filling=resume_filling,
            skills=skills,
            educations=educations,
            experiences=experiences,
            languages=languages,
        )
