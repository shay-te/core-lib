---
name: core-lib-data-access
description: MANDATORY — load this skill BEFORE you add or change a DataAccess, DAO, repository, query class, or any get_by/list/filter lookup for a *-core-lib entity; do not write it from memory. Creates pure-CRUD DataAccess on CRUDDataAccess / CRUDSoftDeleteDataAccess / CRUDSoftDeleteWithTokenDataAccess with an optional RuleValidator. Business logic and caching go in core-lib-service.
---

# Create a core-lib DataAccess (query layer)

A DataAccess is **pure CRUD** over a single entity: insert one row, fetch one
row, update one by PK, soft-delete one by PK, list by simple filters. No
business logic, no reconciliation, no cross-row decisions, no scoping — those
belong in the Service.

## ⛔ No guards. `grep -n "raise ValueError\|require(" ` must return nothing.

"No business logic" includes **every `if` that raises**. An argument guard is a
judgement about the operation, and the operation belongs to a Service. A domain
rule belongs in `validate()`. What is left for this layer is the
`RuleValidator`.

```python
# WRONG — three kinds of logic that do not belong in this layer
def create(self, assessment_id: int, data: dict = None):
    require(assessment_id=assessment_id)                      # argument guard
    payload = dict(data or {})
    payload[Thing.assessment_id.key] = assessment_id
    if not (payload.get('form_page_field_id') or payload.get('custom_field_id')):
        raise ValueError('needs one of them')                 # DOMAIN rule
    return super().create(payload)
```

There is no "right" version of that method — see below. Delete it.

| what it is | where it goes |
|---|---|
| `require(x=x)` — an argument guard | the **Service** method that owns the operation |
| a domain rule (`must name one of A or B`) | **`validate()`**, at publish time |
| "must be an int / max length / a rule no column type carries" | this file's **`RuleValidator`** |
| "may not be null / must be present" | the **column** — `nullable=False` |

## ⛔ Never override `create`. `grep -n "def create" ` must return nothing.

`CRUD.create(data: dict)` already validates through the `rule_validator` you
passed to `__init__`, then inserts. An override can only do three things, and
all three are wrong:

```python
# ⛔ REJECTED
def create(self, workspace_id: int, name: str):
    if not workspace_id:                                     # (1) business logic
        raise ValueError('create requires workspace_id')
    return super().create(create_rule_validator.validate_dict({  # (2) a 2nd validator
        Thing.workspace_id.key: workspace_id,                # (3) repacking args into
        Thing.name.key: name,                                #     the dict base takes
    }))
```

1. **Guarding arguments is business logic** — the Service's, per the section above.
2. **A second `RuleValidator` has nowhere to run.** `CRUD` takes exactly one, in
   `__init__`, and uses it on both write paths. A `create_rule_validator` can
   only fire from inside an override, so it exists purely to justify the
   override's existence.
3. **Repacking positional args into a dict buys nothing** — `create(data: dict)`
   already took a dict. It only guarantees every call site breaks when a column
   is added.

The Service passes the whole payload:

```python
thing = self._thing_da.create({
    Thing.workspace_id.key: workspace_id,
    Thing.name.key: name,
})
```

**And don't restate the schema in the allow-list.**
`ValueRuleValidator(Thing.workspace_id.key, int, nullable=False)` next to
`Column(INTEGER, nullable=False)` is one fact in two files that drift. The
database enforces presence, nullability and length itself — a null identity
column raises `IntegrityError` at flush, under sqlite as well as Postgres.
Declare only what the schema **cannot** say: a Python type a permissive DB
would coerce, or a `custom_validator` for a rule no column type carries.

**One list, two paths — and they behave differently:**

```
update(id, data)  -> validate_dict(data)                     strict:     unknown key raises
create(data)      -> validate_dict(data, strict_mode=False)  NOT strict: unknown key passes
```

So on an append-only table, an allow-list left EMPTY to mean "nothing may ever
be updated" also means **create checks nothing at all** — on the one path that
table actually uses. Write the columns into the single list. Immutability is
then a property of the service surface (no service method issues that update),
asserted by a test over the public API — never by overriding `update` to raise,
which is business logic in a DataAccess again.

