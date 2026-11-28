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
    if not dash:
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
    value = ''
    is_asking = True
    while is_asking:
        value = _prompt(message)
        is_asking = not value
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
    answer = None
    is_valid = True
    is_asking = True
    while is_asking:
        effective_title = title if is_valid else validate_fail_message
        raw = _prompt(_format(effective_title, default, allow_none))
        if not raw:
            answer = _empty_prompt_result(default, allow_none, allow_empty)
            is_asking = answer is None and not allow_none
            is_valid = True
        elif validate_callback and not validate_callback(raw):
            is_valid = False
        else:
            answer = raw
            is_asking = False
    return answer


def prompt_file_name(message: str) -> str:
    """Prompt for a safe file name (letters and underscores only, hyphens converted)."""
    safe_chars = string.ascii_letters + '_'
    answer = ''
    is_asking = True
    while is_asking:
        raw = _prompt(f'{message}: ')
        answer = ''.join(character for character in raw.replace('-', '_') if character in safe_chars)
        is_asking = not answer
    return answer


# ── bool / yes-no ─────────────────────────────────────────────────────────────


def prompt_yes_no(title: str, default: Optional[bool] = None) -> bool:
    """Prompt for yes/no. Retries until a valid answer is given."""
    if default is True:
        default_label = 'yes'
    elif default is False:
        default_label = 'no'
    else:
        default_label = None
    answer = default
    is_asking = True
    while is_asking:
        raw = _prompt(_format(f'{title} (yes/no)', default_label)).lower()
        if not raw and default is not None:
            answer = default
            is_asking = False
        elif raw in ('y', 'yes'):
            answer = True
            is_asking = False
        elif raw in ('n', 'no'):
            answer = False
            is_asking = False
    return answer


def prompt_bool(title: str, default: Optional[bool] = None, allow_none: bool = False) -> Optional[bool]:
    """Prompt for a boolean (true/false/1/0)."""
    answer = None
    is_asking = True
    while is_asking:
        raw = _prompt(_format(title, default, allow_none)).lower()
        if not raw and default is not None:
            raw = str(default).lower()
        if not raw:
            is_asking = not allow_none
        elif raw in ('true', '1'):
            answer = True
            is_asking = False
        elif raw in ('false', '0'):
            answer = False
            is_asking = False
    return answer


# ── numbers ───────────────────────────────────────────────────────────────────


def prompt_int(title: str, default: Optional[int] = None, allow_none: bool = False) -> Optional[int]:
    """Prompt for an integer."""
    answer = None
    is_asking = True
    while is_asking:
        raw = _prompt(_format(title, default, allow_none))
        if not raw:
            answer = default
            is_asking = default is None and not allow_none
        elif is_int(raw):
            answer = int(raw)
            is_asking = False
    return answer


# ── validated inputs ──────────────────────────────────────────────────────────


def prompt_email(title: str, default: Optional[str] = None) -> str:
    """Prompt for a valid email address."""
    value = ''
    is_asking = True
    while is_asking:
        raw = _prompt(_format(title, default))
        value = raw if raw else (default or '')
        is_asking = not is_email(value)
    return value


def prompt_url(title: str, default: Optional[str] = None, allow_empty: bool = False) -> str:
    """Prompt for a valid URL, optionally allowing an empty value."""
    answer = ''
    is_asking = True
    while is_asking:
        raw = _prompt(_format(title, default))
        value = _coalesce_prompt_value(raw, default)
        if allow_empty and not value:
            answer = ''
            is_asking = False
        elif is_url(value):
            answer = value
            is_asking = False
    return answer


def prompt_timeframe(title: str, default: Optional[str] = None, allow_empty: bool = False) -> str:
    """Prompt for a duration string (e.g. 1s, 1m, 1h30m, boot, startup)."""
    answer = ''
    is_asking = True
    while is_asking:
        raw = _prompt(_format(title, default))
        value = _coalesce_prompt_value(raw, default)
        if value in ('boot', 'startup'):
            answer = '0s'
            is_asking = False
        elif allow_empty and not value:
            answer = ''
            is_asking = False
        elif parse(value) is not None:
            answer = str(value)
            is_asking = False
    return answer


# ── selection ─────────────────────────────────────────────────────────────────


def prompt_enum(enum_class: enum.EnumMeta, title: str, default: Optional[int] = None) -> int:
    """Select from an Enum by its integer value. Prints `value-name` pairs, returns the int value."""
    valid_values = {item.value for item in enum_class}
    for item in enum_class:
        print(f'{item.value}-{item.name}')
    answer = None
    is_asking = True
    while is_asking:
        raw = _prompt(_format(title, default))
        value = _coalesce_prompt_value(raw, default)
        if is_int(value) and int(value) in valid_values:
            answer = int(value)
            is_asking = False
    return answer


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
    for position, option in enumerate(options, start=1):
        print(f'{position}. {option}')
    answer = default
    is_asking = True
    while is_asking:
        raw = _prompt(_format('Select an option by number', default))
        if not raw and default is not None:
            answer = default
            is_asking = False
        elif is_int(raw) and 1 <= int(raw) <= len(options):
            answer = options[int(raw) - 1]
            is_asking = False
    return answer


def prompt_list(
    list_values: list,
    title: str,
    default: Optional[int] = None,
    validate_callback: Optional[Callable[[str], bool]] = None,
    validate_fail_message: str = 'Value already present',
) -> int:
    """Select from a list by number. Returns the 0-based index of the selected item."""
    for position, item in enumerate(list_values, start=1):
        print(f'{position}-{item}')
    answer = None
    is_valid = True
    is_asking = True
    while is_asking:
        effective_title = title if is_valid else validate_fail_message
        raw = _prompt(_format(effective_title, default))
        value = _coalesce_prompt_value(raw, default)
        is_valid = True
        if is_int(value) and 0 < int(value) <= len(list_values):
            index = int(value) - 1
            if validate_callback and not validate_callback(list_values[index]):
                is_valid = False
            else:
                answer = index
                is_asking = False
    return answer


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
    is_asking = True
    while is_asking:
        _print_multi_select(title, items, selected, label, instructions, empty_message)
        raw = _prompt('> ')
        if raw.lower() in ('q', 'quit', 'exit'):
            result = None
            is_asking = False
        elif not raw:
            is_asking = False
        else:
            for index in _parse_toggle_indices(raw, len(items)):
                selected[index] = not selected[index]
    return result


def _parse_comma_list_or_none(raw: str, value_parser: Optional[Callable[[str], ListItem]]) -> Optional[list]:
    """The parsed items, or ``None`` when ``value_parser`` rejects one of them."""
    try:
        return parse_comma_separated_list(raw, value_parser=value_parser)
    except (TypeError, ValueError):
        return None


def prompt_comma_list(
    message: str,
    default: Optional[list] = None,
    allow_empty: bool = True,
    value_parser: Optional[Callable[[str], ListItem]] = None,
) -> list:
    """Prompt for a comma-separated list. Returns the parsed items."""
    answer = []
    is_asking = True
    while is_asking:
        raw = _prompt(_format(message, default))
        if not raw and default is not None:
            answer = list(default)
            is_asking = False
        else:
            parsed = _parse_comma_list_or_none(raw, value_parser)
            if parsed is not None and (parsed or allow_empty):
                answer = parsed
                is_asking = False
    return answer
