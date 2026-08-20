---
name: core-lib-tests
description: MANDATORY — load this skill BEFORE you add, fix, or restructure any test for a *-core-lib (entity/data-access/service/connection), raise coverage, or de-mock a test; do not write it from memory. Enforces one unittest.TestCase per file (filename mirrors the class), real collaborators over mocks (mock only DB/SDK/clock boundaries), agnostic fixtures, and an end-to-end test_flow.py.
---

# Write core-lib tests

Tests live **inside the library**, test **only the library**, and never import
host code. Prefer real collaborators; mock only at infrastructure boundaries.

## Steps

1. Put the test under the lib's `tests/` tree.
2. One `unittest.TestCase` per file; filename = snake_case of the class name.
3. Wire the real Service over a real DataAccess against an **in-memory SQLite**
   session; mock only the DB session factory / outbound SDK / clock / dangerous
   filesystem.
4. Reset the cache registry per test so cached rows don't leak.
5. Use generic fixture data; aim for full coverage of public methods +
   one `test_flow.py` driving the primary workflow A→Z.

## One TestCase per file

Class `TestThingService` → `test_thing_service.py`. One `unittest.TestCase` per
file, every test a method of it (§13.6).

## Test the REAL composed lib — never a bespoke harness

**A test calls only public service methods on the composed `FooCoreLib`.** The
DataAccess is internal and is never touched from a test. Wiring
`Service(DataAccess(db))` yourself is a **bespoke harness and is rejected in
review** — "everything comes from the core lib, this is final" (§0, §13.2–13.3).

```python
import unittest

from foo_core_lib.data_layers.data.db.entities.thing import Thing
from tests.helpers.utils import sync_create_start_core_lib, new_project_id

ABSENT_THING_ID = 2_000_000_000        # far above any autoincrement — never 99/999


class TestThingService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.foo_core_lib = sync_create_start_core_lib()   # FULL lib name, not cls.lib

    def test_create_returns_the_thing(self):
        project_id = new_project_id()                     # fresh scope per test
        thing = self.foo_core_lib.thing.create(project_id, 'acme-widget')
        self.assertEqual('acme-widget', thing[Thing.name.key])   # entity keys, not 'name'
```

Load-bearing details (§13.4, §13.6):

- `setUpClass` is exactly `cls.foo_core_lib = sync_create_start_core_lib()`; the
  bootstrap lives in `tests/helpers/utils.py` (ONE composed lib per process, a
  `CoreLibInstance` holder, and a **mandatory `finally: threadLock.release()`** —
  a lock held after a failed boot silently deadlocks the next suite).
- Access is inline and fully spelled: `self.foo_core_lib.thing.create(...)`.
  **No `@property` accessors, no `service = self.foo_core_lib.thing` aliases.**
- The DB is shared across the whole run: take a fresh `new_project_id()` per
  test; never assume an empty table or an absolute autoincrement value.
- Read dict fields with entity keys (`row[Thing.name.key]`), never literals.
  Enum columns assert the INT value, optionally round-tripped through the enum.
- Fixtures are created THROUGH services, and state is verified THROUGH services.
- The smoke file `test_foo_core_lib.py` asserts the PUBLIC surface only.

## The formula (non-negotiable)

**Assert the data you WANT the function to return — recomputed independently —
never the data it happens to return.** Expected values are hardcoded (§13.1).

## What may be mocked

Only what genuinely cannot run on a test host: a backend requiring absent
binaries (through a sanctioned seam in `tests/helpers/utils.py`, not in the
test), or fake SDK *modules* via `mock.patch.dict(sys.modules, {...})`. The
real `@Cache` / `@ResultToDict` / `@DuplicateErrorHandler`, real rule
validators, and a real in-memory sqlite DB always run (§13.2).

**No standalone DB-DataAccess test files** — the DA is exercised through its
service (§13.3).

## Agnostic fixtures (non-negotiable)

Fixtures use **generic example data** — `acme/widget`, `reviewer`, `PROJ-1`,
generic env-var names. Never the host product's name, brand, CLI, or env-var
prefix anywhere in source, tests, comments, docstrings, field names, or
fixtures (AGENTS.md "this library is AGNOSTIC" → "Self-contained and fully tested").

## End-to-end flow

Add one `test_flow.py` driving the primary workflow A→Z against mocked I/O
(`unittest.mock`; no network, no DB beyond in-memory, no real subprocess).

## Rules to enforce (from AGENTS.md)

- One `unittest.TestCase` per file; filename mirrors the class (§13).
- Real collaborators; mock only at true infra boundaries (§13).
- 100% coverage of public functions; one `test_flow.py` ("Self-contained and
  fully tested").
- Generic, product-free fixtures — fully agnostic.
- Never commit `.coverage` / `.coverage.*` (delete before staging).
