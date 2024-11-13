from aiogram.filters import or_f

from app.tg_bot.helpers.state import States


def msg_in_state_f():
    return or_f(
        States.filt,
        States.location,
        States.education,
        States.schedule,
        States.languages,
        States.lang_level,
        States.period,
        States.experience,
        States.photo,
        States.site,
        States.fetching,
    )
