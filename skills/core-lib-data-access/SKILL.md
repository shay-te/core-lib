---
name: core-lib-data-access
description: MANDATORY — load this skill BEFORE you add or change a DataAccess, DAO, repository, query class, or any get_by/list/filter lookup for a *-core-lib entity; do not write it from memory. Creates pure-CRUD DataAccess on CRUDDataAccess / CRUDSoftDeleteDataAccess / CRUDSoftDeleteWithTokenDataAccess with an optional RuleValidator. Business logic and caching go in core-lib-service.
---

# Create a core-lib DataAccess (query layer)

A DataAccess is **pure CRUD** over a single entity: insert one row, fetch one
row, update one by PK, soft-delete one by PK, list by simple filters. No
business logic, no reconciliation, no cross-row decisions, no scoping — those
belong in the Service.

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

allowed_update_types = [                       # the UPDATE allow-list
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

    def create(self, workspace_id: int, name: str) -> Thing:
        if not (workspace_id and name):                     # guard -> ValueError
            raise ValueError('create requires workspace_id and name')
        return super().create({                             # identity cols as explicit args
            Thing.workspace_id.key: workspace_id,
            Thing.name.key: name,
        })
```

## Rules to enforce (from AGENTS.md)

- **MUST subclass a core-lib CRUD base.** Hand-rolled `session.add()` /
  `session.flush()` / bespoke get/update/delete loops are **rejected in
  review** — the base already does the writable-field introspection (§5).
- **`CRUD.__init__(self, Entity, db, rule_validator)`** in `__init__` — not the
  subclass's `__init__` (§5).
- **`rule_validator` is module-level, next to the class**, built from an
  `allowed_update_types` list — one `ValueRuleValidator(Entity.col.key, type,
  custom_validator=...)` per updatable column (§5).
- **`create` takes explicit args for the identity columns** (they're immutable,
  so they never ride an update payload), guards them, then calls
  `super().create({Entity.col.key: value})`. **`update` overrides strip
  immutable columns** before `super().update(id, data)` (§5).
- **Never returns soft-deleted rows**; don't add `include_deleted` (§5).
- **Column references are `Entity.col.key` / `Entity.col`** — never string
  literals (§5).
- **Errors:** your own arg guards raise `ValueError`; the base's guards are
  bare `assert` (→ `AssertionError`); a missing row on `get` is
  `StatusCodeException(404)` (§5).
- **Cross-entity guards** live in module-level helpers inside the DA file (§5).
- **A DB DataAccess is only ever called BY a Service** — never from a host app,
  a test, or another lib (§5).

Expose this DataAccess only through a Service — never as a public attribute of
the main CoreLib class. Build the Service next with `core-lib-service`.
