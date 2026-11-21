import string
import random
from datetime import datetime, timedelta


def generate_random_string(length: int = 10, upper: bool = False, digits: bool = False, special: bool = False) -> str:
    """
    Return `length` random characters. Lowercase letters are always allowed. Each of `upper`, `digits` and `special`
    (punctuation) adds its kind and promises at least one character of it, at a random position; a kind not asked
    for never appears. The string always has `length` characters: when that is fewer than the kinds asked for, it
    holds one character of as many of them as fit, picked at random.
    """
    required_kinds = []
    if upper:
        required_kinds.append(string.ascii_uppercase)
    if digits:
        required_kinds.append(string.digits)
    if special:
        required_kinds.append(string.punctuation)
    characters = random.choices(string.ascii_lowercase + ''.join(required_kinds), k=length)
    if not required_kinds:
        return ''.join(characters)
    if len(characters) < len(required_kinds):
        required_kinds = random.sample(required_kinds, len(characters))
    positions = random.sample(range(len(characters)), len(required_kinds))
    for position, kind in zip(positions, required_kinds):
        characters[position] = random.choice(kind)
    return ''.join(characters)


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
