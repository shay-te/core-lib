def add_tab_spaces(string: str, tab_count: int = 1, tab_size: int = 4) -> str:
    return f'{tab_count * tab_size * " "}{string}'
