import string
import random


def generate_random_string(length: int = 10):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))


def generate_email(domain: str = 'fdna.com'):
    return '{}@{}'.format(generate_random_string(), domain)