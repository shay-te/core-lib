---
name: core-lib-new
description: MANDATORY — load this skill BEFORE you create, bootstrap, or start a whole new *-core-lib library or persistence/integration package from nothing; do not scaffold from memory. Produces the package layout, the main CoreLib composition-root class, singleton accessor, Hydra config plus hydra_plugins, requirements.txt, and a first entity→data-access→service slice. To add one part to an existing lib, use the per-part skill.
---

# Create a new *-core-lib (end to end)

**Read the canonical recipe in [`AGENTS.md`](../../AGENTS.md) first** — §0–§17
(never invent, naming, folder tree, config, entities, DataAccess, services,
composition root, observers, jobs, migrations, framework contracts, tests,
packaging, build order §15, things to avoid §16, final checklist §17). That
recipe is the plan and is authoritative; this skill is the mechanical scaffold.
Where they differ, the recipe wins.

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

1. **Scaffold the tree** above. The package-root `foo_core_lib/__init__.py`
   carries `__version__` **and** re-exports the class
   (`from foo_core_lib.foo_core_lib import FooCoreLib` + `__all__`). **Every
   other `__init__.py` is an empty 0-byte file — but it must exist** (§1, §2).
2. **First vertical slice**: entity → data-access → service (run those three
   skills in order).
3. **Main class** (composition root) — see template.
4. **Singleton accessor** — see template.
5. **Hydra config + plugin** so parent apps can override sections.
6. **Migration** for the first entity (`core-lib-migration`).
7. **Tests** (`core-lib-tests`) — real collaborators, agnostic fixtures.

## Composition root template (copy §7 exactly)

```python
import inspect
import os

from omegaconf import DictConfig

from core_lib.alembic.alembic import Alembic
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.core_lib import CoreLib

from foo_core_lib.constants import FOO_CORE_LIB_CACHE
from foo_core_lib.data_layers.data_access.thing_data_access import ThingDataAccess
from foo_core_lib.data_layers.service.thing_service import ThingService


class FooCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf

        if not CoreLib.cache_registry.get(FOO_CORE_LIB_CACHE):      # ALWAYS guarded
            CoreLib.cache_registry.register(FOO_CORE_LIB_CACHE, CacheHandlerRam())

        core_cfg = conf.core_lib
        db = CoreLib.connection_factory_registry.get_or_reg(core_cfg.data.sqlalchemy)

        self._thing_da = ThingDataAccess(db)
        self.thing = ThingService(self._thing_da)                   # public, SINGULAR

    @staticmethod
    def install(cfg: DictConfig):
        Alembic(os.path.dirname(inspect.getfile(FooCoreLib)), cfg).upgrade()

    @staticmethod
    def uninstall(cfg: DictConfig):
        Alembic(os.path.dirname(inspect.getfile(FooCoreLib)), cfg).downgrade()
```

## Composition-root rules (from AGENTS.md)

- Call `super().__init__()` **first**.
- **Public attributes are the API surface** — expose Services only; never a
  DataAccess (that would leak cache misses and raw ORM rows past the boundary)
  (§7).
- **Guard every registry registration on its own key** —
  `if not CoreLib.cache_registry.get(FOO_CORE_LIB_CACHE):` — registries are
  process-global and `register()` RAISES on a duplicate key (§7, §12).
- **DB comes from `CoreLib.connection_factory_registry.get_or_reg(core_cfg.data.sqlalchemy)`**,
  not a hand-built factory (§7).
- **Ship `install()` / `uninstall()` staticmethods** using
  `Alembic(os.path.dirname(inspect.getfile(FooCoreLib)), cfg)` — note the import
  is `from core_lib.alembic.alembic import Alembic` (§7, §11.1).
- **Agnostic**: no host/product name anywhere; read generic config keys / take
  values via constructor params; inject product-specific text with safe
  neutral defaults (AGENTS.md "this library is AGNOSTIC").
- **Minimal deps**: `requirements.txt` is just `core-lib`; optional/heavy SDKs
  go in `extras_require` (§14).
- **No empty re-export-only modules**; import from the defining submodule
  (§1).

## The agnosticism litmus test

Could you publish this package as-is, with its tests, to a public registry and
have a stranger use it without ever learning what application it came from? If
not, it isn't agnostic yet.
