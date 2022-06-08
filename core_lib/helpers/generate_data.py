import string
import random
from datetime import datetime, timedelta


def generate_random_string(length: int = 10, upper: bool = False, digits: bool = False, special: bool = False) -> str:
    source = string.ascii_lowercase
    if upper:
        source = source + string.ascii_uppercase
    if digits:
        source = source + string.digits
    if special:
        source = source + string.punctuation
    return ''.join(random.choice(source) for _ in range(length))


def generate_email(domain: str = 'domain.com') -> str:
    return f'{generate_random_string()}@{domain}'


def generate_datetime(from_date: datetime = None, to_date: datetime = None) -> datetime:
    today = datetime.today()
    if not from_date:
        from_date = today - timedelta(days=10)
    if not to_date:
        to_date = today + timedelta(days=10)
    first_timestamp = int(from_date.timestamp())
    second_timestamp = int(to_date.timestamp())
    random_timestamp = random.randint(first_timestamp, second_timestamp)
    datetime_from_ms = datetime.fromtimestamp(random_timestamp)
    return datetime(year=datetime_from_ms.year, month=datetime_from_ms.month, day=datetime_from_ms.day)
