import asyncio

from app.parse_robota_ua.parse_robota import get_resumes_page
from app.helpers.resume_filter import ResumeFilter


if __name__ == '__main__':
    res_req_body = ResumeFilter(position="", keywords=[""]).robota_request()
    asyncio.run(get_resumes_page(request_data=res_req_body))
