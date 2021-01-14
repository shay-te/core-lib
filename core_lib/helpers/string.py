def snake_to_camel(snake_str):
    return ''.join(x.title() for x in snake_str.split('_'))


def camel_to_snake(s):
    return ''.join(['_'+c.lower() if c.isupper() else c for c in s]).lstrip('_')

