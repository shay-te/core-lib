---
name: core-lib-tests
description: Write tests for a *-core-lib — one TestCase per file (filename mirrors the class), real collaborators over mocks (mock only at infra boundaries), an end-to-end test_flow.py, and generic agnostic fixtures. Use when asked to add or fix tests for a core-lib service/data-access/connection, or to raise coverage.
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

Class `TestWidgetServiceGet` → `test_widget_service_get.py`. The class name is
the contract; the filename advertises the behaviour under test. Shared fakes go
in a sibling **no-`test_`-prefix** helper module (`widget_service_helpers.py`);
single-use fakes stay at the top of the one file that needs them.

## Real collaborators over mocks

```python
import unittest

from my_core_lib.data_layers.data_access.widget_data_access import WidgetDataAccess
from my_core_lib.data_layers.service.widget_service import WidgetService
from tests.in_memory_db import build_in_memory_db          # real session, sqlite
from tests.reset_cache_registry import reset_cache_registry


class TestWidgetServiceGet(unittest.TestCase):
    def setUp(self):
        reset_cache_registry()
        self.db = build_in_memory_db()
        self.service = WidgetService(WidgetDataAccess(self.db))   # real, not MagicMock

    def test_get_returns_created_widget(self):
        created = self.service.create({'name': 'acme-widget'})
        loaded = self.service.get(created['id'])
        self.assertEqual('acme-widget', loaded['name'])
```

**Mock at infrastructure boundaries, not internal seams.** The litmus test: if
swapping a mock for one that always returns `None`/`{}` leaves every assertion
passing, the test is testing the mock, not behaviour.

- **Mock**: DB session (or use in-memory SQLite), outbound HTTP/SDK clients
  (inject a fake through the connection factory's `config['client']`), the
  clock, destructive filesystem.
- **Don't mock**: the SUT's pure-Python collaborators, enums/dataclasses/value
  objects, sibling Services inside the same lib.

## Agnostic fixtures (non-negotiable)

Fixtures use **generic example data** — `acme/widget`, `reviewer`, `PROJ-1`,
generic env-var names. Never the host product's name, brand, CLI, or env-var
prefix anywhere in source, tests, comments, docstrings, field names, or
fixtures (AGENTS.md "this library is AGNOSTIC", §3).

## End-to-end flow

Add one `test_flow.py` driving the primary workflow A→Z against mocked I/O
(`unittest.mock`; no network, no DB beyond in-memory, no real subprocess).

## Rules to enforce (from AGENTS.md)

- One TestCase per file; filename mirrors the class.
- Real collaborators; mock only at infra boundaries.
- 100% coverage of public functions; one `test_flow.py`.
- Generic fixtures — fully agnostic.
- Never commit `.coverage` / `.coverage.*` (delete before staging).
