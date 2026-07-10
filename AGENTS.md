# AGENTS Notes

## Repo-specific context

- `core_lib/helpers/shell_utils.py` currently exposes `prompt_*` helpers, not `input_*` helpers and not `prompt__*` helpers.
- The active public prompt helpers are:
  - `prompt_string`
  - `prompt_str`
  - `prompt_file_name`
  - `prompt_yes_no`
  - `prompt_bool`
  - `prompt_int`
  - `prompt_email`
  - `prompt_url`
  - `prompt_timeframe`
  - `prompt_enum`
  - `prompt_options`
  - `prompt_list`
  - `prompt_comma_list`

## Recent migration we completed

- Generator modules previously imported old `input_*` names from `core_lib.helpers.shell_utils`.
- Those imports and usages were updated to the new `prompt_*` names across:
  - `core_lib_generator/config_collectors/`
  - `core_lib_generator/core_lib_config_generate_yaml.py`
  - `core_lib_generator/generator_utils/helpers.py`
- A repo-wide scan confirmed there are no remaining `input_*` imports or `shell_utils` prompt call sites left to migrate.
- The only remaining text like `input_list` is a local variable name in tests, not an import from `shell_utils`.

## SonarCloud follow-up

- SonarCloud reported:
  - `prompt_str` had cognitive complexity 17 and needed to be reduced to 15 or less.
  - Nested conditional-expression warnings existed around `prompt_url`, `prompt_timeframe`, `prompt_enum`, and `prompt_list`.
- We addressed this by introducing small private helpers in `core_lib/helpers/shell_utils.py`:
  - `_empty_prompt_result`
  - `_coalesce_prompt_value`
- These helpers keep behavior the same while reducing branching and removing nested conditional expressions.

## Exact SonarCloud items from PR 164

- File: `core_lib/helpers/shell_utils.py`
- Function: `prompt_str`
  - Sonar comment: `Refactor this function to reduce its Cognitive Complexity from 17 to the 15 allowed.`
  - Link: `https://sonarcloud.io/project/issues?id=shay-te_core-lib&issues=AZ15FO8tgeiY87x_QG2T&open=AZ15FO8tgeiY87x_QG2T&pullRequest=164`
- Function: `prompt_url`
  - Original reported line: `148`
  - Sonar comment: `Extract this nested conditional expression into an independent statement.`
  - Link: `https://sonarcloud.io/project/issues?id=shay-te_core-lib&issues=AZ15FO8tgeiY87x_QG2U&open=AZ15FO8tgeiY87x_QG2U&pullRequest=164`
- Function: `prompt_timeframe`
  - Original reported line: `159`
  - Sonar comment: `Extract this nested conditional expression into an independent statement.`
  - Link: `https://sonarcloud.io/project/issues?id=shay-te_core-lib&issues=AZ15FO8tgeiY87x_QG2V&open=AZ15FO8tgeiY87x_QG2V&pullRequest=164`
- Function: `prompt_enum`
  - Original reported line: `178`
  - Sonar comment: `Extract this nested conditional expression into an independent statement.`
  - Link: `https://sonarcloud.io/project/issues?id=shay-te_core-lib&issues=AZ15FO8tgeiY87x_QG2W&open=AZ15FO8tgeiY87x_QG2W&pullRequest=164`
- File location around original line: `207`
  - Sonar link: `https://sonarcloud.io/project/issues?id=shay-te_core-lib&issues=AZ15FO8tgeiY87x_QG2X&open=AZ15FO8tgeiY87x_QG2X&pullRequest=164`
  - Note: the pasted report did not include the textual message for this one, only the issue link and `/ SonarCloud Code Analysis`.
- Function: `prompt_list`
  - Original reported line: `221`
  - Sonar comment: `Extract this nested conditional expression into an independent statement.`
  - Link: `https://sonarcloud.io/project/issues?id=shay-te_core-lib&issues=AZ15FO8tgeiY87x_QG2Y&open=AZ15FO8tgeiY87x_QG2Y&pullRequest=164`

## Mapping of the fix to those Sonar items

- `prompt_str` was simplified by delegating empty/default/none handling to `_empty_prompt_result`.
- The nested conditional expressions reported for `prompt_url`, `prompt_timeframe`, `prompt_enum`, and `prompt_list` were replaced with `_coalesce_prompt_value(...)`.
- Current line numbers in `shell_utils.py` have shifted after the refactor, so the Sonar-reported line numbers above refer to the older pre-fix version from PR 164.

## Verification we ran

- `python -m pytest tests/test_command_line.py`
- Import smoke test for the updated generator modules:
  - `python -c "import core_lib_generator.config_collectors.setup_collector, core_lib_generator.config_collectors.data_access, core_lib_generator.config_collectors.cache, core_lib_generator.config_collectors.database, core_lib_generator.config_collectors.job, core_lib_generator.config_collectors.solr, core_lib_generator.config_collectors.db_entity, core_lib_generator.config_collectors.service, core_lib_generator.core_lib_config_generate_yaml, core_lib_generator.generator_utils.helpers"`

## Practical guidance for future edits

- If prompt-related code changes again, treat `core_lib/helpers/shell_utils.py` as the source of truth for exported names.
- Before mass-renaming prompt helpers, scan the repo with `rg` for both imports and call sites.
- Keep prompt helpers simple because this repo is checked by SonarCloud and small readability warnings can block PRs.
- **Read config directly; never defend it.** Access required config straight off the `DictConfig` by attribute — `conf.core_lib.<section>.<key>` (e.g. `conf.core_lib.extraction.ocr_languages`, `conf.core_lib.extraction.confidence_threshold`). Do NOT wrap config reads in `.get(section, {})`, `or {}`, `try/except`, or a default value. Missing/malformed config must fail loud at construction — a silent fallback to a default hides the misconfiguration and is strictly worse than crashing. The only thing allowed to wrap a config read is a pure type coercion of the read value (`float(...)`, `tuple(...)`) because env-sourced values arrive as strings / OmegaConf nodes — that is not a fallback. Tests construct the lib with a real `OmegaConf.create({...})` and assert that an absent key raises `omegaconf.errors.OmegaConfBaseException`, not that it defaults.
- **Never commit `coverage.py` artifacts.** The `.coverage` SQLite file (and any `.coverage.*` parallel-run shards) is a local run artifact — it must never be tracked. Every repo's `.gitignore` lists both `.coverage` and `.coverage.*`; if you run `coverage run`, delete the resulting `.coverage` before staging and confirm `git ls-files | grep '^\.coverage$'` is empty. The `.coveragerc` config file IS tracked — only the data file is ignored.

---

# Building a new `*-core-lib` from scratch (canonical recipe)

This is how EVERY new core-lib in this workspace is built. It is distilled from the real libs — `task-core-lib`, `workflow-core-lib`, `custom-field-core-lib`, `email-core-lib`, `library-core-lib`, `doc-to-markdown-core-lib` — plus every correction the owner made while `library-core-lib` was being brought up to standard. Follow it exactly. Every "small thing" here cost real debugging time or a review rejection.

A core-lib is a composition root (`<Name>CoreLib(CoreLib)`) that wires **Services** over **DataAccess** over **entities**. Host apps touch ONLY the services exposed on the CoreLib. Dependencies point one way:

```
entities  ←  data_access  ←  service  ←  <Name>CoreLib  ←  host app / tests
```

Nothing to the right of an arrow is ever imported/called by anything to its left, and nothing skips a layer: a host or a test never calls a DataAccess; a DataAccess never calls a Service.

## 0. The meta-rule: never invent

**Before writing ANY line — file layout, decorator, helper, test idiom, naming — ask: "is this exactly how the existing core-libs do it?" If none of them does it, do NOT do it**, even if the new way seems better. The existing patterns are chosen for readability and debuggability: someone reading a failing test or a stack trace must recognize the shape instantly. Concrete inventions that were rejected in review, so you don't repeat them:

