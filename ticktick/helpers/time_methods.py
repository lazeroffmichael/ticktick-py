import pytz

from ticktick.helpers.constants import DATE_FORMAT
import datetime


def convert_local_time_to_utc(original_time: datetime, time_zone: str):
    """
    Converts the passed datetime from the time_zone specified into UTC time.

    Timezones can be found in timezones.txt

    :param original_time: datetime string in the time zone passed
    :param time_zone: string of the timezone from the pytz list of timezones
    :return: datetime object containing the converted UTC time with no timezone information attached
    """

    utc = pytz.utc
    time_zone = pytz.timezone(time_zone)
    original_time = original_time.strftime(DATE_FORMAT)
    time_object = datetime.datetime.strptime(original_time, DATE_FORMAT)
    time_zone_dt = time_zone.localize(time_object)
    return time_zone_dt.astimezone(utc).replace(tzinfo=None)


def convert_iso_to_tick_tick_format(date: datetime, tz: str):
    """
    Parses ISO 8601 Format to Tick Tick Format
    ISO 8601 Format Example: 2020-12-23T01:56:07+00:00
    TickTick Required Format: 2020-12-23T01:56:07+0000 -> Where the last colon is removed for timezone
    :param date: Datetime object to be parsed
    :param tz: Timezone
    :return: Parsed time string
    """
    date = convert_local_time_to_utc(date, tz)
    date = date.replace(tzinfo=datetime.timezone.utc).isoformat()
    date = date[::-1].replace(":", "", 1)[::-1]
    return date
