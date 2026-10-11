---
id: shell_utils
title: Shell Prompts
sidebar: core_lib_doc_sidebar
permalink: shell_utils.html
folder: core_lib_doc
toc: false
---

Functions that ask a question in the terminal and keep asking until the answer is valid: a string with a default, a yes/no, a number, an email or URL, a duration, a choice from a menu, or a comma-separated list. `core_lib generate` uses them when you run it without `--yaml` and it asks you to describe your library.

> **Optional utility.** You can use Core-Lib without them. They are for interactive command-line scripts: they read with `input()`, so do not call them from a web request, a job or a test without replacing `builtins.input`.
>
> **Where it fits:** Setup and admin scripts you run by hand.

*core_lib.helpers.shell_utils* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/shell_utils.py){:target="_blank"}

## Example

```python
# new_project.py
from core_lib.helpers.shell_utils import (
    prompt_comma_list, prompt_int, prompt_options, prompt_str, prompt_timeframe, prompt_yes_no,
)

name = prompt_str('Project name', default='acme')
port = prompt_int('Port', default=8080)
region = prompt_options('Region:', ['eu-west-1', 'us-east-1'])
tags = prompt_comma_list('Tags (comma separated)')
frequency = prompt_timeframe('Sync every', default='1h')
confirmed = prompt_yes_no('Create it?', default=True)
print(name, port, region, tags, frequency, confirmed)
```

A session, with what the user typed after each colon:

```text
Project name [default: acme]:
Port [default: 8080]: abc
Port [default: 8080]: 9000
Region:
1. eu-west-1
2. us-east-1
Select an option by number: 3
Select an option by number: 2
Tags (comma separated): red, blue
Sync every [default: 1h]:
Create it? (yes/no) [default: yes]: maybe
Create it? (yes/no) [default: yes]: y
acme 9000 us-east-1 ['red', 'blue'] 1h True
```

## How every prompt behaves

- The question is printed as `Title: `. With a default it is `Title [default: value]: `, and when an empty answer is allowed to mean "nothing", `Title [press Enter to skip]: `.
- Leading and trailing spaces are stripped from the answer.
- An invalid answer asks the same question again, with no error message. The exceptions are `prompt_str()` and `prompt_list()` with a `validate_callback`: after a rejected answer, the next question shows `validate_fail_message` instead of the title.
- Pressing Enter returns the default when there is one. Without a default, most prompts ask again; the flags below change that.

## Functions

| Function | Returns | Accepts |
|---|---|---|
| `prompt_string(message)` | `str` | Any non-empty text. `message` is printed exactly as given, so end it with `': '`. |
| `prompt_str(title, default=None, allow_empty=False, validate_callback=None, validate_fail_message='Invalid value, please try again', allow_none=False)` | `str` or `None` | Any text that passes `validate_callback`. See below. |
| `prompt_file_name(message)` | `str` | Text reduced to letters and `_`; hyphens become `_`, everything else (digits, dots, spaces) is dropped: `my-file 2.txt` gives `my_filetxt`. Asks again if nothing is left. |
| `prompt_yes_no(title, default=None)` | `bool` | `y`, `yes`, `n`, `no`, any case. ` (yes/no)` is added to the title. |
| `prompt_bool(title, default=None, allow_none=False)` | `bool` or `None` | `true`, `1`, `false`, `0`, any case. With `allow_none=True`, Enter returns `None`. |
| `prompt_int(title, default=None, allow_none=False)` | `int` or `None` | A whole number such as `42` or `-5`; `3.5` and `0x10` are rejected. With `allow_none=True`, Enter returns `None`. |
| `prompt_email(title, default=None)` | `str` | A valid email address (`is_email` from [Validation Helpers](validation.html)). |
| `prompt_url(title, default=None, allow_empty=False)` | `str` | A valid URL (`is_url`). With `allow_empty=True`, Enter returns `''`. |
| `prompt_timeframe(title, default=None, allow_empty=False)` | `str` | A duration [pytimeparse](https://github.com/wroberts/pytimeparse){:target="_blank"} understands, such as `30s`, `1h30m` or `1d`, the format [jobs](job.html) use. `boot` and `startup` return `'0s'`. With `allow_empty=True`, Enter returns `''`. |
| `prompt_enum(enum_class, title, default=None)` | `int` | The value of a member. Prints `value-NAME` per member first and returns the **value**, not the member. |
| `prompt_options(message, options, default=None)` | the chosen item | A number from the printed `1. option` menu. Raises `ValueError` if `options` is empty or `default` is not one of them. |
| `prompt_list(list_values, title, default=None, validate_callback=None, validate_fail_message='Value already present')` | `int` | A number from the printed `1-item` menu. Returns the **0-based index**; `default` is given as the 1-based number. |
| `prompt_comma_list(message, default=None, allow_empty=True, value_parser=None)` | `list` | Comma-separated text. Empty items are dropped. See below. |

### prompt_str()

- **`default`**: Returned when the user presses Enter.
- **`allow_empty`**: When `True` and there is no default, Enter returns `''`.
- **`allow_none`**: When `True` and there is no default, Enter returns `None`. It wins over `allow_empty`.
- **`validate_callback`** *`(Callable[[str], bool])`*: Called with the stripped answer; returning `False` asks again. It is not called for an empty answer.
- **`validate_fail_message`**: Shown as the question after a rejected answer.

```python
from core_lib.helpers.shell_utils import prompt_str

code = prompt_str('Code', validate_callback=lambda value: value.isupper(), validate_fail_message='Use capitals')
```

```text
Code: abc
Use capitals: ABC
```

### prompt_comma_list()

- **`default`** *`(list)`*: Returned (as a copy) when the user presses Enter.
- **`allow_empty`**: Default `True`. When `False`, an answer with no items asks again.
- **`value_parser`** *`(Callable[[str], Any])`*: Converts each item, such as `int`. If it raises `ValueError` or `TypeError` for any item, the whole answer is asked again.

```python
from core_lib.helpers.shell_utils import prompt_comma_list

ports = prompt_comma_list('Ports', value_parser=int)
```

```text
Ports: 80, x
Ports: 80, 443
```

`ports` is `[80, 443]`.

## Testing code that prompts

Replace `builtins.input` with the answers, in order:

```python
from unittest import mock

from core_lib.helpers.shell_utils import prompt_int

with mock.patch('builtins.input', side_effect=['abc', '9000']):
    assert prompt_int('Port') == 9000   # 'abc' was rejected, so it asked twice
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="parse_utils.html">Previous</a></button>
    <button class="pageNext-btn"><a href="test_core_lib.html">Next</a></button>
</div>