- `@property` accessors in tests that alias `self.lib.collection` as `self.service` / `self.collection_da` — rejected: "not easy to read and understand if something fails". Access is always inline and fully spelled: `self.library_core_lib.collection.create(...)`.
- Naming the CoreLib handle `cls.lib` — rejected. It is the full lib name: `cls.library_core_lib`, `cls.task_core_lib`.
- Plural public service attributes (`self.documents`) — rejected. Singular, always (§1).
- A bespoke test harness that wires DataAccess + Services directly (a `library_harness.py`) — rejected: "everything comes from the core lib, this is final" (§13).
- Hand-rolled `session.add()`/`session.flush()` CRUD inside a DataAccess — rejected; CRUD bases only (§5).
- Vague variable names for composed parts — `storage = StorageDataAccess(...)` was rejected; it is `storage_data_access = StorageDataAccess(StorageConnectionFactory(storage_cfg))`. Name a variable what the thing IS.
- Defensive config reads (`storage_cfg.get('prefix_originals')`) — rejected; direct attribute access, fail loud, and make sure the key ALWAYS exists in the yaml (§3).
- Standalone DataAccess test files — rejected: "no one is exposing the DA; we only test what we expose, which is the service" (§13).

When two existing libs disagree, this document names the canonical choice and marks the other as a divergence NOT to copy (there is a list in §16).

## 1. Naming (exact — no variation)