**Read methods take what they are given.** Without a guard, a `None` parent
compiles to `IS NULL` and returns an empty list — never another tenant's rows.
The Service already guarded; a second check here is a copy of a decision made
one layer up, and two copies can disagree.

See "A DataAccess holds NO business logic" in `AGENTS.md`.

## Steps

1. Confirm the entity exists (use `core-lib-entity` first if not).
2. Choose a base class by the entity's delete strategy (table below).
3. Create `data_layers/data_access/<entity>_data_access.py`.
4. Add a `RuleValidator` if writes need field validation/coercion.
5. Add only thin query methods (`get_by_*`, `all`, simple filters). Anything
   smarter is a Service concern.

## Base classes

| Base | Delete | Required mixins | Use when |
|---|---|---|---|
| `CRUD` | abstract | — | custom get/delete logic |
| `CRUDDataAccess` | hard | — | plain CRUD, hard deletes |
| `CRUDSoftDeleteDataAccess` | soft | `SoftDeleteMixin` | `get()` filters `deleted_at IS NULL`; `delete()` sets it |
| `CRUDSoftDeleteWithTokenDataAccess` | soft | both mixins | same + indexed `deleted_at_token` lookup |

Constructor for all CRUD variants:
`__init__(self, db_entity, db: SqlAlchemyConnectionFactory, rule_validator: RuleValidator = None)`.

## Canonical template (copy this shape — §5)

```python
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_soft_data_access import CRUDSoftDeleteDataAccess
from core_lib.rule_validator.rule_validator import RuleValidator, ValueRuleValidator

from foo_core_lib.data_layers.data.db.entities.thing import Thing

allowed_update_types = [                       # the ONE allow-list, both paths
    ValueRuleValidator(Thing.workspace_id.key, int),
    ValueRuleValidator(
        Thing.name.key,
        str,
        custom_validator=lambda v: bool(v) and len(v) <= 255,
    ),
]
rule_validator = RuleValidator(allowed_update_types)


class ThingDataAccess(CRUDSoftDeleteDataAccess):

    def __init__(self, db: SqlAlchemyConnectionFactory):
        CRUD.__init__(self, Thing, db, rule_validator)      # CRUD.__init__, not the subclass
```

That is the whole class — no `create`, no guards, domain queries only.

## Rules to enforce (from AGENTS.md)

- **Extends `DataAccess`** — every class in this folder, including shared bases
  and mixins. A shared reader written as a bare `object` is the only thing in
  `data_access/` not declaring what layer it is in. Put it ALONGSIDE the CRUD
  base rather than replacing it when its users need different CRUD behaviour;
  the MRO linearises with the marker last.

- **MUST subclass a core-lib CRUD base.** Hand-rolled `session.add()` /
  `session.flush()` / bespoke get/update/delete loops are **rejected in
  review** — the base already does the writable-field introspection (§5).
- **`CRUD.__init__(self, Entity, db, rule_validator)`** in `__init__` — not the
  subclass's `__init__` (§5).
- **`rule_validator` is module-level, next to the class** — ONE of them, built
  from an `allowed_update_types` list, one `ValueRuleValidator(Entity.col.key,
  type, custom_validator=...)` per column (§5).
- **Never override `create`** (§5.1). `CRUD.create(data: dict)` plus that
  validator is the write API; the Service passes the whole payload. No second
  `create_rule_validator`, and no allow-list entry restating a column's type or
  `nullable=False`. **`update` overrides strip immutable columns** before
  `super().update(id, data)` (§5).
- **Never returns soft-deleted rows**; don't add `include_deleted` (§5).
- **Column references are `Entity.col.key` / `Entity.col`** — never string
  literals (§5), and that holds in EVERY position, not just a query: a set,
  tuple, module constant, comparison or argument. In a filter set a stale
  literal fails *silently* — the name stops matching and the column stops
  being excluded (§4.3).
- **Errors:** your own arg guards raise `ValueError`; the base's guards are
  bare `assert` (→ `AssertionError`); a missing row on `get` is
  `StatusCodeException(404)` (§5).
- **Cross-entity guards** live in module-level helpers inside the DA file (§5).
- **A DB DataAccess is only ever called BY a Service** — never from a host app,
  a test, or another lib (§5).

Expose this DataAccess only through a Service — never as a public attribute of
the main CoreLib class. Build the Service next with `core-lib-service`.
