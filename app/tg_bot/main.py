import re
import logging

from asyncio import sleep
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, link_preview_options
from aiogram.fsm.context import FSMContext

from app.services.context import ParseContext
from app.scoring.sort_resumes_by_relevance import sort_resumes_by_relevance
from app.tg_bot.helpers.keyboards import (
    filt_keyboard,
    locations_kb,
    education_kb,
    schedule_kb,
    period_kb,
    expirience_kb,
    photo_kb,
    get_lang_level_kb,
    languages_kb,
    sites_kb,
)
from app.tg_bot.helpers.state import States
from app.tg_bot.helpers.delete_incorrect_with_timeout import (
    delete_incorrect_with_timeout,
)
from app.tg_bot.helpers.get_filt_msg import get_filt_msg_text
from app.tg_bot.helpers.save_data_and_update_filt_msg import (
    save_data_and_update_filt_msg,
)
from app.tg_bot.helpers.enums import StateStr, FilterLangs, ids_to_parsers
from app.tg_bot.helpers.msg_in_state_f import msg_in_state_f
from app.tg_bot.helpers.get_5_best_msg import get_5_best_msg
from app.settings import settings


base_router = Router(name="private_chat_router")
base_router.message.filter(
    F.chat.type == "private",
)


@base_router.message(Command(settings.BOT_SEARCH_CMD), States.filt)
async def handle_search(msg: Message, state: FSMContext) -> None:
    data = await state.get_data()
    context: ParseContext = data.get(StateStr.CONTEXT, None)
    try:
        await state.set_state(States.fetching)
        fetching_msg = await msg.answer(
            "Fetching resumes from the website's database, please wait"
        )

        parsed_resumes = await context.parse()
        if parsed_resumes:
            sorted_resumes = sort_resumes_by_relevance(
                resumes=parsed_resumes, resume_filter=context.filter_obj
            )

            msg_text = get_5_best_msg(sorted_resumes)

            await msg.answer(
                text=msg_text,
                link_preview_options=link_preview_options.LinkPreviewOptions(
                    is_disabled=True
                ),
            )
        else:
            await msg.answer(
                text=(
                    "No resumes found matching your filters\n"
                    "please try to expand your search criteria\n"
                    f"\n/{settings.BOT_PULL_CMD} restart resumes pulling process"
                )
            )

    except Exception as e:
        if not (context.parser_cls or context.filter_obj.speciality):
            to_delete = await msg.answer("Input speciality and site first, please")
        else:
            logging.error(e)
            to_delete = await msg.answer(
                "Sorry, something went wrong. Try again later."
            )
        await sleep(7)
        await to_delete.delete()
        await state.set_state(States.filt)

    else:
        filt_msg: Message = data[StateStr.FILT_MSG]
        await filt_msg.delete()
        await state.clear()

    finally:
        await msg.delete()
        await fetching_msg.delete()


@base_router.message(msg_in_state_f())
async def handle_other_message(msg: Message) -> None:
    await msg.delete()


@base_router.message(Command(settings.BOT_PULL_CMD))
async def handle_pull(msg: Message, state: FSMContext) -> None:
    """Handles the `settings.BOT_PULL_MSG` button press"""
    data = await state.get_data()
    context = ParseContext()
    data[StateStr.CONTEXT] = context
    await state.set_state(States.filt)
    msg_text = get_filt_msg_text(context)
    data[StateStr.FILT_MSG] = await msg.answer(
        text=msg_text, reply_markup=filt_keyboard
    )
    await state.set_data(data)
    await msg.delete()


