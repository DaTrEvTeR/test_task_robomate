import logging
import asyncio

from app.tg_bot.config import dp, bot
from app.tg_bot.main import base_router


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


if __name__ == "__main__":
    dp.include_router(base_router)
    asyncio.run(dp.start_polling(bot))
