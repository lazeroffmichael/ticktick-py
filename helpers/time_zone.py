import pytz
from datetime import datetime

from helpers.constants import DATE_FORMAT


def convert_local_time_to_utc(original_time: datetime, time_zone:str):
    """
    Converts the passed datetime from the time_zone specified into UTC time.

    Timezones can be found in timezones.txt

    :param original_time: datetime string in the time zone passed
    :param timezone: string of the timezone from the pytz list of timezones
    :return: datetime object containing the converted UTC time with no timezone information attached
    """

    utc = pytz.utc
    time_zone = pytz.timezone(time_zone)
    original_time = original_time.strftime(DATE_FORMAT)
    time_object = datetime.strptime(original_time, DATE_FORMAT)
    time_zone_dt = time_zone.localize(time_object)
    return time_zone_dt.astimezone(utc).replace(tzinfo=None)

