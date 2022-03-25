from re import split


def snake_to_camel(snake_str) -> str:
    return ''.join(x.title() for x in snake_str.split('_'))


def camel_to_snake(s) -> str:
    return ''.join(['_' + c.lower() if c.isupper() else c for c in s]).lstrip('_')


def any_to_pascal(string: str) -> str:
    pascal_string = []
    string = string[1:] if string[0].isnumeric() else string
    for word in split('([^a-zA-Z0-9])', string):
        if word.isalnum():
            if not word[0].isupper() and not word[0].isnumeric():
                word = word[:1].upper() + word[1:]
            pascal_string.append(word)
    return ''.join(pascal_string)
