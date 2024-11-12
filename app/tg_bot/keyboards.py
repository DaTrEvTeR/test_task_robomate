from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.services.enums import (
    CityType,
    EducationType,
    ScheduleType,
    PeriodType,
    ExperienceType,
)

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
    ]
)

buttons = [
    InlineKeyboardButton(text=str(city), callback_data=str(city.value))
    for city in CityType
]
rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
locations_kb = InlineKeyboardMarkup(inline_keyboard=rows, row_width=2)

rows = [
    InlineKeyboardButton(text=str(ed), callback_data=str(ed.value))
    for ed in EducationType
]
education_kb = InlineKeyboardMarkup(
    inline_keyboard=[[row] for row in rows], row_width=1
)

rows = [
    InlineKeyboardButton(text=str(sch), callback_data=str(sch.value))
    for sch in ScheduleType
]
schedule_kb = InlineKeyboardMarkup(inline_keyboard=[[row] for row in rows], row_width=1)

rows = [
    InlineKeyboardButton(text=str(per), callback_data=str(per.value))
    for per in PeriodType
]
period_kb = InlineKeyboardMarkup(inline_keyboard=[[row] for row in rows], row_width=1)

rows = [
    InlineKeyboardButton(text=str(ex), callback_data=str(ex.value))
    for ex in ExperienceType
]
expirience_kb = InlineKeyboardMarkup(
    inline_keyboard=[[row] for row in rows], row_width=1
)

photo_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="require", callback_data="1")],
        [InlineKeyboardButton(text="doesn't matter", callback_data="0")],
    ]
)
