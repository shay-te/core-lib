---
name: core-lib-reuse
description: MANDATORY — load this skill BEFORE writing ANY helper, utility, decorator, converter, guard, encoder, parser, date/string/enum function, or a `helpers.py`/`utils.py` module in a *-core-lib; and before hand-writing a try/except or a dict-building loop that a core-lib decorator already does. Inventory of what `core_lib` already provides, so you call it instead of re-implementing a thinner, subtly-wrong copy.
---

# Check core-lib before you write a helper

A core-lib sits on top of `core_lib`, which already ships the conversions,
decorators and guards most libraries reinvent. **A re-implementation is almost
always THINNER than the original**, which is why this hides so well: the copy
looks correct, passes its tests, and silently drops the cases the original
handles.

The real example this skill exists for:

```python
# ⛔ WRONG — a hand-rolled result_to_dict that converts NOTHING
def _row(entity_row) -> dict:
    return {c.key: getattr(entity_row, c.key) for c in type(entity_row).__table__.columns}

# ✅ RIGHT — the same walk, plus enum -> int, datetime -> epoch, Decimal -> float
from core_lib.data_transform.result_to_dict import result_to_dict
result_to_dict(entity_row)
```

Both produce a dict of the same keys. Only one produces a payload that
survives JSON serialization — and the difference surfaces at a host, not here.

## The rule

**Grep before you write. If `core_lib` does 80% of it, call it and add the 20%.**

```python
encoded = result_to_dict(value)          # core-lib's job
return {k: v for k, v in encoded.items() if k not in _NOT_IN_A_TEMPLATE}
```

And when you DO have to write one, say in the docstring that you checked and
what core-lib lacks — so the next reader does not re-run your search.

## Inventory — what `core_lib` already provides

**Decorators (reach for these before any try/except or manual conversion)**

| Need | Use | Notes |
|---|---|---|
| service returns dicts, not ORM rows | `@ResultToDict()` — `core_lib.data_transform.result_to_dict` | walks entities/lists/tuples/Rows; converts enum→`.value`, datetime/date→epoch float, `Decimal`→float, follows relationships |
| the same conversion mid-function | `result_to_dict(value)` (the plain function) | same module |
| raise 404 when a getter finds nothing | `@NotFoundErrorHandler()` — `core_lib.error_handling.not_found_decorator` | raises `StatusCodeException(404)` when the result is **falsy**; already on the CRUD bases' `get` |
| map a uniqueness violation to 409 | `@DuplicateErrorHandler()` — `core_lib.error_handling.duplicate_error_decorator` | never hand-write `except IntegrityError` |
| cache a read | `@Cache(KEY, handler_name=...)` — `core_lib.cache.cache_decorator` | key templating via `build_function_key` |
| fire a host event | `@Observe(event_key=..., observer_name=...)` — `core_lib.observer.observer_decorator` | see `core-lib-observer` |
| turn a bare `assert` into a status code | `with StatusCodeAssert(code, msg):` — `core_lib.error_handling.status_code_assert` | context manager |
| validate one dict argument of your own DataAccess method | `@ParameterRuleValidator(rule_validator, 'data')` — `core_lib.rule_validator.rule_validator_decorator` | the dict must be passed **positionally** |
| log a line before each call | `@Logging('get_user_{user_id}')` — `core_lib.helpers.logging` | logs before the call only; no return value, no exception |

**Functions and classes** (each has a page in the docs; the ones under "Utilities (optional)" are
not needed to use Core-Lib)