@base_router.callback_query(F.data == "speciality")
async def speciality(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(
        text="Enter speciality in format <blockquote>\nspeciality name\n</blockquote>"
    )
    await state.set_state(States.speciality)
    await cb.answer()


@base_router.message(States.speciality)
async def set_speciality(msg: Message, state: FSMContext) -> None:
    data = await state.get_data()
    context: ParseContext = data.get(StateStr.CONTEXT)

    context.filter_obj.speciality = msg.text.lower().replace(" ", "_")

    await save_data_and_update_filt_msg(state, data, context)
    await msg.delete()


@base_router.callback_query(F.data == "skills")
async def skills(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(
        text="Enter up to 3 main skills that candidate must have in format <blockquote>\nSkill, another skill...</blockquote>"
    )
    await state.set_state(States.main_skills)
    await cb.answer()


@base_router.message(States.main_skills)
async def set_skills(msg: Message, state: FSMContext) -> None:
    skills_list = msg.text.lower().split(", ")
    skills_list = [skill.replace(" ", "_") for skill in skills_list]
    if len(skills_list) > 3:
        return await delete_incorrect_with_timeout(msg)
    data = await state.get_data()
    context: ParseContext = data.get(StateStr.CONTEXT)

    context.filter_obj.main_skills = skills_list

    await save_data_and_update_filt_msg(state, data, context)
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
    context: ParseContext = data.get(StateStr.CONTEXT)

    context.filter_obj.city = int(cb.data)

    await save_data_and_update_filt_msg(state, data, context)
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
    context: ParseContext = data.get(StateStr.CONTEXT)

    context.filter_obj.education = int(cb.data)

    await save_data_and_update_filt_msg(state, data, context)
    await cb.answer()


@base_router.callback_query(F.data == "age")
async def age(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(
        text="Enter age range in format <blockquote>\n0, 100\n</blockquote>(letters and other spec symbols are fobidden, 0 is any, 100 is max)"
    )
    await state.set_state(States.age)
    await cb.answer()


@base_router.message(States.age)
async def set_age(msg: Message, state: FSMContext) -> None:
    if not re.match(r"^[0-9, ]+$", msg.text.lower()):
        return await delete_incorrect_with_timeout(msg)
    age_list = msg.text.lower().split(", ")
    try:
        age_from = int(age_list[0])
        age_to = int(age_list[1])
    except Exception:
        return await delete_incorrect_with_timeout(msg)
    condition = any(
        (len(age_list) > 2, not (100 >= age_from >= 0), not (100 >= age_to >= 0))
    )
    if condition:
        return await delete_incorrect_with_timeout(msg)

    data = await state.get_data()
    context: ParseContext = data.get(StateStr.CONTEXT)

    context.filter_obj.age_from = age_from
    context.filter_obj.age_to = age_to

    await save_data_and_update_filt_msg(state, data, context)
    await msg.delete()


@base_router.callback_query(F.data == "salary")
async def salary(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(
        text="Enter salary range(UAH) in format <blockquote>\n0, 20000\n</blockquote>(letters and other spec symbols are fobidden, 0 is any)"
    )
    await state.set_state(States.salary)
    await cb.answer()


@base_router.message(States.salary)
async def set_salary(msg: Message, state: FSMContext) -> None:
    if not re.match(r"^[0-9, ]+$", msg.text.lower()):
        return await delete_incorrect_with_timeout(msg)
    salary_list = msg.text.lower().split(", ")
    try:
        salary_from = int(salary_list[0])
        salary_to = int(salary_list[1])
    except Exception:
        return await delete_incorrect_with_timeout(msg)
    condition = any((len(salary_list) > 2, salary_to < 0, salary_to < 0))
    if condition:
        return await delete_incorrect_with_timeout(msg)

    data = await state.get_data()
    context: ParseContext = data.get(StateStr.CONTEXT)

    context.filter_obj.salary_from = salary_from
    context.filter_obj.salary_to = salary_to

    await save_data_and_update_filt_msg(state, data, context)
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
    context: ParseContext = data.get(StateStr.CONTEXT)

    context.filter_obj.schedule = int(cb.data)

    await save_data_and_update_filt_msg(state, data, context)
    await cb.answer()


@base_router.callback_query(F.data == "languages")
async def languages(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(
        text="Choose required languages from list:", reply_markup=languages_kb
    )
    await state.set_state(States.languages)
    await cb.answer()


@base_router.callback_query(States.languages)
async def set_language(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(
        text=f"Choose required {FilterLangs(int(cb.data))} min level from list:",
        reply_markup=get_lang_level_kb(cb.data),
    )
    await state.set_state(States.lang_level)
    await cb.answer()


@base_router.callback_query(States.lang_level)
async def set_lang_level(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    context: ParseContext = data.get(StateStr.CONTEXT)

    lang = cb.data.split(" ")
    lang_id, lang_lev = int(lang[0]), int(lang[1])
    context.filter_obj.update_language((lang_id, lang_lev))

    await save_data_and_update_filt_msg(state, data, context)
    await cb.answer()


@base_router.callback_query(F.data == "period")
async def period(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(text="Choose period from list:", reply_markup=period_kb)
    await state.set_state(States.period)
    await cb.answer()


@base_router.callback_query(States.period)
async def set_period(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    context: ParseContext = data.get(StateStr.CONTEXT)

    context.filter_obj.period = int(cb.data)

    await save_data_and_update_filt_msg(state, data, context)
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
    context: ParseContext = data.get(StateStr.CONTEXT)

    context.filter_obj.experience = int(cb.data)

    await save_data_and_update_filt_msg(state, data, context)
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
    context: ParseContext = data.get(StateStr.CONTEXT)

    context.filter_obj.photo = bool(int(cb.data))

    await save_data_and_update_filt_msg(state, data, context)
    await cb.answer()


@base_router.callback_query(F.data == "keywords")
async def keywords(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(
        text="Enter keywords that will be considered a plus if the candidate has them, in the format <blockquote>\nKeyword, another keyword\n</blockquote>"
    )
    await state.set_state(States.keywords)
    await cb.answer()


@base_router.message(States.keywords)
async def set_keywords(msg: Message, state: FSMContext) -> None:
    keywords_list = msg.text.lower().split(", ")

    data = await state.get_data()
    context: ParseContext = data.get(StateStr.CONTEXT)

    context.filter_obj.keywords = keywords_list

    await save_data_and_update_filt_msg(state, data, context)
    await msg.delete()


@base_router.callback_query(F.data == "site")
async def site(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.edit_text(text="Choose site from list:", reply_markup=sites_kb)
    await state.set_state(States.site)
    await cb.answer()


@base_router.callback_query(States.site)
async def set_site(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    context: ParseContext = data.get(StateStr.CONTEXT)

    context.parser_cls = ids_to_parsers[int(cb.data)]

    await save_data_and_update_filt_msg(state, data, context)
    await cb.answer()


@base_router.message(CommandStart())
async def command_start_handler(msg: Message) -> None:
    """This handler receives messages with the `/start` command"""
    await msg.answer(
        text=settings.start_msg,
    )
