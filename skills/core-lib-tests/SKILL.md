---
name: core-lib-tests
description: MANDATORY — load this skill BEFORE you add, fix, or restructure any test for a *-core-lib (entity/data-access/service/connection), raise coverage, or de-mock a test; do not write it from memory. Tests must be ADVERSARIAL — written to break the code, covering edge cases and complete end-to-end user flows against the REAL composed library with almost no mocking. Enforces one unittest.TestCase per file (filename mirrors the class), real collaborators (mock only DB/SDK/clock boundaries), agnostic fixtures, and an end-to-end test_flow.py.
---

# Write core-lib tests

Tests live **inside the library**, test **only the library**, and never import
host code.

## The bar: a test suite that is HARD to pass

Write tests that are **as challenging as you can make them**. A suite that
only walks the happy path is not a safety net — it is a green light with
nothing behind it. Four standing requirements, each with its own section below:

1. **Try to BREAK the code.** Your job is to find the input that makes it
   wrong, not to demonstrate that it works.
2. **Cover the edges.** Empty, null, one, boundary, over-long, duplicate, out
   of order, wrong tenant, wrong type. The middle of the range is where bugs
   are not.
3. **Drive COMPLETE use cases end to end.** Whole flows a real user performs,
   not one method at a time.
4. **Use the REAL thing.** Almost nothing is mocked. A mock is a claim about
   how a collaborator behaves, and that claim is what breaks in production.

A test you were confident would pass before you ran it taught you nothing.
Aim to be surprised.

## Steps

1. Put the test under the lib's `tests/` tree.
2. One `unittest.TestCase` per file; filename = snake_case of the class name.
3. Compose the real library against a **real SQLite** database — the factory is
   *pointed* at sqlite, not mocked; the session, migrations and transactions are
   genuine. Mock only an outbound SDK / the clock / a dangerous filesystem call.
4. Reset the cache registry per test so cached rows don't leak.
5. Use generic fixture data; aim for full coverage of public methods +
   one `test_flow.py` driving the primary workflow A→Z.
6. **Now do the work that matters**: write the adversarial cases (§1), walk the
   edge-case checklist (§2), and drive complete user journeys (§3). Steps 1–5
   are the scaffolding; a suite that stops there is a green light with nothing
   behind it.

## One TestCase per file

Class `TestThingService` → `test_thing_service.py`. One `unittest.TestCase` per
file, every test a method of it (§13.6).

## Test the REAL composed lib — never a bespoke harness

**A test calls only public service methods on the composed `FooCoreLib`.** The
DataAccess is internal and is never touched from a test. Wiring
`Service(DataAccess(db))` yourself is a **bespoke harness and is rejected in
review** — "everything comes from the core lib, this is final" (§0, §13.2–13.3).

### The one carve-out: a stateless pure engine, ADDITIVE only

The rule exists to stop a hand-wired stack **standing in for** the composed one
and hiding a wiring bug. A stateless engine constructed with no arguments —
`ScorerService()`, no DataAccess, no DB, nothing faked — is not that. Calling it
directly to assert arithmetic is legitimate, and clearer than driving the same
sum through a publish-and-submit cycle:

```python
score = ScorerService().score        # module-level binding; pure, no I/O
```

It is legitimate **only as an extra layer**. The hard condition:

> **Every behaviour tested directly on an engine must ALSO be reached through
> the public surface by at least one test.** Every mode, branch and rule type —
> not "the engine is covered somewhere".

Check it, don't assume it. For each variant the engine handles, confirm a test
drives it through the real service:

```bash
for m in SUM WEIGHTED_AVG PICK_HIGHEST THRESHOLD CATEGORICAL; do
  grep -rl "ScoringMode.$m" tests/*.py | xargs grep -l "submission.submit" \
    || echo "*** $m is engine-only — no public-path test ***"
done
```

A variant that appears only in engine tests is a real gap: the wiring that
selects it is unproven, and the suite is green anyway.

