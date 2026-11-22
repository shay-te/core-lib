import enum
import string
from typing import Callable, Optional, Sequence, TypeVar

from pytimeparse import parse

from core_lib.helpers.validation import is_int, is_email, is_url, parse_comma_separated_list


OptionValue = TypeVar('OptionValue')
ListItem = TypeVar('ListItem')


# ── private helpers ──────────────────────────────────────────────────────────


def _prompt(message: str) -> str:
    return input(message).strip()


def _format(title: str, default=None, allow_none: bool = False) -> str:
    if default is not None:
        return f'{title} [default: {default}]: '
    if allow_none:
        return f'{title} [press Enter to skip]: '
    return f'{title}: '


def _empty_prompt_result(default=None, allow_none: bool = False, allow_empty: bool = False):
    if default is not None:
        return default
    if allow_none:
        return None
    if allow_empty:
        return ''
    return None


def _coalesce_prompt_value(raw: str, default) -> str:
    if raw:
        return raw
    if default is not None:
        return str(default)
    return ''


def _int_range(start_text: str, end_text: str) -> range:
    """The numbers from start to end inclusive, in either order; empty when either is not an int."""
    try:
        start = int(start_text)
        end = int(end_text)
    except ValueError:
        return range(0)
    return range(min(start, end), max(start, end) + 1)


def _toggle_token_numbers(token: str) -> range:
    """The 1-based numbers one token names: ``3``, or a range ``1-3``."""
    start_text, dash, end_text = token.partition('-')
    if not dash or not start_text:
        return _int_range(token, token)
    return _int_range(start_text, end_text)


def _parse_toggle_indices(raw: str, max_index: int) -> list:
    """Parse ``1,3,5`` / ``1 3 5`` / ``1-3,7`` into 0-based indices.

    Out-of-range and unparseable tokens are dropped silently — a typo in
    one token shouldn't drop the whole edit.
    """
    tokens = raw.replace(',', ' ').split()
    return [
        number - 1
        for token in tokens
        for number in _toggle_token_numbers(token)
        if 1 <= number <= max_index
    ]


# ── string ────────────────────────────────────────────────────────────────────


def prompt_string(message: str) -> str:
    """Simple string prompt that retries until the user enters a non-empty value."""
    while True:
        value = _prompt(message)
        if value:
            return value


def prompt_str(
    title: str,
    default: Optional[str] = None,
    allow_empty: bool = False,
    validate_callback: Optional[Callable[[str], bool]] = None,
    validate_fail_message: str = 'Invalid value, please try again',
    allow_none: bool = False,
) -> Optional[str]:
    """Prompt for a string with optional default, validation, and empty/none handling."""
    is_valid = True
    while True:
        effective_title = title if is_valid else validate_fail_message
        raw = _prompt(_format(effective_title, default, allow_none))
        if not raw:
            empty_result = _empty_prompt_result(default, allow_none, allow_empty)
            if empty_result is not None or allow_none or allow_empty:
                return empty_result
            is_valid = True
            continue
        if validate_callback and not validate_callback(raw):
            is_valid = False
            continue
        return raw


def prompt_file_name(message: str) -> str:
    """Prompt for a safe file name (letters and underscores only, hyphens converted)."""
    safe_chars = string.ascii_letters + '_'
    while True:
        raw = _prompt(f'{message}: ')
        result = ''.join(c for c in raw.replace('-', '_') if c in safe_chars)
        if result:
            return result


# ── bool / yes-no ─────────────────────────────────────────────────────────────


def prompt_yes_no(title: str, default: Optional[bool] = None) -> bool:
    """Prompt for yes/no. Retries until a valid answer is given."""
    if default is True:
        default_label = 'yes'
    elif default is False:
        default_label = 'no'
    else:
        default_label = None
    while True:
        raw = _prompt(_format(f'{title} (yes/no)', default_label)).lower()
        if not raw and default is not None:
            return default
        if raw in ('y', 'yes'):
            return True
        if raw in ('n', 'no'):
            return False


def prompt_bool(title: str, default: Optional[bool] = None, allow_none: bool = False) -> Optional[bool]:
    """Prompt for a boolean (true/false/1/0)."""
    while True:
        raw = _prompt(_format(title, default, allow_none)).lower()
        if not raw:
            if default is not None:
                raw = str(default).lower()
            elif allow_none:
                return None
            else:
                continue
        if raw in ('true', '1'):
            return True
        if raw in ('false', '0'):
            return False


# ── numbers ───────────────────────────────────────────────────────────────────


def prompt_int(title: str, default: Optional[int] = None, allow_none: bool = False) -> Optional[int]:
    """Prompt for an integer."""
    while True:
        raw = _prompt(_format(title, default, allow_none))
        if not raw:
            if default is not None:
                return default
            if allow_none:
                return None
            continue
        if is_int(raw):
            return int(raw)


# ── validated inputs ──────────────────────────────────────────────────────────


def prompt_email(title: str, default: Optional[str] = None) -> str:
    """Prompt for a valid email address."""
    while True:
        raw = _prompt(_format(title, default))
        value = raw if raw else (default or '')
        if is_email(value):
            return value


def prompt_url(title: str, default: Optional[str] = None, allow_empty: bool = False) -> str:
    """Prompt for a valid URL, optionally allowing an empty value."""
    while True:
        raw = _prompt(_format(title, default))
        value = _coalesce_prompt_value(raw, default)
        if allow_empty and not value:
            return ''
        if is_url(value):
            return value


