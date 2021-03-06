import datetime as dt

from babel.dates import get_timezone


def now(tzname: str = 'Asia/Seoul') -> dt.datetime:
    """Helper to make current datetime."""

    return dt.datetime.now(tz=get_timezone(tzname))


def datetime(*args, tzname: str = 'Asia/Seoul') -> dt.datetime:
    return get_timezone(tzname).localize(dt.datetime(*args))


def fromtimestamp(timestamp: float, tzname: str = 'Asia/Seoul') -> dt.datetime:
    return get_timezone(tzname).localize(dt.datetime.fromtimestamp(timestamp))


def fromisoformat(date_str: str, tzname: str = 'Asia/Seoul') -> dt.datetime:
    return get_timezone(tzname).localize(dt.datetime.fromisoformat(date_str))