**Private functions** (`_normalize`, `_is_newer`) may be imported into a test
only for a defensive branch genuinely unreachable from the public API — and
before writing that test, ask whether the branch should exist at all. An
unreachable arm is usually dead code to delete, not behaviour to pin (see
"Statement coverage cannot see an untaken branch" below).

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
- **Guard the no-literal rule with an AST walk over library source** — collect
  every column name off the entities, then flag any `ast.Constant` string in
  the library that matches, excluding `entities/` and `migrations/` (which
  declare the schema). Review cannot enforce this once names appear inside sets
  and constants, and a stale literal there fails silently. Pair it with a
  "would this catch a planted literal?" test, or an empty offender list quietly
  means the walk stopped working (§4.3).
  Enum columns assert the INT value, optionally round-tripped through the enum.
- Fixtures are created THROUGH services, and state is verified THROUGH services.
- The smoke file `test_foo_core_lib.py` asserts the PUBLIC surface only.

## The formula (non-negotiable)

**Assert the data you WANT the function to return — recomputed independently —
never the data it happens to return.** Expected values are hardcoded (§13.1).

Running the code to see what it prints and pasting that in is not a test: it
asserts the bug as readily as the fix. Compute the expected value by hand, from
the specification, and write the literal.

## 1. Try to BREAK the code

Approach each function as someone trying to make it produce a wrong answer, not
as someone confirming it produces a right one. For every method, ask:

- **What input makes this silently wrong?** Not "raise" — *wrong*. A raise is
  loud and someone will notice. A plausible-but-incorrect number is the bug
  that ships. Hunt those first.
- **What does the docstring promise that no test checks?** A claim in prose
  with no assertion behind it is a claim nobody has verified.
- **Which guard could I delete and still see green?** If you can remove an `if`
  and the suite passes, either the guard is dead or the test for it is missing.
  Actually try it: comment the guard out, run, put it back.
- **Where does an error become an absence?** A broad `except` that swallows a
  real failure into `None` reads as "not found" forever after. Test that the
  error you did NOT mean to swallow still escapes.

**Mutation-check a test you care about.** Break the code deliberately — flip a
`<` to `<=`, drop a `not`, return `0` instead of the computed value — and
confirm the test fails. A test that stays green against broken code is
decoration. Restore the code immediately.

Beware the **symmetric test**: encode-then-decode, write-then-read-back,
serialize-then-parse. It passes whatever the two halves agree on, including
agreeing on the wrong thing. Assert the intermediate form directly — walk the
actual blob and assert what it must NOT contain, not just that it round-trips.

## 2. Cover the edges

The middle of a range is where bugs are not. Work this checklist per method:

| Dimension | Cases to write |
|---|---|
| Cardinality | zero rows, exactly one, many; empty list vs `None` (they differ) |
| Boundaries | min, min−1, max, max+1; a zero-width range; equal values (ties) |
| Ordering | reversed input, duplicates, two rows with the SAME timestamp |
| Identity | absent id far above autoincrement, another tenant's id, `None` id |
| Strings | empty, whitespace, at the column limit, one over it, unicode |
| Numbers | `0`, negative, float precision (`0.1+0.2`), int-vs-float, rounding at `.5` |
| Enums | every member, and a value outside the enum |
| Lifecycle | soft-deleted row, re-created after delete, two versions live at once |
| Concurrency | the same operation twice (idempotent?), a second caller mid-flight |
| Optionality | every nullable column actually null, and every default not supplied |

Two that are missed most often: **a tie** (equal timestamps/scores — which wins,
and is it deterministic?), and **"empty is a legitimate answer"** (an empty
response list is a real submission, not a missing one; a guard that rejects
falsy rejects it).

## 3. Drive COMPLETE use cases end to end

Do not stop at one method per test. Write the **whole story a real user
performs**, in order, through public services only:

> publish an assessment → a subject takes it → read their scores → they take
> it again months later → read the trend → compare the two takes → an expert
> rates them → compare self-vs-expert → re-publish v2 → confirm the old take
> still scores against v1

Each step asserts real values, and the flow asserts things a single-method test
structurally cannot see: that step 4 still works after step 9 changed the
definition, that ids issued in step 1 are still valid in step 8, that nothing
leaked between two tenants running the same flow. Give the file a name that
says whose journey it is; `test_flow.py` is the minimum, not the ceiling.

