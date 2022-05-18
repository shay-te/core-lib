def is_exists(user_input: str, items: list) -> bool:
    for item in items:
        if item['key'] == user_input:
            return False
    return True
