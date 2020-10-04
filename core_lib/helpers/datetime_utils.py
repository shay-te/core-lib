from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def _next_weekday(weekday, hours: int = 0, minutes: int = 0):
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return today + timedelta(days=days_ahead, hours=hours, minutes=minutes)


_sunday_weekday = 6
_monday_weekday = 0
_tuesday_weekday = 1
_wednesday_weekday = 2
_thursday_weekday = 3
_friday_weekday = 4
_saturday_weekday = 5


def sunday(hours: int = 0, minutes: int = 0):
    return _next_weekday(_sunday_weekday, hours, minutes)


def monday(hours: int = 0, minutes: int = 0):
    return _next_weekday(_monday_weekday, hours, minutes)


def tuesday(hours: int = 0, minutes: int = 0):
    return _next_weekday(_tuesday_weekday, hours, minutes)


def wednesday(hours: int = 0, minutes: int = 0):
    return _next_weekday(_wednesday_weekday, hours, minutes)


def thursday(hours: int = 0, minutes: int = 0):
    return _next_weekday(_thursday_weekday, hours, minutes)


def friday(hours: int = 0, minutes: int = 0):
    return _next_weekday(_friday_weekday, hours, minutes)


def saturday(hours: int = 0, minutes: int = 0):
    return _next_weekday(_saturday_weekday, hours, minutes)


def tomorrow(hours: int = 0, minutes: int = 0):
    return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1, hours=hours, minutes=minutes)


def yesterday(hours: int = 0, minutes: int = 0):
    return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1) + timedelta(hours=hours, minutes=minutes)


def month_next(hours: int = 0, minutes: int = 0):
    return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).replace(day=1) + relativedelta(months=1, hours=hours, minutes=minutes)


def month_beginning(hours: int = 0, minutes: int = 0):
    return datetime.utcnow().replace(day=1, hour=hours, minute=minutes, second=0, microsecond=0)


def year_next(hours: int = 0, minutes: int = 0):
    return datetime.utcnow().replace(day=1, month=1, hour=hours, minute=minutes, second=0, microsecond=0) + relativedelta(years=1)


def year_beginning(hours: int = 0, minutes: int = 0):
    return datetime.utcnow().replace(day=1, month=1, hour=hours, minute=minutes, second=0, microsecond=0)


def midnight():
    return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.datetime.now()

