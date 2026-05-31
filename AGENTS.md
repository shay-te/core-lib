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

## Database column access — use `<Entity>.<column>.key`, never strings

**Rule.** Whenever code reads or names a DB column — keying into a dict that
came back from a `ResultToDict()` data-access call, naming a column in a query
condition, etc. — reference it as `<Entity>.<column>.key` (or `.value` for an
enum), **not** as the raw `'column'` string literal.

```python
# YES
lead[FunnelLead.score.key]
stage_def[FunnelStage.name.key]
score_row[FunnelStageFieldScore.comparison_value.key]
meta_data.get(MetaDataField.BETWEEN_HIGH.value)

# NO — magic string that won't move when the column is renamed
lead['score']
stage_def['name']
score_row['comparison_value']
meta_data.get('between_high')
```

**Why.** Renaming a column then becomes a typed reference that the IDE / Python
catches at import time, not a silent string mismatch at runtime. The dict from
`ResultToDict()` is keyed by the SQLAlchemy `Column.key`, so the reference
resolves to the exact same string while staying coupled to the entity.

**What still stays a string:** Python keyword-argument names in a function
call (e.g. `name=stage_def[FunnelStage.name.key]` — `name=` is the parameter
name, not a string), and class/attribute identifiers in code. Everything that
*is* a string literal naming something — a column, a JSON-payload key, a spec
DSL key — should have a named constant or `.key`/`.value` you reach for instead.

**More generally — prefer a constant over a literal whenever one exists.** If
there's an enum value, a class attribute, or a known `.key`/`.value` for what
you're typing, reach for that instead of writing the string by hand.

## Spec DSL keys belong in their consumer's module as constants

**Rule.** When a "spec" (a plain-data dict structure) is read by a consumer
module (e.g. a seeder, a renderer), the **dict keys that aren't DB columns**
still get module-level constants, defined in the **consumer** module and
imported by every spec.

```python
# in funnel_seed.py — the consumer owns the spec-shape contract:
STAGE_ELIGIBILITY = 'eligibility'
STAGE_SCORES = 'scores'
FIELD_KEY = 'field_key'

# in madigan_funnel_spec.py — every spec imports them and uses them as keys:
from .funnel_seed import FIELD_KEY, STAGE_ELIGIBILITY, STAGE_SCORES
MADIGAN_FUNNEL_STAGES = [
    {FunnelStage.name.key: '…',
     STAGE_ELIGIBILITY: [{FIELD_KEY: RecordTypeField.key, …}],
     STAGE_SCORES:      [{FIELD_KEY: ServiceTierField.key, …}]},
    …
]
```

**Why.** Renaming a DSL key then happens in *one* place (the consumer), every
spec picks it up, and a reader can find every site by grep on a symbol instead
of a fuzzy string.

## Define functions and methods at module/file top level — never re-define per call

**Rule.** A function or method gets defined **once at import**, not rebuilt
inside a loop, inside another function called per object, or inside an
orchestration method that runs per row/per organization.

```python
# NO — `get_external_field_id` is rebuilt for every organization:
def seed_funnel(name, stages):
    def seed_for_org(org_id):
        def get_external_field_id(field_key):
            ...
        for stage_def in stages:
            ...

# YES — methods defined once on a class at module top level; a single
# lightweight instance is built per call, and the per-org cache is just data:
class _FunnelSeeder:
    def __init__(self, conn, …): ...
    def _resolve_external_field_id(self, org_id, field_key, cache): ...
    def seed_org(self, org_id, stages): ...
```

If the helper needs per-call state (conn, entities, names), a small class
holding that state is the cleanest solution — the methods are then defined
once on the class, and per-call state is on the instance. Pure helpers go at
module level. Per-row state (caches, accumulators) is just data passed in.

## Every DB query belongs in its own private function/method

**Rule.** A method or function does **one DB statement**, named for what it
does. The orchestration method then reads as a sequence of named calls — no
inline `conn.execute(sa.select(…))` / `sa.insert(…)` / `sa.delete(…)` mixed
into business logic.

```python
# YES — every query has a name; orchestration is a readable script:
class _FunnelSeeder:
    def _funnel_already_seeded(self, org_id): ...   # one SELECT
    def _insert_funnel(self, org_id): ...           # one INSERT
    def _insert_stage(self, …): ...                 # one INSERT
    def _insert_rule(self, …): ...                  # one INSERT
    def _insert_score(self, …): ...                 # one INSERT
    def seed_org(self, org_id, stages):
        if self._funnel_already_seeded(org_id):
            return
        funnel_id = self._insert_funnel(org_id)
        for stage_def in stages:
            stage_id = self._insert_stage(funnel_id, stage_def, …)
            …
```

**Why.** Each query gets a real name (you can grep for it, refactor it, test
it), the orchestration reads top-to-bottom as intent, and a future change to
"how do we look up X" is one method to edit, not five inline patches.

## Naming reflects *what* and *which kind*

**Rule.** A symbol's name says *what* it returns/operates on **and**, when
there's a kind/variant distinction, *which kind*. Don't make the reader infer
either from context or the docstring.

```python
# NO — "of what?" the reader has to read the body to know.
def _resolve_target_id(self, field_key): ...

# Better — says what:
def _resolve_field_target_id(self, field_key): ...

# Best — also says which kind, because there's also a custom-field path:
def _resolve_built_in_field_target_id(self, field_key): ...
def _resolve_external_field_id(self, …): ...   # different "id" — distinct name
```

The same applies to types and parameters. `field_key_to_custom_label:
dict[str, str]` smuggled in a "label" that the consumer didn't care about —
`field_key_to_is_built_in: dict[str, bool]` names the actual decision being
made. If your name needs a docstring to disambiguate "is this the built-in
path or the custom one?", rename it instead of explaining it.

## Reusable engines live in their own file

**Rule.** Generic mechanics that any client (or any spec) could call go in a
separate, client-agnostic module. The client file only owns its *data* (its
spec / its constants) and a thin call into the engine. A new client = a new
data file + a thin call — never a copy-pasted engine.

```python
# YES — engine and client are different files:
#   admin_core_lib/.../funnel/funnel_seed.py        ← engine (reconcile_funnel)
#   admin_core_lib/.../funnel/madigan_funnel_spec.py← Madigan data
#   admin_core_lib/.../funnel/acme_funnel_spec.py   ← Acme data (one day)
# Each spec file is just: MY_FUNNEL_STAGES = [...] + a call to reconcile_funnel.
```

This pairs with the spec-DSL-keys rule above: the engine module owns the
*shape* (the key constants and the contract), the data module owns the
*content*.
