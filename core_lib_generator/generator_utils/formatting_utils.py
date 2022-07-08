import re


def add_tab_spaces(string: str, tab_count: int = 1, tab_size: int = 4) -> str:
    return f'{tab_count * tab_size * " "}{string}'


def remove_line(pattern: str, string: str) -> str:
    return re.sub(".*" + pattern + ".*\n?", "", string)
