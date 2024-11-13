from app.services.enums import CustomEnum
from app.parse_work_ua.work_ua_parser import WorkUaParser
from app.parse_robota_ua.robota_ua_parser import RobotaUaParser


class StateStr:
    FILT_MSG = "filt_msg"
    CONTEXT = "parse_context"


class FilterLangs(CustomEnum):
    ENGLISH = 1
    GERMAN = 2
    FRENCH = 3
    SPANISH = 4
    ITALIAN = 5
    POLISH = 130
    UKRAINIAN = 145


class SitesIds(CustomEnum):
    ROBOTA_UA = 1
    WORK_UA = 2


ids_to_parsers = {
    SitesIds.ROBOTA_UA.value: RobotaUaParser,
    SitesIds.WORK_UA.value: WorkUaParser,
}

parsers_to_str = {
    v: str(SitesIds(k)).replace(" ", ".") for k, v in ids_to_parsers.items()
}
