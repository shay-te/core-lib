def is_bool(st):
    st = str.lower(st)
    return st == "true" or st == "false"


def is_float(st):
    try:
        float(st)
        return True
    except ValueError:
        return False


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def decode_primitive(s):
    if is_bool(s):
        return str.lower(s) == "true"

    if is_int(s):
        return int(s)

    if is_float(s):
        return float(s)
