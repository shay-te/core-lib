---
id: parse_utils
title: Parse Utilities
sidebar: core_lib_doc_sidebar
permalink: parse_utils.html
folder: core_lib_doc
toc: false
---

Forgiving parsers for messy input, such as a spreadsheet import or a free-text form: booleans written as `'yes'`, dates in several formats, ranges like `'20 to 30'`, heights like `5'10`, and a fuzzy match of a value against a list of allowed options. Each function returns `None` (or the value you choose) for input it cannot read, instead of raising.

> **Optional utility.** You can use Core-Lib without them. The module imports **pandas**, which `pip install core-lib` does not install: run `pip install pandas` (it brings numpy, which the module also imports) before importing `core_lib.helpers.parse_utils`, or the import fails with `ModuleNotFoundError`.
>
> **Where it fits:** Where data first enters your app, usually a Service that imports rows, before they are validated and stored.

*core_lib.helpers.parse_utils* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/parse_utils.py){:target="_blank"}

## Text

### normalize()

Lowercases a value, strips accents (`é` → `e`), replaces every character that is not a letter or digit with a space, and collapses repeated spaces. A non-string is converted with `str()` first.

```python
def normalize(text: str) -> str:
```

### similarity()

How alike two strings are, from `0.0` to `1.0`, using `difflib.SequenceMatcher`. It compares the strings as given, so case matters: `similarity('Color', 'color')` is `0.8`. Normalize both first if it should not.

```python
def similarity(a: str, b: str) -> float:
```

### fetch_closest_option()

Returns the option most similar to `source`, compared after `normalize()`. Returns `None` when even the best score is below `threshold`, when `source` is not a string, or when `options` is empty. Options that are not strings, booleans included, are skipped.

```python
def fetch_closest_option(source: str, options: list, threshold: float = 0.89) -> Union[str, None]:
```

**Arguments**

- **`source`** *`(str)`*: The value to look up.
- **`options`** *`(list)`*: The allowed values. The matching option is returned as written in this list.
- **`threshold`** *`(float)`*: Default `0.89`. The lowest similarity accepted.

**Example**

```python
from core_lib.helpers.parse_utils import fetch_closest_option, normalize, similarity

print(normalize('  Café-au-Lait!!  '))                                 # cafe au lait
print(similarity('colour', 'color'))                                   # 0.9090909090909091
print(fetch_closest_option('Tel-Aviv', ['tel aviv', 'Jerusalem']))     # tel aviv
print(fetch_closest_option('Tel Avv', ['Tel Aviv', 'Haifa']))          # Tel Aviv  (similarity 0.93)
print(fetch_closest_option('Tel Avv', ['Tel Aviv'], threshold=0.95))  # None
```

## Lists and dicts

### clean_list()

Returns a copy of the list without `None`, `''`, `[]`, `{}` and `()`. Other falsy values such as `0`, `False` and `'0'` are kept. Anything that is not a list returns `[]`.

```python
def clean_list(list_to_clean: list) -> list:
```

### find_key_by_value()

Returns the first key whose value equals `target`, or `None`.

```python
def find_key_by_value(data, target):
```

**Example**

```python
from core_lib.helpers.parse_utils import clean_list, find_key_by_value

print(clean_list([1, None, '', [], {}, (), 0, False, 'a']))  # [1, 0, False, 'a']
print(clean_list('not a list'))                              # []
print(find_key_by_value({'a': 1, 'b': 2, 'c': 2}, 2))        # b
print(find_key_by_value({'a': 1}, 9))                        # None
```

## Values

### parse_bool()

Reads a boolean from a bool, the strings `'yes'`/`'true'`/`'1'` and `'no'`/`'false'`/`'0'` (any case, surrounding spaces ignored), or the ints `1` and `0`. Returns `None` for anything else, including other ints, floats such as `1.0`, and `None`.

```python
def parse_bool(value):
```

### parse_any_nan()

Replaces "no value" with `replace_with`: a float `NaN`, anything pandas considers missing (`None`, `pd.NaT`), and any string listed in `strings_to_replace`. A list, numpy array or pandas Series is processed item by item and returned as a list.

```python
def parse_any_nan(val, replace_with=None, strings_to_replace: tuple = ()):
```

**Arguments**

- **`val`**: The value, or a list, numpy array or pandas Series of values.
- **`replace_with`**: Default `None`. What a missing value becomes.
- **`strings_to_replace`** *`(tuple)`*: Default `()`. Strings that also count as missing. The value is stripped and lowercased before it is compared, so write these in lower case: `('n/a', 'none')` matches `' N/A '`, but `('N/A',)` matches nothing.

### float_to_str()

Formats a number as text. A float with no fraction loses its `.0` (`3.0` → `'3'`), `None` and `NaN` become `''`, and any other value is passed to `str()`. With `remove_dot=True` the decimal point of a fractional float is removed (`3.25` → `'325'`).

```python
def float_to_str(value, remove_dot: bool = False) -> str:
```

**Example**

