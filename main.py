import logging
import asyncio

from app.tg_bot.config import dp, bot
from app.tg_bot.main import base_router


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def wrapper():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        dp.include_router(base_router)
        asyncio.run(wrapper())
    except Exception as e:
        logging.error(f"ROOT ERROR: {e}")
