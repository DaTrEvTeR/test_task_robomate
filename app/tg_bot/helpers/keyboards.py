from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.services.enums import (
    CityType,
    EducationType,
    ScheduleType,
    PeriodType,
    ExperienceType,
    LangLevelType,
)
from app.tg_bot.helpers.enums import FilterLangs, SitesIds

filt_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Speciality", callback_data="speciality")],
        [InlineKeyboardButton(text="Main skills", callback_data="skills")],
        [InlineKeyboardButton(text="Location", callback_data="location")],
        [InlineKeyboardButton(text="Education", callback_data="education")],
        [InlineKeyboardButton(text="Age range", callback_data="age")],
        [InlineKeyboardButton(text="Salary range", callback_data="salary")],
        [InlineKeyboardButton(text="Schedule", callback_data="schedule")],
        [
            InlineKeyboardButton(
                text="Knowledge of languages", callback_data="languages"
            )
        ],
        [InlineKeyboardButton(text="Search period", callback_data="period")],
        [InlineKeyboardButton(text="Experience", callback_data="experience")],
        [InlineKeyboardButton(text="Photo", callback_data="photo")],
        [InlineKeyboardButton(text="Keywords in experience", callback_data="keywords")],
        [InlineKeyboardButton(text="Site", callback_data="site")],
    ]
)

buttons = [
    InlineKeyboardButton(
        text=str(city).title().replace(" ", "-"), callback_data=str(city.value)
    )
    for city in CityType
]
loc_rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
locations_kb = InlineKeyboardMarkup(inline_keyboard=loc_rows, row_width=2)

edu_rows = [
    InlineKeyboardButton(text=str(ed), callback_data=str(ed.value))
    for ed in EducationType
]
education_kb = InlineKeyboardMarkup(
    inline_keyboard=[[row] for row in edu_rows], row_width=1
)

sch_rows = [
    InlineKeyboardButton(text=str(sch), callback_data=str(sch.value))
    for sch in ScheduleType
]
schedule_kb = InlineKeyboardMarkup(
    inline_keyboard=[[row] for row in sch_rows], row_width=1
)

per_rows = [
    InlineKeyboardButton(text=str(per), callback_data=str(per.value))
    for per in PeriodType
]
period_kb = InlineKeyboardMarkup(
    inline_keyboard=[[row] for row in per_rows], row_width=1
)

exp_rows = [
    InlineKeyboardButton(text=str(ex), callback_data=str(ex.value))
    for ex in ExperienceType
]
expirience_kb = InlineKeyboardMarkup(
    inline_keyboard=[[row] for row in exp_rows], row_width=1
)

photo_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="require", callback_data="1")],
        [InlineKeyboardButton(text="doesn't matter", callback_data="0")],
    ]
)


lang_rows = [
    InlineKeyboardButton(text=str(lang), callback_data=str(lang.value))
    for lang in FilterLangs
]
languages_kb = InlineKeyboardMarkup(
    inline_keyboard=[[row] for row in lang_rows], row_width=1
)


def get_lang_level_kb(lang_id: str) -> InlineKeyboardMarkup:
    lev_rows = [
        InlineKeyboardButton(text=str(lev), callback_data=f"{lang_id} {lev.value}")
        for lev in LangLevelType
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=[[row] for row in lev_rows], row_width=1
    )


site_rows = [
    InlineKeyboardButton(text=str(site), callback_data=str(site.value))
    for site in SitesIds
]
sites_kb = InlineKeyboardMarkup(
    inline_keyboard=[[row] for row in site_rows], row_width=1
)