- Repo `foo-core-lib` → python package `foo_core_lib` → main class `FooCoreLib` in `foo_core_lib/foo_core_lib.py`.
- `foo_core_lib/__init__.py` re-exports the class: `from foo_core_lib.foo_core_lib import FooCoreLib`. Every other `__init__.py` in the package tree is an EMPTY file (0 bytes) — but it must exist (`config/`, `data_layers/`, each subpackage, `migrations/`, `migrations/versions/`, `hydra_plugins/foo_core_lib/`, `tests/`, `tests/helpers/`, `tests/data/`).
- Constants in `foo_core_lib/constants.py`: the cache handler key `FOO_CORE_LIB_CACHE = 'foo_core_lib'` and (if the lib fires events) the observer key `FOO_CORE_LIB_NAME = 'FOO_CORE_LIB'`.
- Per domain object `Thing`: entity `Thing` in `data_layers/data/db/entities/thing.py` (`__tablename__ = 'thing'` — singular); DataAccess `ThingDataAccess` in `data_layers/data_access/thing_data_access.py`; service `ThingService` in `data_layers/service/thing_service.py`. One class per file.
- **The public CoreLib attribute is the service class name minus `Service`, snake_case, SINGULAR:** `WorkspaceService → self.workspace`, `DocumentService → self.document`, `DocumentCollaboratorService → self.document_collaborator`. NEVER plural (`self.documents` is wrong and was explicitly rejected).
- The DataAccess instance is private: `self._thing_da` on the CoreLib (or a local variable in `__init__` if nothing else needs it — task/workflow do that) and `self._thing_da` on the service that owns it. It is NEVER a public attribute.
- Cache key templates are `'<lib>_<entity>_{param}'`: `'library_document_{project_id}_{document_id}'`, `'library_workspace_{workspace_id}'`. Named module-level constants next to the service: `CACHE_KEY_DOCUMENT = 'library_document_{project_id}_{document_id}'`.
- Index/constraint name constants on the entity: `INDEX_WORKSPACE_ID = 'ix_thing_workspace_id'` (`ix_<table>_<column>`; composite: `ix_<table>_<col1>_<col2>` or a meaningful pair name like `ix_document_workspace_collection`).
- Searchpath plugin: file `hydra_plugins/foo_core_lib/foo_core_lib_searchpath.py`, class `FooCoreLibSearchPathPlugin`. (email's file is misnamed `*_sourcepath.py` — a typo; do not copy it.)
- Module-level tuning constants are SCREAMING_SNAKE at the top of the service module (`EMPTY_TRASH_BATCH = 10_000`, `VIEW_URL_EXPIRES_SECONDS = 900`), each with a comment saying why the value is what it is.

## 2. Folder tree (complete)

```
foo-core-lib/
  foo_core_lib/
    __init__.py                       # from foo_core_lib.foo_core_lib import FooCoreLib
    foo_core_lib.py                   # composition root
    constants.py                      # FOO_CORE_LIB_CACHE (+ FOO_CORE_LIB_NAME if events)
    config/
      __init__.py                     # REQUIRED, empty — pkg://foo_core_lib.config won't resolve without it
      foo_core_lib.yaml               # '# @package _global_', fully env-var driven
    connections/                      # ONLY if the lib owns a non-DB backend (S3 etc.)
      __init__.py
      foo_connection_factory.py       # validates config, builds the client (lazy import)
      foo_connection.py               # thin context-manager handle
    data_layers/
      __init__.py
      data/
        __init__.py
        db/
          __init__.py
          entities/
            __init__.py
            thing.py                  # one entity (+ its enum) per file
          migrations/
            __init__.py
            env.py                    # stock alembic boilerplate — copy from a sibling lib verbatim
            script.py.mako            # copy from a sibling lib verbatim
            .migration_ver            # latest revision number, e.g. "1" — keep in sync
            versions/
              __init__.py
              2026-06-21_1_create_db.py
      data_access/
        __init__.py
        thing_data_access.py
        foo_storage_data_access.py    # backend verbs, if the lib has a backend
      service/
        __init__.py
        thing_service.py
    observer/                         # ONLY if the lib fires events (task/workflow shape)
      __init__.py
      foo_listener.py                 # FooListener(ABC) — host implements this
      foo_observer_listener.py        # FooObserverListener(ObserverListener) + EVENT_* keys
    jobs/                             # ONLY if the lib schedules background jobs
      __init__.py
      foo_job.py                      # class FooJob(Job)
  hydra_plugins/
    foo_core_lib/
      __init__.py                     # empty
      foo_core_lib_searchpath.py      # FooCoreLibSearchPathPlugin
  tests/
    __init__.py
    helpers/
      __init__.py
      utils.py                        # sync_create_start_core_lib, load_config, new_project_id, seams
    data/
      .env                            # test env vars (DB sqlite :memory:, backend 127.0.0.1, MEMCACHED_HOST)
      config/
        config.yaml                   # defaults: [core_lib, foo_core_lib, (foo_core_lib_test | _self_)]
        foo_core_lib_test.yaml        # test-safe overrides, if the packaged yaml is not fully env-driven
      entities/                       # test-only stand-in entities (task's TestUser), if needed
    stub_<backend>.py                 # deterministic double for an uncontrollable backend, if needed
    test_thing_service.py             # ONE TestCase class per file
    test_foo_core_lib.py              # composed-lib smoke test (public surface only)
  core_lib_config.yaml                # repo-root compose for install/CLI entrypoints
  requirements.txt                    # RUNTIME deps only
  .coveragerc                         # source = foo_core_lib; omit migrations/*
  .gitignore                          # includes .coverage and .coverage.*
  docker-compose-dev.yaml             # ONLY if the lib needs local infra (MinIO etc.)
```

## 3. Config (Hydra) — the packaged yaml, the search path, the compose

### 3.1 `foo_core_lib/config/foo_core_lib.yaml`

- First line is exactly `# @package _global_`. Root key is `core_lib:`.
- **Every value is sourced from an environment variable** with an in-yaml default: `${oc.env:FOO_<KEY>,<default>}`. Nullable values default to `null`: `${oc.env:FOO_ENDPOINT_URL,null}`.
- **Booleans and numbers MUST be wrapped in `oc.decode`:** `${oc.decode:${oc.env:FOO_USE_SSL,true}}`. A bare `${oc.env:...}` resolves to a STRING — `'false'` is truthy — which silently breaks `create_engine(echo=…)`, makes `create_db` impossible to disable, and defeats `use_ssl is False` checks. This was a real shipped bug.
- **The DB block lives at `core_lib.data.sqlalchemy` — not anywhere else** — because two framework pieces hard-code that path: `CoreLib.connection_factory_registry.get_or_reg(cfg.core_lib.data.sqlalchemy)` and `Alembic.__init__`, which builds the migration URL from `core_lib.data.sqlalchemy.config.url`. Shape (task/workflow/custom-field all match):

```yaml
# @package _global_
core_lib:
  data:
    sqlalchemy:
      _instance_key_: sqlalchemy_connection
      _target_: core_lib.connection.sql_alchemy_connection_factory.SqlAlchemyConnectionFactory
      config:
        log_queries: ${oc.decode:${oc.env:FOO_DB_LOG_QUERIES,false}}
        create_db: ${oc.decode:${oc.env:FOO_DB_CREATE_DB,false}}
        session:
          pool_recycle: 3600
          pool_pre_ping: false
          pool_size: 5
          max_overflow: 10
        url:
          protocol: ${oc.env:FOO_DB_PROTOCOL,postgresql}
          username: ${oc.env:POSTGRES_USER,null}
          password: ${oc.env:POSTGRES_PASSWORD,null}
          host: ${oc.env:POSTGRES_HOST,null}
          port: ${oc.decode:${oc.env:POSTGRES_PORT,5432}}
          file: ${oc.env:FOO_DB_FILE,null}
  alembic:
    version_table: foo_alembic_version
```

  (`library-core-lib` currently keeps its DB block at `core_lib.data.db` and constructs the factory directly — that divergence breaks its `install()` because Alembic can't find the URL. Do NOT copy it; `data.sqlalchemy` is the contract.)
- `version_table` is ALWAYS overridden per lib: `task_alembic_version`, `workflow_alembic_version`, `custom_field_alembic_version` → yours is `foo_alembic_version`. Without it every lib would fight over the shared `alembic_version` table in a shared database.
- Backend/domain sections follow the same env pattern (see library's storage block: `provider`, `region`, `bucket`, `endpoint_url`, `access_key`, `secret_key`, `use_ssl` (decoded), `addressing_style`, `prefix_originals`, `prefix_markdown`). If code reads a key, the key EXISTS in this yaml — code never `.get()`s around a missing key.
- Limits/tuning live under a named section (`core_lib.limits.max_upload_bytes`) — sourced from env like everything else.

### 3.2 Search path plugin + `__init__.py`

```python
# hydra_plugins/foo_core_lib/foo_core_lib_searchpath.py
from hydra.plugins.search_path_plugin import SearchPathPlugin
from hydra.core.config_search_path import ConfigSearchPath


class FooCoreLibSearchPathPlugin(SearchPathPlugin):
    def manipulate_search_path(self, search_path: ConfigSearchPath) -> None:
        assert isinstance(search_path, ConfigSearchPath)
        search_path.append("foo_core_lib", "pkg://foo_core_lib.config")
```

- `foo_core_lib/config/__init__.py` MUST exist (empty). Without it `pkg://foo_core_lib.config` is not an importable package in some environments and every compose that lists `- foo_core_lib` dies with `MissingConfigException: Could not load 'foo_core_lib'`. All four reference libs ship it; library and doc-to-markdown were missing it and it cost a debugging session.
- `hydra_plugins/foo_core_lib/__init__.py` is also an empty required file.

### 3.3 Repo-root `core_lib_config.yaml` (install/CLI compose)

```yaml
defaults:
  - _self_
  - core_lib
  - foo_core_lib

core_lib_module: foo_core_lib

hydra:
  run:
    dir: .
```

Optionally ship an install entrypoint like workflow's `app_workflow_core_lib_install.py`:

```python
@hydra.main(config_name='core_lib_config', version_base='1.1')
def main(cfg):
    FooCoreLib.install(cfg)
```

### 3.4 Composition rules that bite

- **NEVER compose another repo's config group in your defaults list** (`- other_core_lib`). Resolving `pkg://other_core_lib.config` from a sibling repo fails in some environments with `Could not load 'other_core_lib'`. If your lib composes another CoreLib and needs a section of its config (library needs doc-to-markdown's `core_lib.extraction`), provide that section INLINE in your own yaml (and in the test `config.yaml` under `_self_`).
- When a compose file mixes a `defaults:` list with inline keys, the defaults list must contain `_self_` (otherwise hydra warns and the merge order is unspecified).
- The base `core_lib` config group requires `MEMCACHED_HOST` to resolve (`core_lib.cache.memcached.url.host` is `${oc.env:MEMCACHED_HOST}` with NO default). Any environment that composes `- core_lib` must export it — test `.env` files set `MEMCACHED_HOST=localhost` even though nothing uses memcached.

## 4. Entities (`data_layers/data/db/entities/thing.py`)

```python
import enum

from sqlalchemy import Column, VARCHAR, INTEGER, ForeignKey, JSON, Index, UniqueConstraint

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin
from core_lib.data_layers.data.db.sqlalchemy.types.int_enum import IntEnum


class ThingKind(enum.Enum):
    ALPHA = 1        # IntEnum values MUST start at 1 — never 0 (see §12)
    BETA = 2


class Thing(Base, SoftDeleteMixin):

    __tablename__ = 'thing'

    INDEX_WORKSPACE_ID = 'ix_thing_workspace_id'
    INDEX_WORKSPACE_NAME = 'ix_thing_workspace_name'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    workspace_id = Column(INTEGER, ForeignKey('workspace.id'), nullable=False)
    name = Column(VARCHAR(length=255), nullable=False)
    kind = Column(IntEnum(ThingKind), nullable=False)
    position = Column(INTEGER, nullable=False, default=0, server_default='0')

    __table_args__ = (
        Index(INDEX_WORKSPACE_ID, 'workspace_id', unique=False),
        Index(INDEX_WORKSPACE_NAME, 'workspace_id', 'name', unique=False),
    )
```

Rules, each load-bearing:

- **Mixin choice decides the DataAccess base** (§5). `SoftDeleteMixin` gives `created_at`/`updated_at`/`deleted_at` (all Python-side `default=`, no `server_default`, forced to the end of the table via `_creation_order`). `SoftDeleteTokenMixin` adds ONLY `deleted_at_token` (Integer, default 0) — **an entity used with `CRUDSoftDeleteWithTokenDataAccess` needs BOTH mixins** (`class X(Base, SoftDeleteMixin, SoftDeleteTokenMixin)`), because the token delete stamps both `deleted_at` and `deleted_at_token`.
- **Use the token mixin whenever the table carries a UNIQUE constraint over business columns.** The live-row marker is `deleted_at_token == 0`, so the unique constraint is declared over `(business_cols..., deleted_at_token)` — a soft-deleted row (token = deletion epoch) no longer collides with a re-created live row. Example: `UniqueConstraint(document_id.key, user_id.key, deleted_at_token.key, name=INDEX_DOCUMENT_USER)` on `document_collaborator`.
- **Every index and unique constraint gets a class-constant name** referenced from `__table_args__` AND from the migration — the name exists in exactly one place.
- **Any column with a `server_default` MUST also carry the matching Python `default=`** (`default=0, server_default='0'`). With only `server_default`, a freshly inserted ORM row holds `None` for the column until re-fetched — which surfaces as `None` through `@ResultToDict` and as `DetachedInstanceError` under lazy refresh. This was a real bug that hand-written fake-DA tests hid and the real composed stack exposed.
- VARCHAR lengths are always explicit (`VARCHAR(length=255)`, names get 512, keys/paths get 1024). Free text is `Text`. Dict payloads are `JSON` columns named `meta_data` (not `metadata` — that name collides with SQLAlchemy).
- FKs whose child rows must die with the parent declare it in the schema: `ForeignKey('document.id', ondelete='CASCADE')` (collaborators/favorites die with their document — `empty_trash` relies on it).
- The enum class lives in the SAME file as its entity, right above it.
- Derive enum-based values from the member NAME, not the value: a file extension is `f'.{kind.name.lower()}'` — using `.value` after an IntEnum conversion produced the literal extension `.1` in production code. Real bug.

## 5. DataAccess (`data_layers/data_access/thing_data_access.py`)

**MUST subclass a core-lib CRUD base. Hand-rolled `session.add()` / `session.flush()` / bespoke get/update/delete loops are rejected in review.** Pick by delete semantics:

| Base (all in `core_lib.data_layers.data_access.db.crud.*`) | get filter | delete does | use when |
|---|---|---|---|
| `CRUDDataAccess` | `id` (404 if missing) | HARD delete, returns rowcount | rows may really vanish |
| `CRUDSoftDeleteDataAccess` | `id AND deleted_at IS NULL` | stamps `deleted_at=utcnow()`, returns rowcount | normal soft delete |
| `CRUDSoftDeleteWithTokenDataAccess` | `id AND deleted_at_token == 0` | stamps `deleted_at` + `deleted_at_token=epoch`, returns rowcount | soft delete + unique constraints |

Canonical shape (library's `WorkspaceDataAccess`):

```python
allowed_update_types = [
    ValueRuleValidator(Workspace.project_id.key, int),
    ValueRuleValidator(
        Workspace.name.key,
        str,
        custom_validator=lambda v: bool(v) and len(v) <= 255,
    ),
]
rule_validator = RuleValidator(allowed_update_types)


class WorkspaceDataAccess(CRUDSoftDeleteDataAccess):

    def __init__(self, db: SqlAlchemyConnectionFactory):
        CRUD.__init__(self, Workspace, db, rule_validator)

    def create(self, project_id: int, name: str) -> Workspace:
        if not (project_id and name):
            raise ValueError('create requires project_id and name')
        return super().create({
            Workspace.project_id.key: project_id,
            Workspace.name.key: name,
        })
```

Rules:

- The `rule_validator` (module-level, next to the class) is the UPDATE allow-list: one `ValueRuleValidator(Entity.col.key, type, custom_validator=...)` per updatable column. Anything not listed is rejected under strict mode with `PermissionError` (§12 for exact semantics).
- `create` takes explicit positional/keyword args for the identity columns (they are immutable, so they never ride in an update payload), guards them with `ValueError`, and defers the insert to `super().create({...})` — never its own `session.add`.
- `update` overrides guard immutable columns (strip `project_id`/FKs from the payload) before `super().update(id, data)`.
- Domain queries (`get_by_project`, `full_text_search`, `list_trash`, `search_by_name`, …) live on the DataAccess, written in the query-builder style the other DAs use (`session.query(Entity).filter(...).all()` chains). Do NOT refactor an existing DA's access pattern to a different style — that exact change was rejected in review.
- Multi-column dict updates go through `session.query(...).update(data, synchronize_session=False)` with the payload first passed through `self._rule_validator.validate_dict(data, strict_mode=False, strict_output=True)` — `strict_output=True` silently DROPS unknown keys instead of raising, and `synchronize_session=False` avoids `InvalidRequestError: Invalid expression type` on bulk updates. (Both halves were found the hard way.)
- Column references everywhere are `Entity.col.key` / `Entity.col` — never string literals.
- Cross-entity guards live in module-level helpers inside the DA file (library's `_assert_collection_in_workspace(session, workspace_id, collection_id)` raising `StatusCodeException(404)`), called inside `create`/`update` before writing.
- Errors: DA-level argument guards raise `ValueError`; base-CRUD arg guards are bare `assert` (so `AssertionError`); "not found" on `get` is `StatusCodeException(404)` raised by the base's `@NotFoundErrorHandler()`; uniqueness violations bubble up as `sqlalchemy.exc.IntegrityError` for the service's `@DuplicateErrorHandler` to map.
- **A DataAccess is only ever called BY a Service.** Never from a host app, never from a test, never from another lib.

## 6. Services (`data_layers/service/thing_service.py`)

Stateless. `__init__(self, thing_da: ThingDataAccess, ...)` stores `self._thing_da` plus any sibling services it depends on (services may depend on services; they never reach into a sibling's DA).

Decorator stacks — copy these orders exactly (library's `WorkspaceService`/`DocumentService`):

```python
CACHE_KEY_THING = 'foo_thing_{thing_id}'

@ResultToDict()                      # create: dict out; 409 mapping under it
@DuplicateErrorHandler()
def create(self, project_id: int, name: str): ...

@Cache(CACHE_KEY_THING, handler_name=FOO_CORE_LIB_CACHE)      # read: cache outermost,
@ResultToDict()                                               # dict conversion inside
def get(self, thing_id: int):
    try:
        return self._thing_da.get(thing_id)
    except StatusCodeException:
        return None                  # service swallows the DA's 404 into None

@Cache(CACHE_KEY_THING, handler_name=FOO_CORE_LIB_CACHE, invalidate=True)   # writes evict
def update(self, thing_id: int, data: dict):
    return self._thing_da.update(thing_id, data)

@ResultToDict()                      # list endpoints: no cache, just dicts
def list(self, project_id: int, limit: int = 100, offset: int = 0): ...
```

Rules:

- `@Cache(...)` outermost on cached reads so a cache hit skips `@ResultToDict` and the DA entirely; `@ResultToDict()` outermost on `create` so the 409 from `@DuplicateErrorHandler` propagates before dict conversion. Write methods carry `@Cache(..., invalidate=True)` — the decorator runs the function FIRST, then deletes the key (and does not delete if the function raises).
- A write that must also evict a key templated on DIFFERENT params uses the empty-body eviction-hook pattern: a private method decorated `@Cache(OTHER_KEY, handler_name=..., invalidate=True)` whose body is `pass`; the real write calls it with the params that fill the template (library's `_invalidate_project_mapping(project_id)` called by `delete`).
- **Tenant-boundary discipline:** the external tenant key (`project_id`) is translated to the internal row key (`workspace_id`) in exactly one place — a `resolve_<x>_id(project_id)` (cached read that raises a domain `LookupError` subclass when absent) and/or an idempotent `ensure_<x>(project_id, ...)` get-or-create that recovers from a concurrent-create 409 by re-reading. Every other service method takes `project_id`, resolves it internally, and scopes ALL queries by the internal id — a cross-tenant call is a 0-rowcount/`None`/404, never a leak.
- Missing required args raise `ValueError` at the top of the method. Mutations return the affected rowcount so a caller can detect a no-op (missing row / cross-tenant) without an extra read. Getters return `None` for absent (swallowing the DA's 404); "payload builder" methods that must exist raise `StatusCodeException(HTTPStatus.NOT_FOUND, ...)` themselves.
- Services return plain dicts (via `@ResultToDict`) — a host app or test reads fields as `row[Thing.name.key]`. Enum columns arrive as their INT VALUE, datetimes as epoch floats (§12).
- Pure derivations (key builders, slugs, content types) are module-level `_helpers` at the bottom of the service file — testable without the CoreLib.
- Batch loops that delete/purge use a module-level batch constant (`EMPTY_TRASH_BATCH = 10_000`) so tests can patch the MODULE GLOBAL (allowed) instead of internals (forbidden).

## 7. Composition root (`foo_core_lib.py`)

```python
class FooCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf

        if not CoreLib.cache_registry.get(FOO_CORE_LIB_CACHE):           # ALWAYS guarded
            CoreLib.cache_registry.register(FOO_CORE_LIB_CACHE, CacheHandlerRam())

        core_cfg = conf.core_lib
        db = CoreLib.connection_factory_registry.get_or_reg(core_cfg.data.sqlalchemy)

        self._thing_da = ThingDataAccess(db)
        self.thing = ThingService(self._thing_da)                        # public, singular

    @staticmethod
    def install(cfg: DictConfig):
        Alembic(os.path.dirname(inspect.getfile(FooCoreLib)), cfg).upgrade()

    @staticmethod
    def uninstall(cfg: DictConfig):
        Alembic(os.path.dirname(inspect.getfile(FooCoreLib)), cfg).downgrade()
```

- Order inside `__init__`: `super().__init__()` → `self.config = conf` → guarded registry registrations → connection factory → DAs → services (dependency order — a service that needs `self.workspace` is built after it).
- **DB connection via `CoreLib.connection_factory_registry.get_or_reg(core_cfg.data.sqlalchemy)`** — the registry dedupes on `_instance_key_`, so a host composing several core-libs over one database shares ONE engine. (This is also what lets the Alembic wrapper and test helpers find the same factory.)
- **Every registry registration is guarded** (`if not CoreLib.cache_registry.get(KEY): register(...)`) — the registries are process-global and `DefaultRegistry.register` RAISES `ValueError` on a duplicate key, so an unguarded register makes the second CoreLib construction in a process (tests; multi-lib hosts) explode. custom-field registers unguarded — that is the bug pattern, not the convention.
- Cache handler choice: `CacheHandlerRam()` for a lib whose cache is per-process, or `instantiate_config(core_cfg.cache.foo)` / `CacheHandlerMemcached(build_url(**core_cfg.cache.foo.url))` when production needs a shared cache. Either way, registered under the ONE `FOO_CORE_LIB_CACHE` constant that every `@Cache(handler_name=...)` in the lib names.
- Composing another CoreLib: construct it with the SAME conf (`self.doc_to_markdown = DocToMarkdownCoreLib(conf)`), expose the piece services need as an attribute (`self.markdown_extractor = self.doc_to_markdown.document`), and pass that into your services. Host-extension hooks are explicit pass-through methods (`def register_extractor(self, extractor: Extractor): self.doc_to_markdown.document.register(extractor)`) — hosts never reach through the composition.
- `install`/`uninstall` staticmethods exactly as above (the `os.path.dirname(inspect.getfile(FooCoreLib))` argument is how Alembic finds `data_layers/data/db/migrations` — §11). Workflow additionally ships `downgrade(cfg)` → `.downgrade("-1")` (one step back) and `create_migration(cfg, name)` statics — copy those when the lib will evolve its schema.
- A stateless lib (no DB) is the same skeleton minus DB/DAs: `EmailCoreLib` is `super().__init__()`, `self.config = conf`, `self.mail_client = instantiate_config(self.config.core_lib.email_core_lib.client)`, and public methods that delegate to the client. `DocToMarkdownCoreLib` reads its config directly with pure coercions (`float(...)`, `tuple(...)`) and exposes `self.document`.

## 8. Observers / events (when a host must react to what the lib does)

Follow task/workflow exactly (three pieces + wiring):

1. `observer/foo_listener.py` — the ABC a HOST implements. Mandatory events are `@abstractmethod`; optional ones get empty default bodies:

```python
class FooListener(ABC):
    @abstractmethod
    def on_thing_due(self, thing_id: int, project_id: int, ...): ...
    def on_thing_created(self, thing: dict): ...
    def on_thing_updated(self, thing: dict): ...
```

2. `observer/foo_observer_listener.py` — the adapter with the event-key constants:

```python
class FooObserverListener(ObserverListener):
    EVENT_THING_CREATED = 'EVENT_THING_CREATED'
    EVENT_THING_UPDATED = 'EVENT_THING_UPDATED'

    def __init__(self, foo_listener: FooListener):
        self._foo_listener = foo_listener

    def update(self, key: str, value):
        if key == self.EVENT_THING_CREATED:
            self._foo_listener.on_thing_created(value['thing'])
        elif key == self.EVENT_THING_UPDATED:
            self._foo_listener.on_thing_updated(value['thing'])
```

3. In the composition root: a private `Observer`, a GUARDED registry registration under `FOO_CORE_LIB_NAME`, and a typed attach method **named after the domain** (never shadow the base `CoreLib.attach_listener` the way custom-field does):

```python
self._foo_observer = Observer()
if not CoreLib.observer_registry.get(FOO_CORE_LIB_NAME):
    CoreLib.observer_registry.register(FOO_CORE_LIB_NAME, self._foo_observer)

def attach_foo_listener(self, foo_listener: FooListener):
    self._foo_observer.attach(FooObserverListener(foo_listener))
```

4. Services FIRE events through empty `_fire_*` methods decorated with `@Observe` — the decorator does the dispatch, the body is `pass`:

```python
@Observe(event_key=FooObserverListener.EVENT_THING_CREATED, observer_name=FOO_CORE_LIB_NAME)
def _fire_on_thing_created(self, thing: dict):
    pass
```

Event payloads are the `@ResultToDict`-style dicts (a listener gets `thing[Thing.id.key]`, not an ORM row).

## 9. Jobs (scheduled background work)

- `jobs/foo_job.py`:

```python
class FooDueJob(Job):
    def initialized(self, data_handler: FooCoreLib):
        assert data_handler and isinstance(data_handler, FooCoreLib)
        self._foo_core_lib = data_handler

    def run(self):
        self._foo_core_lib.thing.notify_overdue_things()
```

- Yaml under the lib's own section:

```yaml
  foo_core_lib:
    jobs:
      thing_due:
        initial_delay: startup        # 'boot'/'startup' → runs immediately; else a pytimeparse duration
        frequency: 1d                 # omit for a one-shot job
        handler:
          _target_: foo_core_lib.jobs.foo_due_job.FooDueJob
```

- Wire in `__init__` (after the services exist): `self.load_jobs(self.config.core_lib.foo_core_lib.jobs, {'thing_due': self})` — the dict maps job name → the `data_handler` passed to `initialized` (task passes the whole CoreLib; custom-field passes the one service it needs).
- `initial_delay` is MANDATORY (`load_jobs` raises `ValueError` when falsy). A job that is also a `CoreLibListener` is auto-attached.
- **Test consequence:** a `startup` job queries its table the moment `start_core_lib()` runs — before any test created rows. The test helper must then pre-create tables on the engine AND run `install()` before `start_core_lib()` (task's helper, §13.4). A lib with no startup jobs skips both.

## 10. Non-DB backends (object storage etc.) — the `connections/` pattern

Three pieces, mirroring the DB stack (library's storage is the reference):

1. **`connections/storage_connection_factory.py`** — `class StorageConnectionFactory(ConnectionFactory)`. Validates EVERY required config key in `__init__` with a dedicated error type (`class StorageConnectionError(ValueError)`) BEFORE building anything — including pairwise rules (`access_key` and `secret_key` both-or-neither). Builds the client once; `get()` returns a fresh thin `StorageConnection(self._client)`.
   **The heavy SDK import is LAZY** — `import boto3` is the first line INSIDE the `_build_client` staticmethod, never at module top. That keeps the SDK an optional dependency: the lib imports, config-validation tests run, and only actually connecting requires it installed. Consequently `boto3` is NOT in `requirements.txt`.
2. **`connections/storage_connection.py`** — lifecycle only: `__enter__` returns the raw client, `__exit__` does nothing. No verbs here.
3. **`data_layers/data_access/storage_data_access.py`** — `class StorageDataAccess(DataAccess)` owns ALL the verbs (`put`, `get`, `delete`, `exists`, `list` with pagination, `presigned_url`), each opening `with self._factory.get() as client:`. Returns small dataclasses (`StorageObject(key, size, etag)`), not raw SDK responses.

In the composition root the naming is literal: `storage_data_access = StorageDataAccess(StorageConnectionFactory(storage_cfg))` — the variable is named what it is (a bare `storage = ...` was rejected). Key-naming policy (prefixes like `originals/`/`markdown/`) is NOT a connection concern — it lives on the service that owns the keys, passed in as constructor args read from config.

Provider quirks are absorbed in the factory (`provider: minio` + `addressing_style: auto` → `path`). Ship `docker-compose-dev.yaml` with the real local backend (MinIO server + healthcheck + an `mc` one-shot that creates the bucket `--ignore-existing`) so `docker compose -f docker-compose-dev.yaml up -d` gives a working backend with documented stable credentials.

## 11. Migrations — exact conventions (this section was rewritten three times in review; every detail matters)

### 11.1 How Alembic is wired (no alembic.ini exists, anywhere)

`core_lib.alembic.Alembic(core_lib_path, cfg)` builds the alembic `Config()` IN MEMORY from the yaml node `core_lib.alembic` (base group provides: `script_location: data_layers/data/db/migrations`, `file_template: "%%(year)d-%%(month).2d-%%(day).2d_%%(rev)s_%%(slug)s"`, `version_file_name: '.migration_ver'`, `render_as_batch: false`, `version_table: alembic_version` — which your lib yaml overrides to `foo_alembic_version`). `script_location` is resolved relative to `core_lib_path` = `os.path.dirname(inspect.getfile(FooCoreLib))`, and the DB URL is built from `core_lib.data.sqlalchemy.config.url` — which is WHY the DB block must live at that exact path (§3.1). Migrations run through `EnvironmentContext` directly; `env.py` is stock boilerplate that is effectively bypassed — copy `env.py` and `script.py.mako` verbatim from a sibling lib and never edit them.

### 11.2 The files

- Filename: `<YYYY-MM-DD>_<N>_<reason_slug>.py` — produced by the `file_template`; the date is the creation date, `N` is the revision number, and the slug states the REASON (`create_db`, `add_creator_user_id`, `index_target_custom_field_history_fk`). Real sequences to imitate: task's `2024-04-02_1_create_db.py` … `2026-06-05_5_add_creator_user_id.py`.
- Module header, exactly:

```python
"""create_db

Revision ID: 1
Revises:
Create Date: 2026-06-21 08:26:06.852789

"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy import ForeignKey

from foo_core_lib.data_layers.data.db.entities.thing import Thing

revision = '1'
down_revision = None
branch_labels = None
depends_on = None
```

- `revision` is a bare integer as a STRING (`'1'`, `'2'`, …), `down_revision` is the previous number (or `None` for the first). Never uuid-style revision ids.
- `.migration_ver` (next to `versions/`) holds the latest revision number as plain text. `Alembic.create_migration(name)` maintains it (`rev_id = str(count + 1)`); if you hand-write a migration, update it yourself — custom-field's is stale (says 9, has 11 files); don't repeat that.
- **While the lib is UNRELEASED there is exactly ONE migration.** Every schema change during initial development is folded into `<date>_1_create_db.py` — never a stack of `2_add_x.py`, `3_fix_x.py` before first release. After release, changes append sequential migrations following the same conventions (prefer `FooCoreLib.create_migration`-style generation, then hand-edit the body to the entity-referencing style below).

### 11.3 The body — everything referenced through the entities

```python
def upgrade():
    op.create_table(
        Thing.__tablename__,
        sa.Column(Thing.id.key, sa.Integer, primary_key=True, nullable=False),
        sa.Column(Thing.workspace_id.key, sa.Integer, ForeignKey('workspace.id'), nullable=False),
        sa.Column(Thing.name.key, sa.VARCHAR(length=255), nullable=False),
        sa.Column(Thing.kind.key, sa.Integer, nullable=False),
        sa.Column(Thing.position.key, sa.Integer, nullable=False, server_default='0'),

        sa.Column(Thing.created_at.key, sa.DateTime, default=datetime.utcnow),
        sa.Column(Thing.updated_at.key, sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column(Thing.deleted_at.key, sa.DateTime, default=None),

        sa.Index(Thing.INDEX_WORKSPACE_ID, Thing.workspace_id.key, unique=False),
        sa.Index(Thing.INDEX_WORKSPACE_NAME, Thing.workspace_id.key, Thing.name.key, unique=False),
    )


def downgrade():
    op.drop_table(Thing.__tablename__)
```

- Table names: `Entity.__tablename__`. Column names: `Entity.col.key`. Index/constraint names: `Entity.INDEX_*` constants. **The ONLY string literal permitted is the ForeignKey target** (`ForeignKey('workspace.id')`, with `ondelete='CASCADE'` where the entity declares it). Writing `'thing'` or `'workspace_id'` as a literal is exactly the "not paying attention to the smallest details" review rejection.
- Type mapping: `IntEnum(X)` column → `sa.Integer`. `VARCHAR` keeps its exact length. `JSON` → `sa.JSON`, `Text` → `sa.Text`.
- Mixin columns are SPELLED OUT per table, in this order after the business columns: `created_at` (`default=datetime.utcnow`), `updated_at` (`default=datetime.utcnow, onupdate=datetime.utcnow`), `deleted_at` (`default=None`), and for token entities `deleted_at_token` (`sa.Integer, default=0`).
- Unique constraints over soft-deletable rows include the token column and take their name from the entity constant: `sa.UniqueConstraint(A.document_id.key, A.user_id.key, A.deleted_at_token.key, name=A.INDEX_DOCUMENT_USER)`.
- `downgrade()` drops tables in REVERSE dependency order (children first).
- Create parent tables before children within `upgrade()` (FK targets must exist).
- **Before committing, verify the migration produces a schema IDENTICAL to `Base.metadata.create_all`** — run both against fresh sqlite databases and diff the reflected schema (tables, columns, types, nullability, defaults, indexes, uniques). Any drift means the migration (or the entity) is wrong.
- Nothing else goes in the migrations folder. No invented helper modules, no config, no README beyond what siblings have.

## 12. Framework contracts you must know (these bite; verified against core-lib source)

- **`CRUD.create(data)`** returns the ENTITY instance (id populated; session `expire_on_commit=False`, auto-commit on context exit). Validates with `strict_mode=False` (unknown keys pass; keys the entity lacks are skipped; `'id'` is skipped).
- **`CRUD.update(id, data)`** returns **`None`** (base). It validates with plain `validate_dict(data)` — which is ALWAYS strict-mode (see next bullet) — and does NOT filter soft-deleted rows. If your service needs a rowcount, your DA override must `return session.query(...).update(...)` itself.
- **`RuleValidator.validate_dict` gotcha:** the method's own defaults (`strict_mode=True, strict_output=False`) override the constructor's — constructor-level settings apply only when the caller passes `None` explicitly. `strict_mode=True` → unknown key raises `PermissionError`; `strict_mode=False, strict_output=True` → unknown key silently dropped. EVERY validation failure is `PermissionError` (wrong type, non-nullable None, failing `custom_validator`, unparseable datetime string).
- **`get` on every CRUD base is wrapped in `@NotFoundErrorHandler()`, which raises `StatusCodeException(404)` on ANY falsy result** (None, `[]`, `0`, `''`). Services must try/except it when "absent → None" is the contract.
- **`@DuplicateErrorHandler()`** catches only `sqlalchemy.exc.IntegrityError` and raises `StatusCodeException(HTTPStatus.CONFLICT)`. It is NOT applied by the CRUD base — put it on your create paths.
- **`@ResultToDict()`** converts: Enum → `.value`; `datetime` → epoch FLOAT (`.timestamp()`); `date` → midnight epoch; `Decimal` → float; entity → dict of columns (+ loaded relationships, cycle-guarded); lists recursed; namedtuples → dicts; **`None` passes through**. So tests read `row[Thing.kind.key] == ThingKind.ALPHA.value` (an int) and timestamps as floats.
- **`@Cache`:** key is a `str.format` template bound BY PARAMETER NAME from the wrapped function's signature (positional, kwargs, then declared defaults) — a placeholder that names a non-parameter renders as `!M{name}M!`, a falsy param as `!E{name}E!`; the key is space-stripped and truncated to 250 chars. Unknown `handler_name` raises `ValueError` at call time. `invalidate=True` runs the function FIRST, then deletes the key, and skips deletion when the function raises. String `expire` (e.g. `'1h'`) is parsed at decoration time.
- **`IntEnum` TypeDecorator is truthiness-based both directions:** a member with value `0` binds as NULL and a stored `0` reads back as `None` — **enum values MUST start at 1.**
- **Mixins carry Python-side `default=` only** (no `server_default`, no `nullable=False`) and `_creation_order = 9998` pins them to the end of the table.
- **`DefaultRegistry.register` raises `ValueError` on a duplicate key** (hence guarded registration); `unregister` is silent when absent; `get()` with no key falls back to the FIRST registered object; `registered()` lists keys.
- **`start_core_lib()` raises `CoreLibInitException` if called twice** on the same instance.
- **`SqlAlchemyConnectionFactory`:** reads `create_db` (code default TRUE → `Base.metadata.create_all` at construction; base yaml ships `false` — prod relies on `install()`), `log_queries` → `echo`, `session.pool_*` (pool args are OMITTED for sqlite). Session contexts auto-commit on clean exit and rollback on exception.
- **`build_url`:** `{protocol: sqlite, file: ':memory:'}` → `sqlite:///:memory:`.

## 13. Tests — the philosophy and the exact mechanics

### 13.1 The formula (non-negotiable)

**A test asserts the data you WANT the function to return — recomputed independently — never the data the function happens to return.** Expected values are hardcoded literals or derived from the test's own inputs by DIFFERENT means than the code under test. Never echo a function's output back into its own assertion. Never loosen an assertion so a test passes. **When a test fails, the CODE is wrong — you fix the code, not the test.** A test that adapts itself to broken output is worse than no test. Prove strictness with a mutation check: temporarily break the production code (drop a decorator, flip a filter) and confirm the suite goes RED; revert.

### 13.2 Test the REAL composed stack — fakes hid real bugs

Suites run against the real `FooCoreLib` — real DataAccess, real `@Cache`/`@ResultToDict`/`@DuplicateErrorHandler`, real rule validators, real DB (in-memory sqlite), real backend (moto/MinIO for S3). Hand-written fake DAs/fake storage previously masked three shipped bugs in one lib: (1) a `server_default`-only column returning `None`/`DetachedInstanceError` on the real ORM, (2) a file extension computed from `enum.value` producing `.1`, (3) fake rows returning enum MEMBERS where the real stack returns int values. The ONLY permitted double is a backend that cannot run on a test host (the ~50-binary doc-to-markdown pipeline) — injected through a sanctioned seam (§13.5), never by monkeypatching internals.

### 13.3 Service-only — we test what we expose, and we expose services

- A test calls ONLY public service methods on the composed lib: `self.foo_core_lib.thing.create(...)`. **The DataAccess and any storage adapter are internal — never touched by a test: not to create fixtures, not as a read-oracle.** Grep the finished test file for `_da`, `._db`, `_storage`, or any `._<private>` on the lib object: ZERO hits.
- **No standalone DataAccess test files.** The DA is exercised through its service. (Deleted from library in review: `test_data_access.py`, `test_document_*_data_access.py`, a DA-seeded cascade test, and a DA-direct search test whose behavior `lib.search` already covered.)
- Fixtures are created THROUGH services (`workspace.create` → `collection.create` → `document.upload` → `document_collaborator.grant`); state is verified THROUGH services (`get`, `list`, `list_trash`, `search`, `is_favorite`, `get_markdown`, presigned URLs from `get_download_url`/`get_view_payload`).
- Whatever is only observable by reaching into internals gets re-expressed through the service or DROPPED — deleted categories, for the record: exact blob-key sets in storage; raw `deleted_at` reads ("trashed" is: absent from `get`/`list`, present in `list_trash`); cache-hit proofs that mutate the row behind the cache (cache correctness is observable only as write→read freshness); DA-monkeypatched race simulations (duplicate behavior is exercised by calling the service twice and asserting what it REALLY does); exact intra-type orderings that depend on `created_at` you cannot set through any service (assert set-membership, window sizes, and type-boundary ordering instead — never a flaky exact sequence).
- Storage-backed assertions through the service: markdown content via `get_markdown`; original presence via a presigned URL that contains the document's own `original_key` (taken from the upload's returned dict), a `Signature=` param, and `Expires=` ≈ `now + expiry` (absolute epoch, `assertAlmostEqual(..., delta=60)`).
- Allowed OUTSIDE the service suites, in their own plain-`unittest` files (no CoreLib): entity-introspection tests (`Entity.__table__.indexes` carries the FK index — custom-field's `test_target_custom_field_history_entity.py` is the reference); pure-helper tests (slug/key derivation functions); backend "client" adapter tests with a mocked SDK client through the real thin connection; an env-guarded REAL-backend integration test (`@unittest.skipUnless(os.environ.get('FOO_STORAGE_ENDPOINT_URL'), ...)`) that round-trips every verb and cleans up after itself.

### 13.4 `tests/helpers/utils.py` — the one bootstrap (verbatim canonical shape)

```python
import itertools
import os
import threading
import traceback

import hydra
from dotenv import load_dotenv
from hydra.core.global_hydra import GlobalHydra

from core_lib.core_lib import CoreLib
from foo_core_lib.foo_core_lib import FooCoreLib


class OblInstance(object):
    instance = None
    config = None


threadLock = threading.Lock()

_project_ids = itertools.count(1)


def new_project_id() -> int:
    return next(_project_ids)


def load_config():
    if not OblInstance.config:
        path = os.path.join(os.path.dirname(__file__), '..', 'data')
        load_dotenv(dotenv_path=os.path.join(path, '.env'))

        GlobalHydra.instance().clear()
        hydra.initialize(config_path=os.path.join('..', 'data', 'config'), caller_stack_depth=1)
        OblInstance.config = hydra.compose('config.yaml')
    return OblInstance.config


def sync_create_start_core_lib() -> FooCoreLib:
    threadLock.acquire()
    if not OblInstance.instance:
        try:
            [CoreLib.cache_registry.unregister(key) for key in CoreLib.cache_registry.registered()]
            [CoreLib.observer_registry.unregister(key) for key in CoreLib.observer_registry.registered()]
            OblInstance.instance = FooCoreLib(load_config())
            OblInstance.instance.start_core_lib()
        except BaseException as e:
            print(''.join(traceback.format_exception(type(e), e, e.__traceback__)))
            raise e

    # Clear the cache
    for key in CoreLib.cache_registry.registered():
        CoreLib.cache_registry.get(key).flush_all()

    threadLock.release()
    return OblInstance.instance
```

- ONE composed CoreLib per test process, shared by every suite. The lock must not stay held after a failed boot (a stuck lock deadlocks the next `setUpClass` — keep the try/raise shape; the admin-backend variant uses `finally`).
- `new_project_id()` is a MONOTONIC counter, not `random.randint` — the tenant key is uniquely constrained, so a random collision is a hard 409 mid-suite. (Libs whose tenant key is not unique, like task, may use `random.randint(1000, 10000)` per test file; when in doubt, the counter.)
- **task-variant** (needed ONLY when the lib schedules a `startup` job that queries a table immediately): before constructing the lib, pre-create the tables on the shared engine and run install —
  `db_factory = CoreLib.connection_factory_registry.get_or_reg(config.core_lib.data.sqlalchemy)` → `Thing.__table__.create(db_factory.engine, checkfirst=True)` → construct → `instance.install(config)` → `start_core_lib()`.
- Test-only stand-in entities (rows your queries JOIN against but another lib owns, e.g. a `User`) live in `tests/data/entities/` and are created the same way (`TestUser.__table__.create(engine, checkfirst=True)`) inside the helper.
- **Backend-control seams live HERE, not in tests:** a `@contextmanager def use_markdown_extractor(lib, extractor):` that swaps `lib.document._markdown_extractor` and restores it in `finally`. A test uses the context manager; only utils knows the private attribute. (For a stateless lib, prefer the front door: doc-to-markdown's orchestration units pass controlled extractors through the REAL production constructor parameter — `DocumentService(selection_service=..., extractors=[...])` — nothing monkeypatched.)

### 13.5 `tests/data/` — config + env

- `config/config.yaml`: `defaults: [core_lib, foo_core_lib, foo_core_lib_test]` where `foo_core_lib_test.yaml` (same dir, starts `# @package _global_`) carries test-safe overrides — task's sets `create_db: true` + sqlite + `version_table` + job config; email's sets a fake `api_key: SOME-KEY` so construction succeeds. If the packaged yaml is FULLY env-driven (library), the third group may be unnecessary — then use `defaults: [core_lib, foo_core_lib, _self_]` plus inline keys for anything extra (e.g. a composed sibling's section). Never compose a sibling REPO's config group (§3.4).
- `.env` (loaded by `load_config`): `MEMCACHED_HOST=localhost` ALWAYS (the base group interpolates it with no default); DB → `FOO_DB_PROTOCOL=sqlite`, `FOO_DB_FILE=:memory:`, `FOO_DB_CREATE_DB=true` (tests rely on `create_all`, not Alembic — except the task-variant); backend endpoints → **`http://127.0.0.1:9000`, NEVER `http://localhost:9000`**: on Windows `localhost` resolves to IPv6 `::1` first and a moto/MinIO bound on IPv4 stalls EVERY NEW connection ~60s before falling back — a 8-second suite becomes ~17 minutes at ~0s CPU, and the only tell is `create_connection` at the top of a `faulthandler` dump.
- Local S3 without Docker: `pip install "moto[server]"`, run exactly ONE `python -m moto.server -p 9000` (several instances on one port scatter requests and stall), create the bucket once via boto3. boto3/moto are dev-env deps, never `requirements.txt`.

### 13.6 Writing the suites

- **One `unittest.TestCase` class per file, every test a method of it.** File `test_thing_service.py` → `class TestThingService`. Merging multiple classes into one was a review requirement, not a preference.
- `setUpClass` is exactly: `cls.foo_core_lib = sync_create_start_core_lib()` — the attribute is the FULL lib name (`cls.library_core_lib`, `cls.task_core_lib`), never `cls.lib`.
- Access is inline and fully spelled at every call site: `self.foo_core_lib.thing.create(...)`. **No `@property` accessors, no `service = self.foo_core_lib.thing` aliases, no helper indirection that hides which service a failing line hit.** Small `_seed()`/`_upload()` fixture helpers ON the test class are fine — they still call services with the full spelling.
- The DB (and bucket) are shared across the whole run: every test takes a fresh `new_project_id()`, never assumes an empty table, an absolute autoincrement id, or `id == 1`. "ids are monotonic" is asserted relatively (`second > first`).
- Unknown-id branches probe with a constant far above any autoincrement: `ABSENT_THING_ID = 2_000_000_000` — never `99`/`999` (a long-lived shared DB WILL reach those).
- Dict fields are read with entity keys — `row[Thing.name.key]`, `row[Thing.kind.key]` — never string literals.
- Enum columns assert the INT value (and optionally round-trip: `ThingKind(row[Thing.kind.key]) is ThingKind.ALPHA`).
- Log-contract tests use `assertLogs` on the service's module logger (warning fallbacks, swallowed extraction errors) — asserting the documented side channel, not internals.
- Patching a MODULE-LEVEL tuning constant (`document_service.EMPTY_TRASH_BATCH = 2`) to force loop boundaries is allowed — always restored in `try/finally`. Patching methods/attributes of the composed lib is NOT (the one exception is the utils-owned seam, §13.4).
- Exercise error paths as the service defines them: 409 via a real duplicate through the real DB (`assertRaises(StatusCodeException)` + `status_code == HTTPStatus.CONFLICT`), 404/`None` via the service's own contract, `ValueError` for missing args, `PermissionError` for rule-validator rejections — with a follow-up assertion that the failed call left the data untouched (read it back through the service).
- The composed-lib smoke file (`test_foo_core_lib.py`) asserts the PUBLIC surface only: every service attribute exists and works end to end with one real call each; config threading is proven through BEHAVIOR (an env-value visible in an output), not by reading private fields.
- Suite hygiene facts: the hydra `version_base` UserWarning at bootstrap is expected noise; run with `PYTHONPATH="../core-lib;." python -m unittest discover -s tests -p "test_*.py"` (`;` on native-Windows Python, `:` on POSIX — sibling repos on the path as needed, e.g. library adds `../doc-to-markdown-core-lib`).

## 14. Packaging / repo hygiene

- `requirements.txt` — RUNTIME deps only: `core-lib` first, then real runtime deps (`temporalio`, another `*-core-lib` your lib composes). Test-only deps (hydra, python-dotenv, freezegun, boto3, moto) come from the dev environment — never listed. Optional backends stay optional via the lazy-import pattern (§10). (email's file omits `core-lib` — an inconsistency, not a convention.)
- `.coveragerc`: `source = foo_core_lib`, `branch = True`, omit `foo_core_lib/data_layers/data/db/migrations/*`. `.gitignore` includes `.coverage` and `.coverage.*`; never commit the data files (rule at the top of this document).
- No `npm run build`-style heavy steps in any Dockerfile — install dependencies only.
- Constants that multiple modules need live in `constants.py` (or a dedicated constants module) — never in a heavyweight module whose import drags in half the lib; that is how circular imports are born.

## 15. Build order (follow it top to bottom)

1. Skeleton: package dirs + every `__init__.py` (§2), `constants.py`, `requirements.txt`, `.coveragerc`, `.gitignore`.
2. Config: `config/foo_core_lib.yaml` (+ empty `config/__init__.py`), searchpath plugin, repo-root `core_lib_config.yaml`. Every future config key goes here FIRST.
3. Entities (+ enums, INDEX_ constants, mixins).
4. DataAccess per entity (CRUD base + rule_validator + domain queries).
5. Services per entity (decorators, tenant boundary, events fired via `@Observe` if any).
6. Composition root (guarded registrations, `get_or_reg`, services in dependency order, install/uninstall) — plus observer/jobs wiring if used.
7. The ONE first migration + `env.py`/`script.py.mako` copied from a sibling + `.migration_ver` = `1`. Verify schema identity against `create_all`.
8. Test bootstrap: `tests/helpers/utils.py`, `tests/data/config/config.yaml` (+ `foo_core_lib_test.yaml` or inline `_self_` keys), `tests/data/.env`.
9. Service test suites, one class per file, written to §13. Entity/helper/adapter plain-unittest files as needed.
10. Run the FULL suite from the repo root; then mutation-check at least the cache decorators and one rule validator; then run a sibling lib's suite to confirm you broke nothing shared.

## 16. Things to AVOID (each rejected in review or debugged at cost)

1. Inventing any pattern the sibling libs don't use (§0) — including "improvements".
2. Hand-rolled CRUD in a DataAccess (`session.add`/`session.flush` loops) instead of the CRUD bases.
3. Calling or testing a DataAccess from outside the lib. Standalone DA test files.
4. A bespoke test harness that wires DAs+services directly instead of `sync_create_start_core_lib()`.
5. Fake DAs / fake storage inside service tests (they hid three real bugs — §13.2).
6. `@property`/alias indirection in tests; `cls.lib`; anything but the full inline spelling.
7. Plural public service attributes (`self.documents`); exposing a DA publicly.
8. `.get('key', default)` / `try` around config reads; missing keys in the packaged yaml.
9. Bare `${oc.env:...}` for booleans/numbers (string-truthiness bug) — always `oc.decode`.
10. Composing a sibling repo's hydra config group in any defaults list.
11. Missing `config/__init__.py` (or any package `__init__.py`).
12. `localhost` in backend endpoints (Windows `::1` stall) — `127.0.0.1`.
13. More than one moto/MinIO bound to a port; per-run bucket wipes that tests don't need.
14. `random.randint` for a uniquely-constrained tenant key in tests; magic absent-ids like `99`.
15. String literals for table/column/index names in migrations; uuid revision ids; multiple migrations before first release; a stale `.migration_ver`.
16. `server_default` without `default=` on an entity column.
17. Enum values starting at 0 with the `IntEnum` decorator type.
18. Unguarded `cache_registry`/`observer_registry` registration; shadowing `CoreLib.attach_listener` instead of `attach_foo_listener`.
19. Editing a test to make it pass; echo-assertions; exact-order assertions over `created_at` ties; tests that "pass with broken data".
20. Heavy SDK imports at module top for optional backends (`import boto3` belongs inside the client builder); optional backends in `requirements.txt`.
21. Deriving strings from `enum.value` when the NAME is meant (`.1` extension bug).
22. Committing `.coverage` files; letting a Dockerfile run build steps beyond dependency installation.

## 17. Final checklist before handing the lib over

- [ ] Package imports clean with NO optional SDKs installed (`python -c "import foo_core_lib"`).
- [ ] `FooCoreLib(compose)` constructs twice in one process without registry explosions (guards work).
- [ ] All public attributes are singular service names; no DA reachable publicly.
- [ ] `config/__init__.py` + `hydra_plugins/.../__init__.py` exist; `pkg://foo_core_lib.config` composes from a scratch dir.
- [ ] Every config key code reads exists in `foo_core_lib.yaml`; booleans/ints wrapped in `oc.decode`; DB block at `core_lib.data.sqlalchemy`; `version_table: foo_alembic_version`.
- [ ] ONE migration; filename/date/rev/slug per §11.2; body references entities only; `downgrade()` reverse order; `.migration_ver` = `1`; schema byte-identical to `create_all`; `install()`/`uninstall()` run against a scratch DB.
- [ ] `tests/helpers/utils.py` matches §13.4 (task-variant only if startup jobs); `.env` has `MEMCACHED_HOST`, sqlite `:memory:`, `127.0.0.1` endpoints.
- [ ] Every service suite: one class per file; `cls.foo_core_lib`; inline access; fresh `new_project_id()` per test; `ABSENT_* = 2_000_000_000`; `Entity.col.key` for every dict read; zero `_da`/`_db`/`_storage` greps.
- [ ] Mutation check done (break code → red; revert → green). Full suite green from a clean checkout with only the documented env (moto/MinIO where applicable).
- [ ] `requirements.txt` runtime-only; `.coveragerc` present; nothing under `.coverage*` tracked.
