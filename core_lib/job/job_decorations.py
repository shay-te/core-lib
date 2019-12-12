import schedule

time_units = ['s', 'm', 'h', 'd', 'w']


def parse_input_time_string(expression: str):
    if not isinstance(expression, str): raise ValueError('expression must be a tring')
    if not expression: raise ValueError('expression must be set. with format 1s = 1 seconds, 2m = 2 minutes. supported time frames are, s, m, h, d, w')
    if str.isdigit(expression): raise ValueError('time frame must be supplied to time expression')

    time = expression[0:-1]
    time_frame = expression[-1]

    if not str.isdigit(time):
        raise ValueError('time must be an int: {}'.format(time))
    if time_frame not in time_units:
        raise ValueError('time frame is not supported, supported time frames are: {}'.format(time_units))

    return int(time), time_frame




    # if groups:
    #     time = groups.group()
    #     time_frame = groups.group(1)
    #
    #     return time, time_frame
    # else:
    #     raise ValueError('Unable to parse time expression {}'.format(expression))


class Every(object):

    def __init__(self, expression: str):
        self.time, self.time_frame = parse_input_time_string(str)

    def __call__(self, func, *args, **kwargs):
        def __wrapper(request, *args, **kwargs):
            if self.time_frame == 's':
                schedule.every(self.expression).seconds.do(func)
            if self.time_frame == 'm':
                schedule.every(self.expression).minutes.do(func)
            if self.time_frame == 'h':
                schedule.every(self.expression).hours.do(func)
            if self.time_frame == 'd':
                schedule.every(self.expression).days.do(func)
            if self.time_frame == 'e':
                schedule.every(self.expression).weeks.do(func)

        return __wrapper


class On(object):

    def __init__(self, expression: str):
        self.time, self.time_frame = parse_input_time_string(str)

    def __call__(self, func, *args, **kwargs):
        def __wrapper(request, *args, **kwargs):
            return ''
        return __wrapper
