from aiohttp import ClientError
import logging
import brotli

from app.helpers.custom_session import CustomSession
from app.parse_robota_ua.constants import RESUMES_URL

async def get_resumes_page(request_data: dict[str, any]) -> dict[str, any]:
    """Retrieve a page of resumes from the employer API.

    Parameters
    ----------
    request_data : dict
        A dictionary containing the request parameters for fetching resumes, 
        structured according to the API specifications.

    Returns
    -------
    dict
        The JSON response from the API containing the resumes and related data.
    """    
    try:
        async with CustomSession() as session:
            async with session.post(RESUMES_URL, json=request_data) as response:
                if not response.ok:
                    raise ClientError(
                        f"Error {response.status}: {response.reason}"
                    )
                json = await response.json()
            print(json)
            return json
    except Exception as e:
        logging.error(f"Error retrieving resumes: {e}")
