---
name: core-lib-data-access
description: Scaffold a DataAccess class (the query layer) for a *-core-lib entity — pure CRUD over one entity, built on CRUDDataAccess / CRUDSoftDeleteDataAccess / CRUDSoftDeleteWithTokenDataAccess, with optional RuleValidator. Use when asked to add a data-access, DAO, repository, or query class for a core-lib entity, or to add a get_by_*/list query.
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

## Canonical template (CRUD base + rule validator)

```python
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.data_layers.data_access.db.crud.crud_soft_data_access import CRUDSoftDeleteDataAccess
from core_lib.rule_validator.rule_validator import RuleValidator, ValueRuleValidator

from my_core_lib.data_layers.data.db.entities.widget import Widget

widget_rule_validator = RuleValidator([
    ValueRuleValidator(Widget.name.key, str, nullable=False),
    # enum field typed as the ENUM class, not int, so the DA boundary
    # rejects raw ints even if a caller bypasses the service:
    ValueRuleValidator(Widget.status.key, Widget.Status, nullable=False),
])


class WidgetDataAccess(CRUDSoftDeleteDataAccess):
    def __init__(self, db: SqlAlchemyConnectionFactory):
        CRUDSoftDeleteDataAccess.__init__(self, Widget, db, widget_rule_validator)

    def get_by_name(self, name: str):
        if not name:
            raise ValueError('name is required')
        with self._db.get() as session:
            return (
                session.query(Widget)
                .filter(Widget.name == name, Widget.deleted_at == None)
                .first()
            )
```

If you write a custom `create`/`update` that accepts a `data: dict`, use the
entity-introspection loop (CRUD base already does this):

```python
entity = Widget()
for key, value in data.items():
    if key == 'id' or not hasattr(entity, key):
        continue
    if isinstance(value, Enum):
        value = value.value
    setattr(entity, key, value)
```

## Rules to enforce (from AGENTS.md)

- **Pure CRUD only** — no `if exists update else insert`, no "restore"
  branches, no cross-row look-ups, no project/tenant scoping (§3.1).
- **Never returns soft-deleted rows** — every read filters
  `deleted_at == None`; do not add `include_deleted` (§3.2).
- **Writes use entity introspection, not whitelist constants** — no
  `_CREATABLE_FIELDS`/`_MUTABLE_FIELDS` sets (§3.3).
- **Column names come from the entity** — `Widget.name.key`, never `'name'`
  (§3.4).
- **Validate with `raise`, not `assert`** (§1.5).
- **Rule-validator field types use the enum class, not `int`** (§4.2).
- Meaningful names, fetch→validate→use, no single-letter loop vars
  (§§1.1–1.3).

Expose this DataAccess only through a Service — never as a public attribute of
the main CoreLib class. Build the Service next with `core-lib-service`.
