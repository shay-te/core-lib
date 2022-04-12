def add_tab_spaces(string: str, tab_size: int = 4) -> str:
    return string.rjust(len(string) + tab_size)
