---
id: generate_data
title: Generate Data
sidebar: core_lib_doc_sidebar
permalink: generate_data.html
folder: core_lib_doc
toc: false
---

Three generators for throwaway test data: a random string, a random email address, and a random date in a range.

> **Optional utility.** You can use Core-Lib without them. They use Python's `random` module, so they are **not** for passwords, tokens or anything secret (use the `secrets` module for that). If you already use a library such as Faker, keep using it.
>
> **Where it fits:** Tests and seed scripts. Nothing in Core-Lib's own code calls them.

## Functions

### generate_random_string()

*core_lib.helpers.generate_data.generate_random_string()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/generate_data.py#L6){:target="_blank"}

Generates a random string, 10 characters long by default, picked from lowercase letters. The flags add uppercase letters, digits or punctuation to the characters it picks from, so a given result may still contain none of them.

```python
def generate_random_string(length: int = 10, upper: bool = False, digits: bool = False, special: bool = False) -> str:
```

**Arguments**

- **`length`** *`(int)`*: Default `10`. Length of the generated string.
- **`upper`** *`(bool)`*: Default `False`. When `True`, uppercase letters can appear.
- **`digits`** *`(bool)`*: Default `False`. When `True`, digits can appear.
- **`special`** *`(bool)`*: Default `False`. When `True`, punctuation (`string.punctuation`) can appear.

**Returns**

*`(str)`*: The random string.

**Example**

```python
from core_lib.helpers.generate_data import generate_random_string

print(generate_random_string())                      # e.g. staugxgjxd (lowercase only)
print(generate_random_string(10, upper=True))        # e.g. OZiqjsvwfV
print(generate_random_string(5, digits=True))        # e.g. n5mz9
print(generate_random_string(10, True, True, True))  # e.g. P$a@T#3Z,a
```

### generate_email()

*core_lib.helpers.generate_data.generate_email()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/generate_data.py#L17){:target="_blank"}

Generates an email address at `domain`. The part before `@` is 10 random lowercase letters.

```python
def generate_email(domain: str = 'domain.com') -> str:
```


**Arguments**

- **`domain`** *`(str)`*: Default `domain.com`. The domain after `@`.

**Returns**

*`(str)`*: A random email address.

**Example**

```python
from core_lib.helpers.generate_data import generate_email

print(generate_email())               # e.g. qsrhbaykhg@domain.com
print(generate_email('example.com'))  # e.g. kdlndqlmso@example.com
```

### generate_datetime()

*core_lib.helpers.generate_data.generate_datetime()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/generate_data.py#L21){:target="_blank"}

Picks a random moment between `from_date` and `to_date`, then returns **that day at 00:00**: the time is always dropped. Without arguments the range is from 10 days ago to 10 days from now. It uses local time (`datetime.today()`, `datetime.fromtimestamp()`), not UTC.

Because the time is dropped, the result can be earlier than `from_date` on the same day: with `from_date` at 15:00 today, a result of today 00:00 is possible.

```python
def generate_datetime(from_date: datetime = None, to_date: datetime = None) -> datetime:
```

**Arguments**

- **`from_date`** *`(datetime)`*: Default `None` (10 days ago). Start of the range.
- **`to_date`** *`(datetime)`*: Default `None` (10 days from now). End of the range.

**Returns**

*`(datetime)`*: A random day in the range, at 00:00 local time.

**Example**

```python
from datetime import datetime, timedelta
from core_lib.helpers.generate_data import generate_datetime

print(generate_datetime())  # e.g. 2026-09-30 00:00:00 (10 days ago to 10 days from now)

now = datetime.now()
print(generate_datetime(now, now + timedelta(days=10)))  # e.g. 2026-10-12 00:00:00 (today to 10 days from now)
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="function_utils.html">Previous</a></button>
    <button class="pageNext-btn"><a href="instantiate_config.html">Next</a></button>
</div>