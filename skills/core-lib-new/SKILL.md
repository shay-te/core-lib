---
name: core-lib-new
description: MANDATORY — load this skill BEFORE you create, bootstrap, or start a whole new *-core-lib library or persistence/integration package from nothing; do not scaffold from memory. Produces the package layout, the main CoreLib composition-root class, singleton accessor, Hydra config plus hydra_plugins, requirements.txt, and a first entity→data-access→service slice. To add one part to an existing lib, use the per-part skill.
---

# Create a new *-core-lib (end to end)

**Read [`BUILDING_A_CORE_LIB.md`](../../BUILDING_A_CORE_LIB.md) first** — the
full architecture guide (mental model, anatomy, ordered build sequence §9,
decision guide §10, recurring-mistake list §11, Definition of Done §12). This
skill is the mechanical scaffold; that guide is the plan.

This skill orchestrates the others to stand up a complete, agnostic core-lib.
Use the per-part skills for each layer: `core-lib-entity`,
`core-lib-data-access`, `core-lib-service`, `core-lib-connection`,
`core-lib-migration`, `core-lib-tests`.

## Package layout

```
<name>-core-lib/                         # git repo
├── <name>_core_lib/                     # main package (underscored)
│   ├── config/<name>_core_lib.yaml      # Hydra config
│   ├── data_layers/
│   │   ├── data/db/entities/            # SQLAlchemy models (core-lib-entity)
│   │   ├── data/db/migrations/versions/ # Alembic (core-lib-migration)
│   │   ├── data_access/                 # query classes (core-lib-data-access)
│   │   └── service/                     # business logic (core-lib-service)
│   ├── connections/                     # outbound clients (core-lib-connection, optional)
│   ├── error_handling/                  # typed errors
│   └── <name>_core_lib.py               # main class (composition root)
├── hydra_plugins/<name>_core_lib/       # advertises this lib's config to parents
├── tests/
├── setup.py / pyproject.toml
└── requirements.txt                     # just core-lib (+ extras_require for optional SDKs)
```

## Steps

1. **Scaffold the tree** above. `__init__.py` files stay **empty** package
   markers (the package-root may hold only `__version__`) — no re-export
   aggregators.
2. **First vertical slice**: entity → data-access → service (run those three
   skills in order).
3. **Main class** (composition root) — see template.
4. **Singleton accessor** — see template.
5. **Hydra config + plugin** so parent apps can override sections.
6. **Migration** for the first entity (`core-lib-migration`).
7. **Tests** (`core-lib-tests`) — real collaborators, agnostic fixtures.

## Main class template

```python
from omegaconf import DictConfig

from core_lib.core_lib import CoreLib
from core_lib.helpers.config_instances import instantiate_config
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.cache.cache_handler_ram import CacheHandlerRam

from my_core_lib.data_layers.data_access.widget_data_access import WidgetDataAccess
from my_core_lib.data_layers.service.widget_service import WidgetService


class MyCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        CoreLib.__init__(self)                 # FIRST — wires event listeners
        self.config = config
        db = instantiate_config(self.config.core_lib.data.db, SqlAlchemyConnectionFactory)

        # register a default RAM cache ONLY if the host hasn't registered one
        if not CoreLib.cache_registry.registered():
            CoreLib.cache_registry.register('my_core_lib', CacheHandlerRam())

        # public attributes ARE the API surface — expose services, never DataAccess
        self.widgets = WidgetService(WidgetDataAccess(db))
```

## Singleton accessor template

```python
class MyCoreLibInstance:
    _app = None

    @staticmethod
    def init(config):
        if MyCoreLibInstance._app is None:
            MyCoreLibInstance._app = MyCoreLib(config)

    @staticmethod
    def get() -> MyCoreLib:
        return MyCoreLibInstance._app
```

## Composition-root rules (from AGENTS.md)

- Call `CoreLib.__init__(self)` **first**.
- **Public attributes are the API surface** — expose Services only; never a
  DataAccess (that would leak cache misses and raw ORM rows past the boundary)
  (§4 intro).
- Register the default cache handler **only when the registry is empty**, so a
  host can pre-register redis/memcached (§4.5).
- **Agnostic**: no host/product name anywhere; read generic config keys / take
  values via constructor params; inject product-specific text with safe
  neutral defaults (AGENTS.md "this library is AGNOSTIC").
- **Minimal deps**: `requirements.txt` is just `core-lib`; optional/heavy SDKs
  go in `extras_require` (§5.4).
- **No empty re-export-only modules**; import from the defining submodule
  (§2.1).

## The litmus test

Could you publish this package as-is, with its tests, to a public registry and
have a stranger use it without ever learning what application it came from? If
not, it isn't agnostic yet.
