import datetime
from pytimeparse import parse

#
# timedelta
#
from dateutil.relativedelta import relativedelta


def _next_weekday(weekday, hours: int = 0, minutes: int = 0):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return datetime.timedelta(days=days_ahead, hours=hours, minutes=minutes)


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


def next_month(hours: int = 0, minutes: int = 0):
    next_month_time = datetime.datetime.today().replace(day=1) + relativedelta(months=1)
    result = next_month_time - datetime.datetime.now()
    result = result + datetime.timedelta(hours=hours, minutes=minutes)
    return result


def midnight():
    return datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.datetime.now()


expresion_to_function = {
    'sunday': sunday,
    'monday': monday,
    'tuesday': tuesday,
    'wednesday': wednesday,
    'thursday': thursday,
    'friday': friday,
    'saturday': saturday,
    'next_month': next_month,
    'midnight': midnight
}


def parse(expresion: str):
    expression_function = expresion_to_function.get(expresion)
    if expression_function:
        return expression_function()
    else:
        seconds = parse(expresion)
        if seconds is not None:
            return datetime.timedelta(seconds=seconds)
    raise ValueError('Unable to parse timedelta expression `{}`'.format(expresion))
