import asyncio
import logging

from app.parse_robota_ua.robota_ua_parser import RobotaUaParser
from app.helpers.resume_filter import ResumeFilter
from app.settings import settings
from app.helpers.custom_session import CustomSession


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

async def run_parser(filter_obj, settings):
    async with CustomSession() as session:
        parser = RobotaUaParser(
            filter_obj=filter_obj,
            settings=settings,
            session=session
        )
        results = await parser.run_parser()

if __name__ == '__main__':
    filter_obj = ResumeFilter(speciality="python developer", keywords=["fastapi"])
    asyncio.run(run_parser(
        filter_obj=filter_obj, 
        settings=settings))
