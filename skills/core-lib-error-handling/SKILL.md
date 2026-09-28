---
name: core-lib-error-handling
description: MANDATORY — load this skill BEFORE you add, change, raise, or catch ANY exception, error class, error code, validation-failure type, or `errors.py`/`exceptions.py` module in a *-core-lib; and before deciding which HTTP status a refusal means. Everything error-shaped lives in `error_handling/`, one class per file, subclassing core-lib's `StatusCodeException` with a per-class `STATUS_CODE`.
---

# Errors in a core-lib

`core_lib/error_handling/` is the pattern — copy its shape, do not invent one:

```
core_lib/error_handling/
  status_code_exception.py      # class StatusCodeException
  core_lib_init_exception.py    # class CoreLibInitException
  not_found_decorator.py        # class NotFoundErrorHandler
  duplicate_error_decorator.py  # class DuplicateErrorHandler
  status_code_assert.py         # StatusCodeAssert
```

**One class per file. The file is named after the class, in snake_case.**

## Two hard rules

**1. Everything error-shaped lives in `<name>_core_lib/error_handling/` — nowhere else.**

That includes types that are **not exceptions**. A `ValidationError(code, message)`
returned in a list by `validate()` is a `@dataclass`, never raised — and it
still belongs here, because it is the library's error vocabulary and it is
exactly what the matching exception carries:

> **`validate()` itself may never raise either** — anything it raises is a 500
> naming no field, on exactly the half-finished input it exists to judge. Guard
> a half-declared precondition and any JSON blob you walk, once, at the top of
> the module. `AGENTS.md` §6.2.

```python
class AssessmentValidationError(AssessmentError):
    def __init__(self, errors):          # errors: List[ValidationError]
        self.errors = errors or []
```

Filing the dataclass under `data_layers/data/data_types/` because "it is a
dataclass, not an exception" splits one concept across two packages and hides
that the pair belongs together. **`error_handling/` wins over `data_types/`:
the more specific home takes precedence.**

**2. No `errors.py` / `exceptions.py` grab-bag.** Five classes in one module is
the thing this skill exists to prevent. `grep -c "^class " error_handling/*.py`
must print `1` for every file.

## The canonical shape

One base per library, then one file per situation:

```python
# error_handling/foo_error.py
from core_lib.error_handling.status_code_exception import StatusCodeException


class FooError(StatusCodeException):
    """Base for this library's errors: a status code fixed per subclass."""

    STATUS_CODE = None          # NOT defaulted — see below

    def __init__(self, *args):
        super().__init__(self.STATUS_CODE, *args)
```

```python
# error_handling/immutable_foo_error.py
from http import HTTPStatus

from foo_core_lib.error_handling.foo_error import FooError


class ImmutableFooError(FooError):
    """Raised when publishing over an existing (project_id, key, version).

    409: nothing is wrong with the request; it conflicts with what is already
    stored, and the fix is to publish a new version rather than correct input.
    """

    STATUS_CODE = HTTPStatus.CONFLICT
```

Why it is shaped that way:

- **Subclass `StatusCodeException`.** A host maps any error to a response by
  reading `error.status_code` — without importing your classes or knowing which
  library raised it. A bare `Exception` forces every consumer to write its own
  mapping table and keep it in step with your package.
- **`STATUS_CODE` is a CLASS attribute, not a constructor argument.** These are
  not flavours of one error a caller picks a code for; each names one situation
  that always means the same thing to a client, so no raise site can get it
  wrong.
- **Never default `STATUS_CODE`.** A default is a trap: a new error type
  silently inherits whatever the last one used and is reported to clients as
  something it is not. Leave it `None` and let the test below fail the build.
- **Each subclass's docstring states WHY that status**, not just which. "409
  because the stored resource is what forbids this, not the request" is the
  part a reviewer cannot re-derive.

## Choosing the status

| Situation | Status |
|---|---|
| content is well-formed but cannot be processed (a definition that would not score) | **422** `UNPROCESSABLE_ENTITY` — the client shows these to the author; it does not retry |
| the request is fine, the STORED state forbids it (re-publishing a version, a trend on a trait, incomparable versions) | **409** `CONFLICT` |
| a row that must exist does not | **404** — usually raised for you by `@NotFoundErrorHandler()` on the CRUD base's `get` |
| a uniqueness violation | **409** via `@DuplicateErrorHandler()` — never hand-write `except IntegrityError` |
| a missing/empty required ARGUMENT | plain `ValueError` at the top of the service method — not an error class (§6) |

## Test it — walk the package, don't scan a namespace

One class per file means a new error is a new MODULE, and a module nothing
imports is invisible to a scan of any single namespace. Walk the package so the
check cannot be skipped:

```python
def error_classes():
    found = []
    for module in pkgutil.iter_modules(error_handling.__path__):
        namespace = importlib.import_module(
            '{}.{}'.format(error_handling.__name__, module.name))
        found.extend(
            value for value in vars(namespace).values()
            if isinstance(value, type) and issubclass(value, FooError)
            and value is not FooError)
    return found
```

Then assert, for every class found: it subclasses `StatusCodeException`, its
`STATUS_CODE` is not `None`, and an instance's `.status_code` is that value.
Adding `error_handling/some_new_error.py` without a status now fails the build
whether or not a service raises it yet.

## Interaction with `row_or_none`

If a service swallows the DataAccess's 404 to return `None`, it must catch
**only** 404. Once your errors are `StatusCodeException` subclasses too, a bare
`except StatusCodeException:` also swallows your 409 — turning "these versions
cannot be compared" into a silent "not found". See `core-lib-reuse`.

## Checklist

1. Is it error-shaped (an exception, a code, a failure record)? → `error_handling/`.
2. One class, one file, snake_case named after the class. No `errors.py`.
3. Subclass the lib's base, which subclasses `StatusCodeException`.
4. Set `STATUS_CODE` explicitly; docstring says why that code.
5. Package-walking test asserts every subclass declares one.
