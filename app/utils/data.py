import datetime
from dateutil.parser import parser
# from dateutil.parser._parser import ParserError

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S.%f"
DATETIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT


def is_invalid_date_string(date_string):
    # dateutil parser does not agree with dates like "0001-01-01" or "0000-00-00"
    return (not date_string) or (date_string or "").startswith(("0001-01-01", "0000-00-00"))


# datetime functions
def getdate(string_date=None):
    """
    Converts string date (yyyy-mm-dd) to datetime.date object
    """

    if not string_date:
        return get_datetime().date()
    if isinstance(string_date, datetime.datetime):
        return string_date.date()

    elif isinstance(string_date, datetime.date):
        return string_date

    if is_invalid_date_string(string_date):
        return None
    # try:
    #     return parser.parse(string_date).date()
    # except ParserError:
    #     frappe.throw(frappe._('{} is not a valid date string.').format(
    #         frappe.bold(string_date)
    #     ), title='Invalid Date')


def date_diff(string_ed_date, string_st_date):
    return (getdate(string_ed_date) - getdate(string_st_date)).days


def get_datetime(datetime_str=None):
    if datetime_str is None:
        return now_datetime()

    if isinstance(datetime_str, (datetime.datetime, datetime.timedelta)):
        return datetime_str

    elif isinstance(datetime_str, (list, tuple)):
        return datetime.datetime(datetime_str)

    elif isinstance(datetime_str, datetime.date):
        return datetime.datetime.combine(datetime_str, datetime.time())

    if is_invalid_date_string(datetime_str):
        return None

    try:
        return datetime.datetime.strptime(datetime_str, DATETIME_FORMAT)
    except ValueError:
        return parser.parse(datetime_str)


def now_datetime():
    dt = convert_utc_to_user_timezone(datetime.datetime.utcnow())
    return dt.replace(tzinfo=None)


def convert_utc_to_user_timezone(utc_timestamp):
    from pytz import timezone, UnknownTimeZoneError
    utcnow = timezone('UTC').localize(utc_timestamp)
    try:
        return utcnow.astimezone(timezone(get_time_zone()))
    except UnknownTimeZoneError:
        return utcnow


def get_time_zone():
    return 'Africa/Nairobi'  # Default to Kenya ?!
