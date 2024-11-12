import re

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.services.resume_filter import ResumeFilter
from app.tg_bot.keyboards import (
    filt_keyboard,
    locations_kb,
    education_kb,
    schedule_kb,
    period_kb,
    expirience_kb,
    photo_kb,
)
from app.tg_bot.state import States
from app.tg_bot.get_filt_msg import get_filt_msg
from app.tg_bot.enums import StateStr
from app.settings import settings


base_router = Router(name="private_chat_router")
base_router.message.filter(
    F.chat.type == "private",
)


@base_router.message(CommandStart())
async def command_start_handler(msg: Message) -> None:
    """This handler receives messages with the `/start` command"""
    await msg.answer(
        text=settings.start_msg,
    )


@base_router.message(States.filt)
async def handle_other_message(msg: Message) -> None:
    await msg.delete()


@base_router.message(Command(settings.BOT_PULL_CMD))
async def handle_pull(msg: Message, state: FSMContext) -> None:
    """Handles the `settings.BOT_PULL_MSG` button press"""
    await state.get_state()
    data = await state.get_data()
    filt_obj = data.get("filt_obj", None)
    if not filt_obj:
        filt_obj = ResumeFilter()
        data[StateStr.FILT_OBJ] = filt_obj
    await state.set_state(States.filt)
    msg_text = get_filt_msg(filt_obj)
    data[StateStr.FILT_MSG] = await msg.answer(
        text=msg_text, reply_markup=filt_keyboard
    )
    await state.set_data(data)