| Module | Provides |
|---|---|
| `core_lib.helpers.datetime_utils` | `today/tomorrow/yesterday`, `day_begin/day_end`, `hour_begin/hour_end`, `week_begin/week_end`, `month_begin/month_end`, `year_begin/year_end`, every weekday (`monday`…`sunday`), `midnight`, `age(born)`, `timestamp_to_ms`, `reset_datetime` — UTC, naive, each `*_end()` the first moment of the NEXT period |
| `core_lib.helpers.validation` | `is_bool`, `is_int`, `is_float`, `is_email`, `is_url`, `is_int_enum`, `parse_comma_separated_list`, `parse_int_list` |
| `core_lib.helpers.parse_utils` | `parse_bool`, `parse_date`, `parse_range`, `parse_any_nan`, `normalize`, `similarity`, `fetch_closest_option`, `clean_list`, `float_to_str`, `find_key_by_value`, `height_to_cm` — imports **pandas**, which core-lib does not install |
| `core_lib.helpers.string` | `snake_to_camel` (gives PascalCase), `camel_to_snake`, `any_to_pascal` |
| `core_lib.data_transform.helpers` | `get_dict_attr(obj, 'a.b.c', default)`, `set_dict_attr`, `enum_to_dict` |
| `core_lib.helpers.func_utils` | `build_function_key`, `get_func_parameters_as_dict`, `get_func_parameter_index_by_name`, `Keyable` (how an object appears in keys), `UnseenFormatter` |
| `core_lib.helpers.config_instances` | `instantiate_config` (build the `_target_` class from YAML, with a base-class check), `instantiate_config_group_generator_dict` / `_list` |
| `core_lib.helpers.constants` | `MediaType`, `HttpMethod`, `HttpHeaders`, `TimeUnit`, `InstantiateConfigConstants` (`_target_`, `_instance_key_`, `_recursive_`) |
| `core_lib.helpers.thread` | `LockGroup` — one `threading.Lock` per key, in-process only |
| `core_lib.helpers.files` | `download_file`, `download_file_handle`, `get_file_md5` |
| `core_lib.helpers.generate_data` | `generate_random_string`, `generate_email`, `generate_datetime` — test data only, not for secrets |
| `core_lib.helpers.shell_utils` | `prompt_str`, `prompt_int`, `prompt_yes_no`, `prompt_options`, … — interactive CLI prompts |
| `core_lib.helpers.test` | `load_core_lib_config(path, file)` — clears the cache/observer registries and Hydra, composes a test config (path relative to the CALLING file) |
| `core_lib.data_layers.data.data_helpers` | `build_url(protocol, username, password, host, port, path, file)` — the connection-URL builder every factory uses |
| `core_lib.rule_validator.rule_validator` | `RuleValidator` / `ValueRuleValidator` — write-path validation; **never hand-roll a field allow-list** |
| `core_lib.rule_validator.helpers` | `convert_location`, `validate_location`, `convert_datetime` — ready-made `custom_converter`/`custom_validator`s |
| `core_lib.data_layers.data.db.join_config` | `JoinConfig`, `apply_join_configs` — joins a Service chooses at run time |
| `core_lib.data_layers.data.db.sqlalchemy.types` | `IntEnum` (enum column; values start at 1), `Point` (use its static helpers with a geoalchemy2 `Geometry('POINT')` column) |
| `core_lib.client.client_base` | `ClientBase` — HTTP API client with base URL, headers, timeout, auth (see `core-lib-connection`) |
| `core_lib.middleware` | `Middleware`, `MiddlewareChain` — a check or side effect shared by several methods |

## What core-lib does NOT provide (writing these is correct)

Verified by inventory, so you can stop looking:

- **No decoder.** `result_to_dict` is encode-only — there is no `dict_to_entity`.
- **No get-or-none.** `@NotFoundErrorHandler()` goes the OTHER way (`None` → raise 404). If a service must return `None` for an absent row, it swallows the DataAccess's 404 itself. Catch **only** 404 — a bare `except StatusCodeException:` also swallows a 409, turning a real answer into "not found":
  ```python
  def row_or_none(get, row_id):
      try:
          return get(row_id)
      except StatusCodeException as missing:
          if missing.status_code != HTTPStatus.NOT_FOUND:
              raise
          return None
  ```
- **No argument-guard helper.** `core_lib.helpers.validation` is `is_*`/`parse_*` only; `StatusCodeAssert` maps `AssertionError`, it does not check arguments. A lib-local `require(**kwargs)` raising `ValueError` is right (§6 convention).
- **No transient-default mixin**, and do not write one — a column `default=` fires at INSERT by design (§4).

## Where a lib-local helper goes

`<name>_core_lib/helpers.py`, at the **library root** — not under `service/`. A
DataAccess needs `require` too, and importing it from the layer above would
invert the dependency.

## Traps when adopting `result_to_dict`

- **It only converts values INSIDE a structure.** `result_to_dict(a_datetime)`
  returns the datetime unchanged; `result_to_dict({'x': a_datetime})` returns
  the epoch float. So a hand-built dict is converted by decorating the METHOD
  with `@ResultToDict()` — not by calling the function on each field.
- **It re-keys a dict through `str(key)`.** A `class K(str, Enum)` member used
  as a dict key becomes the literal `'K.MEMBER'`. Build such dicts with
  `K.MEMBER.value`; reads by member still work, because the hashes match.

## Checklist

1. Name the behaviour you need in one phrase ("entity → dict", "missing row → None").
2. Search the table above; then `grep -rn "def <verb>" <core-lib>/core_lib/`.
3. If it exists — call it. If it exists at 80% — call it and add the 20%.
4. If it genuinely does not — write it in `helpers.py` at the library root, and
   record in the docstring that you checked and what was missing.