def prompt_timeframe(title: str, default: Optional[str] = None, allow_empty: bool = False) -> str:
    """Prompt for a duration string (e.g. 1s, 1m, 1h30m, boot, startup)."""
    while True:
        raw = _prompt(_format(title, default))
        value = _coalesce_prompt_value(raw, default)
        if value in ('boot', 'startup'):
            return '0s'
        if allow_empty and not value:
            return ''
        if parse(value) is not None:
            return str(value)


# ── selection ─────────────────────────────────────────────────────────────────


def prompt_enum(enum_class: enum.EnumMeta, title: str, default: Optional[int] = None) -> int:
    """Select from an Enum by its integer value. Prints `value-name` pairs, returns the int value."""
    valid_values = {item.value for item in enum_class}
    for item in enum_class:
        print(f'{item.value}-{item.name}')
    while True:
        raw = _prompt(_format(title, default))
        value = _coalesce_prompt_value(raw, default)
        if is_int(value) and int(value) in valid_values:
            return int(value)


def prompt_options(
    message: str,
    options: Sequence[OptionValue],
    default: Optional[OptionValue] = None,
) -> OptionValue:
    """Select from a list by number. Prints a numbered menu, returns the selected item."""
    options = list(options)
    if not options:
        raise ValueError('options must not be empty')
    if default is not None and default not in options:
        raise ValueError('default must be one of the provided options')
    print(message)
    for i, option in enumerate(options, start=1):
        print(f'{i}. {option}')
    while True:
        raw = _prompt(_format('Select an option by number', default))
        if not raw and default is not None:
            return default
        if is_int(raw):
            idx = int(raw)
            if 1 <= idx <= len(options):
                return options[idx - 1]


def prompt_list(
    list_values: list,
    title: str,
    default: Optional[int] = None,
    validate_callback: Optional[Callable[[str], bool]] = None,
    validate_fail_message: str = 'Value already present',
) -> int:
    """Select from a list by number. Returns the 0-based index of the selected item."""
    for i, item in enumerate(list_values):
        print(f'{i + 1}-{item}')
    is_valid = True
    while True:
        effective_title = title if is_valid else validate_fail_message
        raw = _prompt(_format(effective_title, default))
        value = _coalesce_prompt_value(raw, default)
        if is_int(value) and 0 < int(value) <= len(list_values):
            idx = int(value) - 1
            if validate_callback and not validate_callback(list_values[idx]):
                is_valid = False
                continue
            return idx
        is_valid = True


def _initial_multi_select_state(items: list, initial_selected: Optional[Sequence[bool]]) -> list:
    if initial_selected is None:
        return [False] * len(items)
    selected = [bool(is_selected) for is_selected in initial_selected]
    if len(selected) != len(items):
        raise ValueError('initial_selected must match items in length')
    return selected


def _print_multi_select(
    title: str,
    items: list,
    selected: list,
    label: Callable[[ListItem], str],
    instructions: str,
    empty_message: str,
) -> None:
    print()
    print(title)
    if not items:
        print(f'  {empty_message}')
    for position, (item, is_selected) in enumerate(zip(items, selected), start=1):
        mark = '[x]' if is_selected else '[ ]'
        print(f'  {position:>3}. {mark}  {label(item)}')
    print()
    print(instructions)


def prompt_multi_select(
    items: Sequence[ListItem],
    title: str,
    initial_selected: Optional[Sequence[bool]] = None,
    label_for: Optional[Callable[[ListItem], str]] = None,
    instructions: str = (
        'Type indices to toggle (e.g. 1,3,5-7), '
        'or press Enter to apply. Type "q" to cancel.'
    ),
    empty_message: str = '(no items)',
) -> Optional[list]:
    """Toggle-list picker with ``[x]`` / ``[ ]`` checkboxes.

    Operator types comma-separated indices or ranges (``1,3,5-7``) to toggle
    selection, presses Enter to apply, or types ``q`` to cancel. Returns the
    final selection state as a list of bools parallel to ``items``, or
    ``None`` on cancel.

    ``label_for`` formats each row's text after the checkbox; defaults to
    ``str(item)``. The caller owns all formatting (alignment, suffixes,
    warnings) — the picker only owns index, checkbox, and the toggle loop.
    """
    items = list(items)
    selected = _initial_multi_select_state(items, initial_selected)
    label = label_for if label_for is not None else str

    result = selected
    is_choosing = True
    while is_choosing:
        _print_multi_select(title, items, selected, label, instructions, empty_message)
        raw = _prompt('> ')
        if raw.lower() in ('q', 'quit', 'exit'):
            result = None
            is_choosing = False
        elif not raw:
            is_choosing = False
        else:
            for index in _parse_toggle_indices(raw, len(items)):
                selected[index] = not selected[index]
    return result


def prompt_comma_list(
    message: str,
    default: Optional[list] = None,
    allow_empty: bool = True,
    value_parser: Optional[Callable[[str], ListItem]] = None,
) -> list:
    """Prompt for a comma-separated list. Returns the parsed items."""
    while True:
        raw = _prompt(_format(message, default))
        if not raw:
            if default is not None:
                return list(default)
            if allow_empty:
                return []
        try:
            parsed = parse_comma_separated_list(raw, value_parser=value_parser)
        except (TypeError, ValueError):
            continue
        if parsed or allow_empty:
            return parsed