@base_router.callback_query(F.data == "speciality")
async def speciality(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(
        text="Enter speciality in format 'speciality name'(digits and other spec symbols are fobidden)"
    )
    await state.set_state(States.speciality)
    await cb.answer()


@base_router.message(States.speciality)
async def set_speciality(msg: Message, state: FSMContext) -> None:
    if not re.match(r"^[a-z ]+$", msg.text.lower()):
        await msg.delete()
        return
    data = await state.get_data()
    filt_obj: ResumeFilter = data.get(StateStr.FILT_OBJ)
    filt_obj.speciality = msg.text.lower().replace(" ", "_")
    data[StateStr.FILT_OBJ] = filt_obj
    await state.set_data(data)
    await state.set_state(States.filt)
    filt_msg: Message = data.get(StateStr.FILT_MSG)
    msg_text = get_filt_msg(filt_obj)
    await filt_msg.edit_text(text=msg_text, reply_markup=filt_keyboard)
    await msg.delete()


@base_router.callback_query(F.data == "skills")
async def skills(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(
        text="Enter up to 3 main skills that candidate must have in format 'skill, another skill'(digits and other spec symbols are fobidden)"
    )
    await state.set_state(States.main_skills)
    await cb.answer()


@base_router.message(States.main_skills)
async def set_skills(msg: Message, state: FSMContext) -> None:
    if not re.match(r"^[a-z ,]+$", msg.text.lower()):
        await msg.delete()
        return
    skills_list = msg.text.lower().split(", ")
    if len(skills_list) > 3:
        await msg.delete()
        return
    data = await state.get_data()
    filt_obj: ResumeFilter = data.get(StateStr.FILT_OBJ)
    filt_obj.main_skills = skills_list
    data[StateStr.FILT_OBJ] = filt_obj
    await state.set_data(data)
    await state.set_state(States.filt)
    filt_msg: Message = data.get(StateStr.FILT_MSG)
    msg_text = get_filt_msg(filt_obj)
    await filt_msg.edit_text(text=msg_text, reply_markup=filt_keyboard)
    await msg.delete()


@base_router.callback_query(F.data == "location")
async def location(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(
        text="Choose location from list:", reply_markup=locations_kb
    )
    await state.set_state(States.location)
    await cb.answer()


@base_router.callback_query(States.location)
async def set_location(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    filt_obj: ResumeFilter = data.get(StateStr.FILT_OBJ)
    filt_obj.city = int(cb.data)
    data[StateStr.FILT_OBJ] = filt_obj
    await state.set_data(data)
    await state.set_state(States.filt)
    filt_msg: Message = data.get(StateStr.FILT_MSG)
    msg_text = get_filt_msg(filt_obj)
    await filt_msg.edit_text(text=msg_text, reply_markup=filt_keyboard)
    await cb.answer()


@base_router.callback_query(F.data == "education")
async def education(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(
        text="Choose required education type from list:", reply_markup=education_kb
    )
    await state.set_state(States.education)
    await cb.answer()


@base_router.callback_query(States.education)
async def set_education(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    filt_obj: ResumeFilter = data.get(StateStr.FILT_OBJ)
    filt_obj.education = int(cb.data)
    data[StateStr.FILT_OBJ] = filt_obj
    await state.set_data(data)
    await state.set_state(States.filt)
    filt_msg: Message = data.get(StateStr.FILT_MSG)
    msg_text = get_filt_msg(filt_obj)
    await filt_msg.edit_text(text=msg_text, reply_markup=filt_keyboard)
    await cb.answer()


@base_router.callback_query(F.data == "age")
async def age(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(
        text="Enter age range in format '0, 100'(letters and other spec symbols are fobidden, 0 is any, 100 is max)"
    )
    await state.set_state(States.age)
    await cb.answer()


@base_router.message(States.age)
async def set_age(msg: Message, state: FSMContext) -> None:
    if not re.match(r"^[0-9 ,]+$", msg.text.lower()):
        await msg.delete()
        return
    age_list = msg.text.lower().split(", ")
    try:
        age_list[0], age_list[1] = int(age_list[0]), int(age_list[1])
    except Exception:
        await msg.delete()
        return
    condition = any((len(age_list) > 2, 100 < age_list[0] < 0, 100 < age_list[1] < 0))
    if condition:
        await msg.delete()
        return
    data = await state.get_data()
    filt_obj: ResumeFilter = data.get(StateStr.FILT_OBJ)
    filt_obj.age_from = int(age_list[0])
    filt_obj.age_to = int(age_list[1])
    data[StateStr.FILT_OBJ] = filt_obj
    await state.set_data(data)
    await state.set_state(States.filt)
    filt_msg: Message = data.get(StateStr.FILT_MSG)
    msg_text = get_filt_msg(filt_obj)
    await filt_msg.edit_text(text=msg_text, reply_markup=filt_keyboard)
    await msg.delete()


@base_router.callback_query(F.data == "salary")
async def salary(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(
        text="Enter salary range(UAH) in format '0, 20000'(letters and other spec symbols are fobidden, 0 is any)"
    )
    await state.set_state(States.salary)
    await cb.answer()


@base_router.message(States.salary)
async def set_salary(msg: Message, state: FSMContext) -> None:
    if not re.match(r"^[0-9 ,]+$", msg.text.lower()):
        await msg.delete()
        return
    salary_list = msg.text.lower().split(", ")
    try:
        salary_list[0], salary_list[1] = int(salary_list[0]), int(salary_list[1])
    except Exception:
        await msg.delete()
        return
    condition = any((len(salary_list) > 2, salary_list[0] < 0, salary_list[1] < 0))
    if condition:
        await msg.delete()
        return
    data = await state.get_data()
    filt_obj: ResumeFilter = data.get(StateStr.FILT_OBJ)
    filt_obj.salary_from = int(salary_list[0])
    filt_obj.salary_to = int(salary_list[1])
    data[StateStr.FILT_OBJ] = filt_obj
    await state.set_data(data)
    await state.set_state(States.filt)
    filt_msg: Message = data.get(StateStr.FILT_MSG)
    msg_text = get_filt_msg(filt_obj)
    await filt_msg.edit_text(text=msg_text, reply_markup=filt_keyboard)
    await msg.delete()


@base_router.callback_query(F.data == "schedule")
async def schedule(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(
        text="Choose required schedule type from list:", reply_markup=schedule_kb
    )
    await state.set_state(States.schedule)
    await cb.answer()


@base_router.callback_query(States.schedule)
async def set_schedule(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    filt_obj: ResumeFilter = data.get(StateStr.FILT_OBJ)
    filt_obj.schedule = int(cb.data)
    data[StateStr.FILT_OBJ] = filt_obj
    await state.set_data(data)
    await state.set_state(States.filt)
    filt_msg: Message = data.get(StateStr.FILT_MSG)
    msg_text = get_filt_msg(filt_obj)
    await filt_msg.edit_text(text=msg_text, reply_markup=filt_keyboard)
    await cb.answer()


@base_router.callback_query(F.data == "languages")  ###
async def languages(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    data.get("filt_obj")
    cb.message.edit_text("")


@base_router.callback_query(F.data == "period")
async def period(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(text="Choose period from list:", reply_markup=period_kb)
    await state.set_state(States.period)
    await cb.answer()


@base_router.callback_query(States.period)
async def set_period(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    filt_obj: ResumeFilter = data.get(StateStr.FILT_OBJ)
    filt_obj.period = int(cb.data)
    data[StateStr.FILT_OBJ] = filt_obj
    await state.set_data(data)
    await state.set_state(States.filt)
    filt_msg: Message = data.get(StateStr.FILT_MSG)
    msg_text = get_filt_msg(filt_obj)
    await filt_msg.edit_text(text=msg_text, reply_markup=filt_keyboard)
    await cb.answer()


@base_router.callback_query(F.data == "experience")
async def experience(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(
        text="Choose experience from list:", reply_markup=expirience_kb
    )
    await state.set_state(States.experience)
    await cb.answer()


@base_router.callback_query(States.experience)
async def set_experience(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    filt_obj: ResumeFilter = data.get(StateStr.FILT_OBJ)
    filt_obj.experience = int(cb.data)
    data[StateStr.FILT_OBJ] = filt_obj
    await state.set_data(data)
    await state.set_state(States.filt)
    filt_msg: Message = data.get(StateStr.FILT_MSG)
    msg_text = get_filt_msg(filt_obj)
    await filt_msg.edit_text(text=msg_text, reply_markup=filt_keyboard)
    await cb.answer()


@base_router.callback_query(F.data == "photo")
async def photo(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(
        text="Choose experience from list:", reply_markup=photo_kb
    )
    await state.set_state(States.photo)
    await cb.answer()


@base_router.callback_query(States.photo)
async def set_photo(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    filt_obj: ResumeFilter = data.get(StateStr.FILT_OBJ)
    filt_obj.photo = bool(int(cb.data))
    data[StateStr.FILT_OBJ] = filt_obj
    await state.set_data(data)
    await state.set_state(States.filt)
    filt_msg: Message = data.get(StateStr.FILT_MSG)
    msg_text = get_filt_msg(filt_obj)
    await filt_msg.edit_text(text=msg_text, reply_markup=filt_keyboard)
    await cb.answer()


@base_router.callback_query(F.data == "keywords")
async def keywords(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(
        text="Enter keywords that will be considered a plus if the candidate has them, in the format 'keyword, another keyword' (numbers and special characters are forbiden)"
    )
    await state.set_state(States.keywords)
    await cb.answer()


@base_router.message(States.keywords)
async def set_keywords(msg: Message, state: FSMContext) -> None:
    if not re.match(r"^[a-z ,]+$", msg.text.lower()):
        await msg.delete()
        return
    keywords_list = msg.text.lower().split(", ")
    data = await state.get_data()
    filt_obj: ResumeFilter = data.get(StateStr.FILT_OBJ)
    filt_obj.keywords = keywords_list
    data[StateStr.FILT_OBJ] = filt_obj
    await state.set_data(data)
    await state.set_state(States.filt)
    filt_msg: Message = data.get(StateStr.FILT_MSG)
    msg_text = get_filt_msg(filt_obj)
    await filt_msg.edit_text(text=msg_text, reply_markup=filt_keyboard)
    await msg.delete()
