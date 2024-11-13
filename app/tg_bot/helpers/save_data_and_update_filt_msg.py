from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.services.context import ParseContext
from app.tg_bot.helpers.enums import StateStr
from app.tg_bot.helpers.state import States
from app.tg_bot.helpers.keyboards import filt_keyboard
from app.tg_bot.helpers.get_filt_msg import get_filt_msg_text


async def save_data_and_update_filt_msg(
    state: FSMContext, data: dict, context: ParseContext
) -> None:
    data[StateStr.CONTEXT] = context
    await state.set_data(data)

    await state.set_state(States.filt)
    filt_msg: Message = data.get(StateStr.FILT_MSG)
    msg_text = get_filt_msg_text(context)
    await filt_msg.edit_text(text=msg_text, reply_markup=filt_keyboard)
