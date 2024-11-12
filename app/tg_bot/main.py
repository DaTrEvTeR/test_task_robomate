from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.tg_bot.keyboards import replykeyboard

base_router = Router(name="private_chat_router")
base_router.message.filter(
    F.chat.type == "private",
)


@base_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """This handler receives messages with the `/start` command"""
    await message.answer(
        text="Hi, this bot will help you find the perfect candidate for your vacancy, use the pull button to start searching",
        reply_markup=replykeyboard,
    )