```python
from core_lib.helpers.parse_utils import float_to_str, parse_any_nan, parse_bool

print([parse_bool(value) for value in [' Yes ', 'FALSE', 1, 0, 2, 'maybe']])  # [True, False, True, False, None, None]
print(parse_any_nan(float('nan'), replace_with=0))                          # 0
print(parse_any_nan(' N/A ', replace_with='', strings_to_replace=('n/a',)))  # '' (an empty string)
print(parse_any_nan([1, float('nan'), 'x'], replace_with=0))                # [1, 0, 'x']
print(float_to_str(3.0), float_to_str(3.25), float_to_str(3.25, remove_dot=True))  # 3 3.25 325
```

## Dates

### parse_date()

Parses a date string in one of these formats, trying them in this order, and returns a naive `datetime`. Returns `None` when none matches, for an empty string, and for an int or float (a timestamp is not read). A `datetime` is returned as it is.

| Format | Example |
|---|---|
| `%m/%d/%Y %I:%M:%S %p` | `03/15/2024 02:30:00 PM` |
| `%m/%d/%Y %I:%M %p` | `03/15/2024 02:30 PM` |
| `%m/%d/%Y` | `03/15/2024` (month first) |
| `%b %d, %Y` / `%B %d, %Y` | `Mar 15, 2024` / `March 15, 2024` |
| `%Y/%m/%d`, `%Y-%m-%d`, `%Y.%m.%d` | `2024/03/15`, `2024-03-15`, `2024.03.15` |
| `%d-%m-%Y`, `%d.%m.%Y` | `15-03-2024`, `15.03.2024` (day first) |

Before matching it lowercases the text, collapses spaces, tidies the spaces around `,` and `/`, and shortens a four-letter month word such as `sept` or `octo` to its three-letter form. A slash date is always month first, and a dash or dot date with the year last is always day first.

```python
def parse_date(value: Union[str, datetime, int, float]) -> Optional[datetime]:
```

**Example**

```python
from core_lib.helpers.parse_utils import parse_date

print(parse_date('03/15/2024 02:30 PM'))  # 2024-03-15 14:30:00
print(parse_date('mar 15,2024'))          # 2024-03-15 00:00:00
print(parse_date('sept 15, 2024'))        # 2024-09-15 00:00:00
print(parse_date('15.03.2024'))           # 2024-03-15 00:00:00
print(parse_date('yesterday'))            # None
```

## Ranges

### parse_range()

Reads a two-sided range written `'X to Y'` or `'X-Y'` (an en dash or em dash also works) and returns a `(lower, upper)` tuple. A bound written `any` takes `min_limit` or `max_limit`. Returns `None` when the text has no separator, more than two parts, an empty side, or an `any` without a matching limit.

```python
def parse_range(range_str: str, min_limit=None, max_limit=None):
```

**Arguments**

- **`range_str`** *`(str)`*: The text. Anything that is not a string returns `None`.
- **`min_limit`**, **`max_limit`**: What `any` means on each side.

**Returns**

A tuple. A bound made only of digits becomes an `int`; any other bound stays a string, so `'1.5-2'` gives `('1.5', 2)`.

The separator check is a plain substring test for `to` first, so a word containing `to` (`'tomato-potato'`) is split on `to` and returns `None`.

**Example**

```python
from core_lib.helpers.parse_utils import parse_range

print(parse_range('20 to 30'))                               # (20, 30)
print(parse_range('20 – 30'))                                # (20, 30)
print(parse_range('any to 30', min_limit=18, max_limit=99))  # (18, 30)
print(parse_range('any to 30'))                              # None: no min_limit
print(parse_range('1.5-2'))                                  # ('1.5', 2)
```

## Heights

### height_to_cm()

Reads a height and returns whole centimetres, or `None` when it cannot. The text must match one of these forms completely; anything around it, such as `'6 ft'` or `'tall'`, returns `None`.

| Input | Read as | Result |
|---|---|---|
| a number below `3`, such as `1.8` | metres | `180` |
| a number `3` or above, such as `180` | centimetres | `180` |
| `'180 cm'`, `'180cm'` | centimetres | `180` |
| `'1.80 m'`, `'1,80 m'` | metres (a comma works as the decimal point) | `180` |
| `5'10`, `5' 10"`, `6'` | feet and inches | `178`, `178`, `183` |
| `'5.5"'` (the `"` is required) | decimal feet | `168` |
| `'153 ס"מ'` | centimetres, with the Hebrew abbreviation | `153` |
| `'1.75'`, `'175'` | the number rules above | `175`, `175` |

```python
def height_to_cm(height_str):
```

Because `bool` is a kind of `int`, `height_to_cm(True)` returns `100` (one metre). Lists, dicts, sets, tuples, numpy arrays, pandas Series, `NaN` and infinity return `None`.

**Example**

```python
from core_lib.helpers.parse_utils import height_to_cm

print(height_to_cm(1.8))       # 180
print(height_to_cm('1,80 m'))  # 180
print(height_to_cm("5'10"))    # 178
print(height_to_cm('6 ft'))    # None
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="constants.html">Previous</a></button>
    <button class="pageNext-btn"><a href="shell_utils.html">Next</a></button>
</div>
