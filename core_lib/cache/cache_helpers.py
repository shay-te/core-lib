"""Checks the cache handlers share. Every handler refuses what it cannot keep exactly as given, and never rewrites
it, so the caller decides what to do. Each handler keeps its backend's own range: RAM takes any key, value and
expire; Redis any key and an expire to the millisecond; memcached refuses keys itself (python-memcached raises
`MemcachedKeyError`) and keeps whole seconds."""
from datetime import timedelta

NO_TIME = timedelta(0)


def validate_json_cache_value(value):
    # Redis and memcached keep the value as JSON
    if not isinstance(value, (dict, list, int, str)):
        raise ValueError(f'result must be of type `dict`, `list`, `int` or `str`. got `{type(value)}`')


def whole_expire(expire: timedelta, unit: timedelta, unit_name: str) -> int:
    """`expire` as the whole number of `unit`s a backend's protocol sends: memcached takes whole seconds (`unit` 1 s),
    Redis's `PX` whole milliseconds (`unit` 1 ms). Returns that number: 3 s in seconds is `3`, 1.5 s in milliseconds
    is `1500`.

    An expire of 0 or less raises `ValueError`. Never rounded or cut: a caller's business rule chose that time. Cut
    to fit, 1.5 s would reach memcached as 1 s, and 0.5 s as 0, which memcached reads as "never expire". So an expire
    the backend cannot keep exactly raises `ValueError`, and the caller decides what to send instead."""
    if expire <= NO_TIME:
        # Redis refuses it, and memcached would read 0 as "never expire" and a negative time as "already expired"
        raise ValueError(f'expire must be more than 0. got `{expire!r}`')
    # `timedelta % timedelta` is what is left over after the whole units, and a zero timedelta is false: 3 s % 1 s
    # leaves nothing, 1.5 s % 1 s leaves 0.5 s, which memcached cannot keep
    if expire % unit:
        raise ValueError(f'expire must be a whole number of {unit_name}. got `{expire!r}`')
    return expire // unit  # `timedelta // timedelta` is an int: how many whole units fit