## 4. Use the REAL thing — mock almost nothing

**A mock is a claim about how a collaborator behaves, and that claim is
precisely what breaks in production.** Fake DAs inside service tests hid three
real bugs in this codebase (§13.2). An over-mocked test passes in isolation and
fails against the actual system, which is the worst possible trade: it costs
you the work of writing it AND the confidence you thought you bought.

Always real, never mocked:

- the composed `FooCoreLib` and every service and DataAccess in it
- a real **sqlite** database, real migrations, real transactions
- real `@Cache`, `@ResultToDict`, `@Observe`, `@DuplicateErrorHandler`,
  `@NotFoundErrorHandler`
- real `RuleValidator`s, real enum coercion, real soft-delete filtering

**Mockable only if it genuinely cannot run on a test host:** a backend needing
absent binaries (through a sanctioned seam in `tests/helpers/utils.py`, never
inline in the test), a fake SDK *module* via
`mock.patch.dict(sys.modules, {...})`, an outbound network call, the clock.

Before writing `mock.patch`, answer: *what would this test catch that the real
thing would not?* If the honest answer is "it would be faster", use the real
thing. If it is "the real thing is awkward to set up", that awkwardness is a
finding about the library's API — fix the API rather than mocking around it.

**No standalone DB-DataAccess test files** — the DA is exercised through its
service (§13.3).

## Agnostic fixtures (non-negotiable)

Fixtures use **generic example data** — `acme/widget`, `reviewer`, `PROJ-1`,
generic env-var names. Never the host product's name, brand, CLI, or env-var
prefix anywhere in source, tests, comments, docstrings, field names, or
fixtures (AGENTS.md "this library is AGNOSTIC" → "Self-contained and fully tested").

## End-to-end flow

At minimum one `test_flow.py` driving the primary workflow A→Z through the
**real composed library** — real sqlite, real decorators, real validators. "No
I/O" means no network and no real subprocess; it does **not** mean a mocked
database. See §3 above for what a complete flow looks like, and add a
`test_user_journey.py`-style file per distinct user story the library serves.

## Rules to enforce (from AGENTS.md)

- One `unittest.TestCase` per file; filename mirrors the class (§13).
- **Tests are adversarial**: written to break the code, not to demonstrate it
  works. Mutation-check the ones that matter — break the code on purpose and
  confirm the test fails.
- **Edge cases are mandatory, not optional extras** — empty/one/many, both ends
  of every boundary, ties, nulls, over-length, wrong tenant, soft-deleted,
  duplicate calls. Work the checklist in §2.
- **Complete use-case flows end to end**, through public services, asserting
  real values at every step — not one method per test.
- Real collaborators; mock only at true infra boundaries (§13). A mocked
  database, a fake DataAccess or a stubbed decorator is rejected in review.
- **Coverage proves a function RUNS, not that anything NEEDS it.** A helper
  whose only exercise is tests written against the helper itself reads as 100%
  covered and is dead code — the tests are what make it look alive. Before
  testing a function, check it has a caller in library source:
  `grep -rn "\bname(" <lib>/ | grep -v "def name("`. Beware two false
  positives that hid a dead lookup helper for a whole review: the name inside a
  **docstring or message string** (`'... scored question(s) ...'` matched
  `question(`), and its own tests. If the only hits are tests, delete the
  function; if the property it guarded is real, re-test it **through the path
  the library actually takes** — that test is the one worth keeping.
- **Statement coverage cannot see an untaken branch.** `return None if x is
  None else ...` shows 100% while the `None` arm never runs. Probe a suspected
  dead arm by replacing it with an `assert` and running the suite; if nothing
  fails, delete the arm rather than keeping a guard for a case that cannot
  arise.
- 100% coverage of public functions; one `test_flow.py` ("Self-contained and
  fully tested").
- Generic, product-free fixtures — fully agnostic.
- Never commit `.coverage` / `.coverage.*` (delete before staging).
