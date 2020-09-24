import string
import random
from datetime import datetime, timedelta


def generate_random_string(length: int = 10):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))


def generate_email(domain: str = 'domain.com'):
    return '{}@{}'.format(generate_random_string(), domain)


def generate_datetime(from_date: datetime = None, to_date: datetime = None):
    today = datetime.today()
    if not from_date:
        from_date = today - timedelta(days=10)
    if not to_date:
        to_date = today + timedelta(days=10)
    first_timestamp = int(from_date.timestamp())
    second_timestamp = int(to_date.timestamp())
    random_timestamp = random.randint(first_timestamp, second_timestamp)
    return datetime.fromtimestamp(random_timestamp)
