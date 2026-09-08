# AGENTS Notes — core-lib (canonical rulebook for every `*-core-lib`)

> **This file is the single, canonical rulebook for every `*-core-lib` package
> — present or future.** Read the AGNOSTIC principles first, then follow the
> **canonical recipe** (§0–§17) for building or extending a library. The recipe
> is distilled from the real sibling libs plus every owner correction; its §0
> meta-rule is *never invent* — if the existing libs don't do it, don't do it.
>
> Library-specific lessons stay in that library's own `AGENTS.md`. This file
> references no file outside this library.

---

# A column name is NEVER a string literal — `Entity.column.key`

One rule, stated once, because it is the single most repeated review
correction. It already appears per-layer in §5, §6, §11.3 and §13; this is the
consolidated form.

**Anywhere you name a column outside the entity's own class body, write
`Entity.column.key`.** Never `'scale_key'`, never `'normalized'`, never
`'project_id'`.

| Where | Correct | Wrong |
|---|---|---|
| Migration column | `sa.Column(Thing.name.key, …)` | `sa.Column('name', …)` |
| Migration table / index | `Thing.__tablename__`, `Thing.INDEX_*` | `'thing'`, `'ix_thing_name'` |
| Query filter | `Thing.workspace_id == x` | `text("workspace_id = …")` |
| DataAccess payload | `{Thing.name.key: value}` | `{'name': value}` |
| `ValueRuleValidator` | `ValueRuleValidator(Thing.name.key, str)` | `ValueRuleValidator('name', str)` |
| Reading a service dict | `row[Thing.name.key]` | `row['name']` |
| **Test assertion** | `self.assertEqual('x', row[Thing.name.key])` | `row['name']` |

**Why.** A service returns plain dicts via `@ResultToDict`, whose keys are the
column names. A literal is a silent copy of a name that lives somewhere else:
rename the column and the literal still parses, still type-checks, and returns
`None` or a `KeyError` at runtime instead of failing at the rename. `.key` makes
the name exist in exactly ONE place, so a rename is caught by the import rather
than by a user.

**The two exceptions**, both because the mapping is not configured yet or the
target is not ours:

1. **Inside the entity's own `__table_args__`** — at class-body time `.key` on a
   just-declared Column is not usable, so `Index('ix…', 'workspace_id')` uses
   literals (§4).
2. **A `ForeignKey` target** — `ForeignKey('workspace.id')` names another
   table's column, which may not be importable (§11.3).

## The same rule for dict payloads you invent — and ONE declaration only

A library also builds dicts that are NOT rows: an observer event payload, a
JSON column's inner shape, a params blob. Those keys are a contract with a
consumer and deserve one home. But **only the keys nothing else already owns.**

### If a name has an owner, use the owner. Do not re-declare it.

The entity IS the declaration, and `Entity.column.key` is how every layer reads
it — queries, migrations, row dicts, test assertions, and payloads. A payload
key that is a column is read the same way, at the call site:

```python
entry = {
    AssessmentScaleScore.normalized.key: score.normalized,   # the entity owns it
    AssessmentSubmission.submitted_at.key: _epoch(submission.submitted_at),
    'assessment_key': assessment.key,      # nothing owns this one -> enum
}
```

**Both of these are wrong, and they fail differently:**

```python
class ScoreKey(str, enum.Enum):
    NORMALIZED = 'normalized'                          # WRONG - a copy that DRIFTS
    NORMALIZED = AssessmentScaleScore.normalized.key   # WRONG - an ALIAS
```

The literal is the classic bug: rename the column and the payload silently
stops matching the table, with every test still green. The alias cannot drift —
which is why it survives review — but it is a **third handle for one string**.
Now three spellings exist and there is no rule saying which to use, so the next
person picks whichever they saw last. Redundancy in a NAME is how a codebase
grows three vocabularies for one concept.

Same for a JSON param a rule reads: if the entity declares
`AssessmentCompareRule.PARAM_CUTOFF = 'cutoff'`, a finding that echoes that
value back reports it under `PARAM_CUTOFF` — not under a `CompareInputKey.CUTOFF`
that merely points at it.

### What an enum in `constants/` is actually for

Only names **no entity owns**, AND only when there are enough of them to be a
SHAPE:

- composed names a payload invents — `a`, `b`, `delta`, `delta_seconds`
- a name qualified to disambiguate a flat payload — a `key` column emitted as
  `assessment_key` because the same dict already carries a `scale_key`

A healthy `constants/core_lib_constants.py` **imports no entity at all.** If it
needs one, the name it is declaring already has a home.

**A ONE-MEMBER enum is not a shape — use a plain module constant.** An enum
documents the shape of a payload; a single string has no shape to document, and
two one-member enums in one module managed to declare the *same* value twice
before anyone noticed.

**An enum that mirrors a METHOD SIGNATURE is not a declaration.** `@Observe`
builds its event value with `get_func_parameters_as_dict`, so the payload's keys
ARE the emitting method's parameter names — rename a parameter and the real key
moves while the enum keeps saying the old one. Worse, nothing outside the
library sees that dict: a listener ABC takes positional arguments, so the enum
documented a contract with nobody. Read it in the single internal unpacker and
say in a comment where the names come from.

**The test to apply to each enum**, in order — if any answer is no, it does not
belong here:

1. Does anything else already own these names (a column, an entity constant)?
2. Does a CONSUMER OUTSIDE the library actually read this dict?
3. Are there enough members that it describes a shape rather than a string?

Mixing in `str` means a member compares, hashes and JSON-encodes as its own
value, so a consumer may read a payload with either the member or the plain
string. Note `str(member)` does **not** — it yields `'PayloadKey.PROJECT_ID'`.
Use the member itself, or `.value`.

For a fixed set of keys inside one entity's JSON column, plain class constants
on that entity (`Entity.PARAM_MATRIX = 'matrix'`) are the right home — the
entity owns its own blob's shape. What is never fine is the same literal at
three call sites.

### Enforce it, do not just document it

A rename cannot catch an alias, and neither can any behavioural test — by
runtime a literal, an alias and the column are the same string. It has to be
checked in the SOURCE. Every core-lib should carry the equivalent of
`tests/test_constants_contract.py`: parse `constants/`, and fail if any enum
member is either a literal matching a known column/param name, or an expression
derived from an entity.

---

# Scaffolding skills — MANDATORY routing gate (do not skip)

Copy-paste-ready guides for building each part of a core-lib live under
[`skills/`](skills/). They are **tool-neutral** (plain Markdown with
`name` / `description` front-matter), so **any** AI agent can read and follow
them — there is exactly one copy, and this table is how you reach it.

**This is a hard rule, not a suggestion. Before you create or modify any
core-lib part in the table below, you MUST first load — open and follow — the
matching skill.** Loading is not a judgment call: match the row and load the
skill *before* writing code. Never write core-lib code from memory when a
matching skill exists. If more than one row matches (e.g. a new entity that
also needs a migration), load all that apply. For a brand-new library, load
`core-lib-new` first, then each per-part skill as you reach it.

| If you are about to… | You MUST first load |
|---|---|
| add or change an entity / table / model / column / nested enum | [`skills/core-lib-entity/SKILL.md`](skills/core-lib-entity/SKILL.md) |
| add or change a DataAccess / DAO / repository / query / get_by / list / filter | [`skills/core-lib-data-access/SKILL.md`](skills/core-lib-data-access/SKILL.md) |
| add or change a Service / business logic / public method / caching / invalidation | [`skills/core-lib-service/SKILL.md`](skills/core-lib-service/SKILL.md) |
| add or change an external client / provider / SDK / API integration / connection factory | [`skills/core-lib-connection/SKILL.md`](skills/core-lib-connection/SKILL.md) |
| add a migration / alter / create / drop a table, column, index, or constraint | [`skills/core-lib-migration/SKILL.md`](skills/core-lib-migration/SKILL.md) |
| add / fix / restructure tests or raise coverage | [`skills/core-lib-tests/SKILL.md`](skills/core-lib-tests/SKILL.md) |
| create / bootstrap a whole new core-lib from scratch | [`skills/core-lib-new/SKILL.md`](skills/core-lib-new/SKILL.md) |
| write ANY helper / utility / converter / guard / parser, or a `helpers.py` — **check what `core_lib` already ships first** | [`skills/core-lib-reuse/SKILL.md`](skills/core-lib-reuse/SKILL.md) |
| add / change / raise / catch any exception, error class, error code, or validation-failure type; pick an HTTP status | [`skills/core-lib-error-handling/SKILL.md`](skills/core-lib-error-handling/SKILL.md) |

**Adding a skill? This table is not the only place it must appear.** Add the row here AND in `core_lib_generator/template_core_lib/AGENTS.md`, which carries a convenience copy that every generated lib ships — a skill missing from that copy is one a generated lib is never told to load. (`core-lib-new` is the one deliberate omission: a generated lib already exists.)

---

# Core-Lib Rules — this library is AGNOSTIC

This package is a **standalone, product-agnostic library**. Treat it as if it
will be published on its own and dropped into any application that has never
heard of this project. It must know nothing about the host that consumes it.

## No host or product knowledge — anywhere

The name of the host application or product (its brand, its CLI, its env-var
prefix) must **NOT** appear **anywhere** in this library — not in source, not in
tests, not in comments, not in docstrings, not in field names, not in fixtures.

- This library reads **generic, library-owned** names (its own env vars / config
  keys) or — better — takes everything it needs through **constructor params /
  function arguments**.
- It NEVER reads a host-specific env var. The host owns its own config and
  **bridges** it: it passes the value in (a param) or exports it under the
  generic name this library reads.
- Product-specific TEXT (prompts, operator messages, workflow wording, brand
  strings) is **injected by the caller** as a parameter — never hardcoded here.
  Provide a safe, neutral default so the library works standalone.

## The library is the TOOL — never an instance of it

Agnosticism is not only about names. **A core-lib knows nothing about who uses
it, or what they use it for.** It ships the mechanism; every particular
configuration of that mechanism belongs to the caller.

This catches things the brand-name rule above lets through. A list like:

```python
NON_NEGOTIABLE_TOPICS = ['children', 'money', 'faith', 'location', 'timeline']
```

contains no product name and would pass the litmus test below — a stranger
could still use the package. It is still wrong. Those five topics are one
product's decision about one questionnaire. A library for scored assessments
has no opinion on whether "faith" is a topic, exactly as a charting library has
no opinion on which metrics you plot.

**The test that catches it: could a second, completely different customer use
this library for their own instrument without editing a single line of it?** If
adding a third of anything means editing library source, the library has
absorbed content that belongs to the host.

The tell is almost always a **branch, or a table, keyed on a specific
instance**:

```python
if key == FIVE_FACTOR_KEY:                 # <- the library now knows an
    return five_factor_definition(fields)  #    instrument by name
if key == NON_NEGOTIABLES_KEY:
    return non_negotiables_definition(fields)
raise ValueError('unknown built-in "{}"'.format(key))
```

Replace it with a **generic codec**: store the caller's configuration, hand it
back, and never look at what it means. Then a third instrument is a row in a
table, not a commit.

Concrete examples of content that must live OUTSIDE the library — in the host,
in `tests/`, or in `examples/`:

- Named instruments, questionnaires, templates, or presets
- Domain vocabularies (topic lists, category names, tag sets, status labels)
- Tuned magic numbers that encode a product judgement (a specific cutoff, a
  specific band boundary)
- Any "built-in", "default", or "starter" content shipped for convenience

Providing a *shape* is fine — `AnswerSetDefinition`, `bands`, a cutoff
**parameter**. Providing *the* answer set, *the* bands, or *the* cutoff is not.

A useful sanity check: a library's own `examples/` and `tests/` are where a
realistic, named configuration SHOULD live. It proves the mechanism works on a
real case without the mechanism knowing the case exists. If your flagship
example is importable from library source rather than from `tests/` or
`examples/`, that is the smell.

## Before writing a helper, check core-lib for it

The third form of the same mistake. A mirror type re-declares a shape; a
re-typed constant re-declares a name; a hand-rolled helper re-declares
BEHAVIOUR that already exists one package down — and this one hides best,
because the copy is usually thinner than the original and looks correct.

`result_to_dict` walks an entity's columns and converts enums to ints,
datetimes to epoch floats and Decimals to floats. A hand-written encoder that
"handles enums" passes a Decimal straight through — and every payload in the
library now goes out under two slightly different projections, one of which
nobody remembers exists.

Grep before you write. If core-lib does 80% of it, call it and add the 20%:

```python
encoded = result_to_dict(value)          # core-lib's job
return {k: v for k, v in encoded.items() if k not in _NOT_IN_A_TEMPLATE}
```

Do NOT assume the reverse exists. `result_to_dict` is encode-only; there is no
decoder, no argument-guard helper, no "get or None", and no transient-default
mixin. Writing those is right — say in the docstring that you checked, so the
next reader does not re-check.

**Full inventory: [`skills/core-lib-reuse/SKILL.md`](skills/core-lib-reuse/SKILL.md)** — every decorator and helper module `core_lib` ships, what it does NOT ship, and the traps in adopting `result_to_dict`. Load it before writing any helper. The three that bite most often:

- **A decorator usually already does it.** Before hand-writing a try/except or a conversion loop, check `@ResultToDict()`, `@NotFoundErrorHandler()`, `@DuplicateErrorHandler()`, `@Cache`, `@Observe`, `StatusCodeAssert`. A dict-building loop over `__table__.columns` IS `result_to_dict` with every conversion removed.
- **`@NotFoundErrorHandler()` is not a get-or-none.** It goes the other way — falsy result → raise 404 — and it is already on the CRUD bases' `get`. A service that returns `None` for an absent row swallows that 404 itself, and must catch **only** 404: a bare `except StatusCodeException:` also swallows a 409, turning a real answer into "not found".
- **`result_to_dict` only converts values INSIDE a structure.** `result_to_dict(a_datetime)` returns the datetime unchanged. Convert a hand-built dict by decorating the METHOD with `@ResultToDict()`, not by calling the function per field. (Then mind the str-enum key trap — §skills.)

## The entity IS the type. Do not mirror it in a second class.

The same rule as names, one level up: an entity already declares a shape, so
nothing else declares it again. A parallel `*Definition` / `*DTO` / `*Model`
dataclass that mirrors a table is the same duplication as a re-typed column
name, and costs more - now there are two classes, two field lists, and a
conversion layer whose only job is to move values between them.

```python
# WRONG - a second declaration of a shape the entity already owns
@dataclass
class ScaleDefinition:
    key: str
    name_key: str
    direction: Direction
    raw_min: Optional[int] = None
    ...          # every one of these is a column on AssessmentScale

def build_definition(rows): ...   # ~100 lines that exist ONLY to convert
```

Pass the entity. A detached SQLAlchemy instance reads its attributes fine after
its session closes, deep-copies, and pickles - so it works in a pure function,
in a cache, and in a test with no database. Verify those three for your session
config before assuming otherwise; they are the only things the mirror class
actually bought.

**The usual excuse and why it does not hold.** "The pure layer must not import
SQLAlchemy, so the arithmetic can be tested without a database." Check whether
it already imports the entity modules for their ENUMS - it almost always does,
so the boundary is already crossed and the mirror is buying nothing. The real
boundary worth keeping is *no session, no I/O*, and a detached instance honours
it.

**When a second type IS justified** - and say which in a docstring:

- It carries fields NO table has (a computed result, a comparison of two rows).
- It is a genuinely different shape: a tree, a union, several tables merged.
- It is a narrowing you must enforce - a caller may set these three columns and
  no others. Prefer the `RuleValidator` allow-list for that; it is the
  mechanism core-lib already provides.

A rename or a denormalisation is NOT a justification. `question_config_id` for
the entity's `id`, or `scale_key` for a resolved `scale_id`, is a property or a
join - not a reason to declare a whole second class.

**The check:** list the mirror's fields against the table's columns. If the
mirror adds nothing but `id` under another name, delete the mirror. If a
`build_*` / `to_*` / `from_*` function exists whose entire body is field-for-field
assignment, that function is the receipt.

**Audit BOTH directions, and count renames.** Two traps that hid real mirrors
for a whole review cycle each:

- Only the INPUT side got audited first. The result types - what a pure
  function RETURNS - were mirrors of the very rows the service then wrote them
  into, and the persist method was a field-for-field copy between them. Check
  what comes back, not just what goes in.
- The first audit asked "are the mirror's fields a subset of the columns?",
  which every renamed field defeats. `value` for `raw_value` and `points` for
  `points_raw` made a 3-of-3 mirror read as "no table has this shape". Map the
  renames first, THEN compare.

### Doing it without breaking things

Six things bite, in the order you will meet them. None is a reason not to do
it; all are cheap once you know.

**1. A transient entity has no defaults - and that is CORRECT. Do not "fix"
it.** A column's `default=` fires at INSERT, so an entity built in memory
carries `None` where the dataclass said `1`. The tempting move is a mixin that
applies each column's declared default at construction. Do not write one:

- Every row the library actually reads came from the database, so the default
  has already been applied. There is no production path that sees the `None`.
- `validate()` almost certainly already rejects the missing value - here it was
  `weight_not_whole: question 1 has weight None`. Substituting the default
  SILENCES that guard, so an author who omits a required value gets a silent
  `1` instead of an error.
- The only thing such a mixin fixes is test fixtures that left a required value
  out. That is a fixture bug wearing a library's clothes: set the value in the
  fixture, the way a real author would.

A mixin IS warranted for something a generated `__init__` cannot do at all -
letting an entity accept non-column attributes (its child collections) as
kwargs. Keep that narrow, and say in its docstring that it supplies no
defaults.

**2. Value equality is gone.** Dataclasses compare field by field; entities
compare by identity, so `a == b` on two separately built graphs is always
False. Any test asserting `built == restored` silently starts asserting
nothing. Compare the serialised form instead - that IS the contract.

**3. Child collections: attach them, do not declare a `relationship()`.** The
children are fetched with a soft-delete filter the ORM would not apply, and the
library never traverses them lazily. Plain attributes on the instance;
`__init__` must let them through as kwargs.

**4. Serialisation now walks further than you think.** `result_to_dict` follows
an entity's `__dict__`, so attached children come along - carrying `id`,
`assessment_id`, `created_at` and the soft-delete columns. If the output is a
TEMPLATE, filter that bookkeeping at EVERY depth, not just the top level.
A round-trip test cannot catch this: it decodes exactly what it encoded, so a
symmetric leak is invisible. Assert on the blob's contents directly.

**5. Renames break assignment silently.** `response.points = 5` on a dataclass
set a field; on an entity it creates a stray attribute nobody reads, and the
guard checking `points_raw` never fires. Grep for `.<old_name> =`, not just
reads.

**6. The codec gets SIMPLER afterwards - delete the dead half.** Once nothing
passed in is a dataclass, the `dataclasses.fields` / `typing.get_type_hints`
machinery is unreachable. Coverage will tell you; the encoder shrinks to
`result_to_dict` plus a filter, and the decoder to a column walk.

## An entity is DATA. core-lib is not Active Record.

An entity declares columns and nothing else: no query methods, no predicates,
no `@property` that derives an answer, no lookups over its own children. Put
those in the service layer.

```python
# WRONG - Active Record. The entity is answering questions about itself.
class Assessment(Base):
    scoring_mode = Column(IntEnum(ScoringMode), nullable=False)

    @property
    def is_categorical(self):
        return self.scoring_mode == ScoringMode.CATEGORICAL

    def scale(self, scale_key):
        return next((s for s in self.scales if s.key == scale_key), None)

# RIGHT - the entity holds the column, the service reads it.
def is_categorical(assessment) -> bool:
    return assessment.scoring_mode == ScoringMode.CATEGORICAL

def scale(assessment, scale_key):
    return next((s for s in assessment.scales or [] if s.key == scale_key), None)
```

**Why this is structural, not stylistic.** Every Service returns plain dicts
through `@ResultToDict` - that is the contract with a host. So a host NEVER
holds one of these objects. A method on an entity is therefore reachable only
from inside the library, by code that already sits in the service layer and
could have called a function. It buys nothing and costs the layering: `data/`
starts holding logic, and `service/` stops being the only place that knows how
a thing is interpreted.

It also drags the entity somewhere it must not go. `is_categorical` needs
`ScoringMode`; a lookup over children needs to know children exist. Soon the
entity imports half the domain, and `data/` - the layer everything else depends
on - depends back.

**The check:** open every file in `entities/`. `grep -c "def "` should be zero,
with no exception - not even an `__init__`.

If you need an entity to accept a NON-COLUMN kwarg (a child collection
attached when a row is read as part of a larger object), you do not need an
`__init__` for it. Declare it as a plain class attribute with a safe empty
default:

```python
class Thing(Base):
    id = Column(INTEGER, primary_key=True)
    children = ()          # not a column - a default, and a declaration
```

SQLAlchemy's declarative constructor accepts any kwarg for which
`hasattr(type(self), key)` holds, so `Thing(children=[...])` already works. A
mixin that pops those kwargs and re-sets them reimplements the base class.

**Where the logic goes.** The service layer, as plain functions taking the
entity as the first argument. If several services need them, one module owns
them; import the MODULE and qualify the call (`definition_loader.scale(...)`)
rather than the bare names, which collide with the local variables these
functions are usually assigned to.

## A DataAccess holds NO business logic. The RuleValidator does the checking.

A DataAccess assembles a payload and runs a query. It does not decide whether
its arguments are acceptable — that is a judgement about the operation, and the
operation belongs to a Service.

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

There is no corrected version of that method — the whole override goes (§5.1).
Each of the three moves somewhere that already exists:

| what it is | where it belongs |
|---|---|
| `require(x=x)` — an argument guard | the **Service** method that owns the operation |
| a domain rule (`must name one of A or B`) | **`validate()`**, at publish time |
| "must be an int / max length / a rule no column type carries" | the DataAccess's **`RuleValidator`** |
| "may not be null / must be present" | the **column** — `nullable=False` |

**One validator, and it is the one `CRUD.__init__` already took.** core-lib runs
that same list strictly on update and non-strictly on create, so a key with NO
rule reaches its column unchecked on the way in — which means an append-only
table whose allow-list is EMPTY validates nothing on the one path it uses.
Write the columns into that single list rather than adding a second
`create_rule_validator` (which could only run from inside an override you are
not allowed to write). Do not restate what the column already declares: the
database raises `IntegrityError` on a null `nullable=False` column by itself.

**Read methods take what they are given.** With the guard gone, a `None`
parent compiles to `IS NULL` and returns an empty list — never another
tenant's rows. The Service that called it has already guarded; a second check
in the DataAccess is a copy of a decision made one layer up.

**The check:** `grep -n "raise ValueError\|require(" data_layers/data_access/`
should return nothing but comments. A domain rule that is ALSO enforced in
`validate()` is not defence in depth — it is a second copy that can disagree.

## Every class declares what layer it is in

- Everything in `data_access/` extends **`DataAccess`** - including shared
  bases and mixins. That marker is what identifies a class which opens a
  session and returns rows, and a shared reader written as a bare `object` is
  the one thing in the folder not saying what it is.
- Everything in `service/` extends **`Service`**.
- A shared base sits ALONGSIDE the CRUD base rather than replacing it when its
  users need different CRUD behaviour (one carries a delete token, another does
  not). The MRO linearises cleanly with the marker resolving last:

      ThingChildDataAccess -> ChildDataAccess
                           -> CRUDSoftDeleteWithTokenDataAccess -> DataAccess

- The corollary: if a module under `service/` is not a Service, it does not
  belong there. `data_access/` and `service/` are layers, not folders to park
  things in.

## Minimal dependencies

- Import only **stdlib + third-party** packages. Do not import sibling libraries
  peer-to-peer; depend only on a declared shared base, if one exists.
- No compatibility shims, barrel files, or re-export-only modules — import from
  the real module. `__init__.py` files stay empty package markers; §2.1 owns the
  full rule.

## Self-contained and fully tested

- Tests live **inside this library**, never in a top-level/host test folder, and
  never importing host code or a host test package. A test in this library tests
  **only this library**.
- **100% coverage** — every public function, every input permutation.
- **One end-to-end flow test** (`test_flow.py`) driving the primary workflow A→Z
  against mocked I/O (`unittest.mock`; no network, no DB, no real subprocess).
- Fixtures use **generic example data** (`acme/widget`, `reviewer`, `PROJ-1`) —
  never product-flavored names.

## When a feature needs host-specific behavior

Do NOT reach back into the host. Add a **parameter** (constructor or function
arg) with a safe agnostic default, and let the host pass the value in. If you
find yourself typing the product/host name, a host env-var prefix, or
host-specific text in this library — stop, and inject it instead.

## The agnosticism litmus test

Two questions, and BOTH must pass. The first catches host names; the second
catches host *decisions*, which is the one that gets missed:

1. Could you publish this package as-is, with its tests, to a public registry
   and have a stranger use it without ever learning what application it came
   from?
2. Could that stranger build their OWN instrument, template, or preset on it
   without editing a line of library source? If "add a third one" means a
   commit here, the library is carrying content that is not its own.

If the answer to either is no, the fix is never to rename the offending thing.
Move it out: take it as a parameter, or let the caller store it and hand it
back. The library keeps the mechanism; the caller keeps the meaning.

---

## Repo-specific context

- If prompt-related code changes again, treat `core_lib/helpers/shell_utils.py` as the source of truth for exported names.
- Before mass-renaming prompt helpers, scan the repo with `rg` for both imports and call sites.
- Keep prompt helpers simple because this repo is checked by SonarCloud and small readability warnings can block PRs.
- **Read config directly; never defend it.** Access required config straight off the `DictConfig` by attribute — `conf.core_lib.<section>.<key>` (e.g. `conf.core_lib.extraction.ocr_languages`, `conf.core_lib.extraction.confidence_threshold`). Do NOT wrap config reads in `.get(section, {})`, `or {}`, `try/except`, or a default value. Missing/malformed config must fail loud at construction — a silent fallback to a default hides the misconfiguration and is strictly worse than crashing. The only thing allowed to wrap a config read is a pure type coercion of the read value (`float(...)`, `tuple(...)`) because env-sourced values arrive as strings / OmegaConf nodes — that is not a fallback. (One sanctioned exception: a connection-factory VALIDATION layer may read with `config.get(...)` because its whole job is to raise its own, better error for every missing key — see §10 of the recipe below.) Tests construct the lib with a real `OmegaConf.create({...})` and assert that an absent key raises `omegaconf.errors.OmegaConfBaseException`, not that it defaults.
- **Never commit `coverage.py` artifacts.** The `.coverage` SQLite file (and any `.coverage.*` parallel-run shards) is a local run artifact — it must never be tracked. If you run `coverage run`, delete the resulting `.coverage` before staging and confirm `git ls-files | grep '^\.coverage$'` is empty. Where a repo has coverage entries in `.gitignore` (the newer libs), keep them; add them when introducing coverage to a repo that lacks them. The `.coveragerc` config file IS tracked — only the data file is ignored.
---

# Building a new `*-core-lib` from scratch (canonical recipe)

This is how EVERY new core-lib in this workspace is built. It is distilled from the real libs — an older lib, an older lib, an older lib, an older lib, the reference lib, a newer lib — plus every correction the owner made while the reference lib was being brought up to standard. Follow it exactly. Every "small thing" here cost real debugging time or a review rejection.

**How to read this document:** the older libs predate several of the owner's newest rules; the reference lib is the most recently owner-reviewed lib and is the style reference wherever they disagree — UNLESS a bullet flags the reference lib itself as the divergence. Every known sibling divergence is flagged inline as **(divergence: …)** so that when you grep the siblings (as §0 tells you to) and find a contradiction, you know which side is canonical. If you find an UNFLAGGED contradiction, stop and ask — do not guess.

A core-lib is a composition root (`<Name>CoreLib(CoreLib)`) that wires **Services** over **DataAccess** over **entities**. Host apps touch ONLY the services exposed on the CoreLib. Dependencies point one way:

```
entities  ←  data_access  ←  service  ←  <Name>CoreLib  ←  host app / tests
```

Nothing to the right of an arrow is ever imported/called by anything to its left, and nothing skips a layer: a host or a test never calls a DataAccess; a DataAccess never calls a Service.

## 0. The meta-rule: never invent

**Before writing ANY line — file layout, decorator, helper, test idiom, naming — ask: "is this exactly how the existing core-libs do it?" If none of them does it, do NOT do it**, even if the new way seems better. The existing patterns are chosen for readability and debuggability: someone reading a failing test or a stack trace must recognize the shape instantly. Concrete inventions that were rejected in review, so you don't repeat them:

- `@property` accessors in tests that alias `self.lib.collection` as `self.service` / `self.collection_da` — rejected: "not easy to read and understand if something fails". Access is always inline and fully spelled: `self.foo_core_lib.collection.create(...)`.
- Naming the CoreLib handle `cls.lib` — rejected. It is the full lib name: `cls.foo_core_lib`, `cls.foo_core_lib`.
- Plural public service attributes (`self.documents`) — rejected. Singular, always (§1).
- A bespoke test harness that wires DataAccess + Services directly (a `library_harness.py`) — rejected: "everything comes from the core lib, this is final" (§13).
- Hand-rolled `session.add()`/`session.flush()` CRUD inside a DataAccess — rejected; CRUD bases only (§5).
- Vague variable names for composed parts — `storage = StorageDataAccess(...)` was rejected; it is `storage_data_access = StorageDataAccess(StorageConnectionFactory(storage_cfg))`. Name a variable what the thing IS.
- Defensive config reads (`storage_cfg.get('prefix_originals')`) in a composition root or service — rejected; direct attribute access, fail loud, and make sure the key ALWAYS exists in the yaml (§3). (The one sanctioned `.get(...)` site is a connection factory's validation layer — §10.)
- Standalone DB-DataAccess test files — rejected: "no one is exposing the DA; we only test what we expose, which is the service" (§13.3 — the backend *client adapter* test is the one sanctioned exception).

## 1. Naming (exact — no variation)

- Repo `foo-core-lib` → python package `foo_core_lib` → main class `FooCoreLib` in `foo_core_lib/foo_core_lib.py`.
- `foo_core_lib/__init__.py` carries `__version__ = '0.0.0.1'` and (current convention) re-exports the class: `from foo_core_lib.foo_core_lib import FooCoreLib` plus `__all__`. **(divergence: the older libs top-level `__init__.py` contain ONLY `__version__` — so `from foo_core_lib import FooCoreLib` does NOT work; always import from the module path `foo_core_lib.foo_core_lib` when consuming siblings.)** Every other `__init__.py` in the package tree is an EMPTY file (0 bytes) — but it must exist (`config/`, `data_layers/` and each subpackage, `migrations/`, `migrations/versions/`, `hydra_plugins/foo_core_lib/`, `tests/`, `tests/helpers/`, `tests/data/`).
- Constants in `foo_core_lib/constants.py` (current convention): the cache handler key `FOO_CORE_LIB_CACHE = 'foo_core_lib'` and (if the lib fires events) the observer key `FOO_CORE_LIB_NAME = 'FOO_CORE_LIB'`. **(divergence: an older lib uses `<name>_core_lib_constants.py`; an older lib uses `constants/core_lib_constants.py` with `CACHE = 'CACHE_CUSTOM_FIELD'`; an older lib’s key is `CACHE_WORKFLOW = 'WORKFLOW_CACHE'`. New libs use `constants.py` + the `FOO_CORE_LIB_CACHE = 'foo_core_lib'` name/value shape.)**
- Per domain object `Thing`: entity `Thing` in `data_layers/data/db/entities/thing.py` (`__tablename__ = 'thing'` — singular); DataAccess `ThingDataAccess` in `data_layers/data_access/thing_data_access.py`; service `ThingService` in `data_layers/service/thing_service.py`. One class per file. A non-persisted data type `ThingResult` goes in `data_layers/data/data_types/thing_result.py` — same one-class-per-file rule, and never under `service/` (§4.1). A pure engine/helper module under `service/` ends `_helper.py` — those two suffixes are the only ones that folder allows (§6.1). Anything error-shaped goes in `error_handling/<snake_case_class>.py`, one class per file (§4.2).
- **The public CoreLib attribute is the service class name minus `Service`, snake_case, SINGULAR:** `WorkspaceService → self.workspace`, `DocumentService → self.document`, `DocumentCollaboratorService → self.document_collaborator`. NEVER plural (`self.documents` is wrong and was explicitly rejected).
- The DataAccess instance is private: `self._thing_da` on the CoreLib (or a local variable in `__init__` if nothing else needs it — the older libs do that) and `self._thing_da` on the service that owns it. It is NEVER a public attribute.
- Cache key templates (current convention): `'<lib>_<entity>_{param}'`, e.g. `'foo_thing_{project_id}_{thing_id}'`, defined as module-level constants next to the service: `CACHE_KEY_DOCUMENT = '...'`. **(divergence: the older libs keys predate this scheme and live as class attributes — `CACHE_WORKFLOW_GET_{workflow_id}`, `custom_field_{id}`. New libs use the current convention’s shape.)**
- Index/constraint name constants on the entity: `INDEX_WORKSPACE_ID = 'ix_thing_workspace_id'` — `ix_<table>_<column>` for indexes (composite: `ix_<table>_<col1>_<col2>` or a meaningful pair name), `uq_<table>_<meaning>` for UNIQUE constraints (the current convention’s `INDEX_DOCUMENT_USER = 'uq_document_collaborator_doc_user'`). **(divergence: the older libs's older indexes use free-form literal names like `index_workflow_project_id` — old style, do not copy.)**
- Searchpath plugin: file `hydra_plugins/foo_core_lib/foo_core_lib_searchpath.py`, class `FooCoreLibSearchPathPlugin` (use the `...Plugin` suffix). **(divergence: the newest libs named theirs without the `Plugin` suffix; an older lib’s FILE is misnamed `*_sourcepath.py`. New libs: `_searchpath.py` file + `...SearchPathPlugin` class.)**
- Module-level tuning constants are SCREAMING_SNAKE at the top of the service module (`EMPTY_TRASH_BATCH = 10_000`, `VIEW_URL_EXPIRES_SECONDS = 900`); add a comment when the value isn't self-explanatory (the presigned-URL lifetimes carry one).

## 2. Folder tree (complete)

```
foo-core-lib/
  foo_core_lib/
    __init__.py                       # __version__ (+ newest style: re-export FooCoreLib)
    foo_core_lib.py                   # composition root
    constants.py                      # FOO_CORE_LIB_CACHE (+ FOO_CORE_LIB_NAME if events)
    config/
      __init__.py                     # REQUIRED, empty — pkg://foo_core_lib.config won't resolve without it
      foo_core_lib.yaml               # '# @package _global_', env-var driven (§3.1)
    error_handling/                   # ONLY if the lib defines its own errors (§4.2)
      __init__.py
      foo_error.py                    # the base: FooError(StatusCodeException)
      immutable_foo_error.py          # one class per file, named after the class
      validation_error.py             # error-shaped DATA lives here too, not in data_types/
    connections/                      # ONLY if the lib owns a non-DB backend (S3 etc.)
      __init__.py
      storage_connection_factory.py   # named after the BACKEND, no lib prefix (reference shape)
      storage_connection.py
    data_layers/
      __init__.py
      data/
        __init__.py
        data_types/                   # ONLY if the lib has non-persisted data types (§4.1)
          __init__.py
          thing_result.py             # one dataclass per file, named after the class
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
        storage_data_access.py        # backend verbs, if the lib has a backend (no lib prefix)
      service/
        __init__.py
        thing_service.py              # a Service class
        thing_helper.py               # a pure engine/helper — ONLY other allowed suffix (§6.1)
    observer/                         # ONLY if the lib fires events (the older libs shape)
      __init__.py
      foo_listener.py                 # FooListener(ABC) — host implements this
      foo_observer_listener.py        # FooObserverListener(ObserverListener) + EVENT_* keys
    jobs/                             # ONLY if the lib schedules background jobs
      __init__.py
      thing_due_job.py                # class ThingDueJob(Job) — file name matches the class
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
      .env                            # test env vars (DB sqlite :memory:, backend 127.0.0.1, …)
      config/
        config.yaml                   # defaults: [core_lib, foo_core_lib, (foo_core_lib_test | _self_)]
        foo_core_lib_test.yaml        # test-safe overrides, if the packaged yaml is not fully env-driven
      entities/                       # test-only stand-in entities (a test-only stand-in entity), if needed
    stub_<backend>.py                 # deterministic double for an uncontrollable backend, if needed
    test_thing_service.py             # ONE TestCase class per file
    test_foo_core_lib.py              # composed-lib smoke test (public surface only)
  core_lib_config.yaml                # repo-root compose — ONLY if the lib has install()/CLI entrypoints (stateless d2m has none)
  requirements.txt                    # RUNTIME deps only
  .coveragerc                         # if using coverage: source = foo_core_lib; omit migrations/*
  .gitignore                          # include .coverage / .coverage.* when coverage is used
  docker-compose-dev.yaml             # ONLY if the lib needs local infra (MinIO etc.)
```

**(divergence: an older lib’s test helper lives at `tests/utils/helpers.py` with holder class `FooCoreLibInstance` — directory/filename swapped. New libs use `tests/helpers/utils.py` + `CoreLibInstance`.)**

## 3. Config (Hydra) — the packaged yaml, the search path, the compose

### 3.1 `foo_core_lib/config/foo_core_lib.yaml`

- First line is exactly `# @package _global_`. Root key is `core_lib:`.
- **New libs source every value from an environment variable** with an in-yaml default — `${oc.env:FOO_<KEY>,<default>}`, nullable values defaulting to `null` — the style of the newer libs, which is the owner's latest direction. **(divergence: the older libs — the older libs — hardcode plain yaml values (`log_queries: false`, `create_db: false`, `protocol: postgresql`) and use bare `${oc.env:POSTGRES_*}` interpolations with NO defaults. Do not copy that for a new lib, and do not "fix" theirs while building yours.)**
- **Booleans and numbers sourced from env MUST be wrapped in `oc.decode`:** `${oc.decode:${oc.env:FOO_USE_SSL,true}}`. A bare `${oc.env:...}` resolves to a STRING — `'false'` is truthy — which silently breaks `create_engine(echo=…)`, makes `create_db` impossible to disable, and defeats `use_ssl is False` checks. This was a real shipped bug.
- **The DB block lives at the PATH `core_lib.data.sqlalchemy` — not anywhere else.** That exact path is what all DB libs share, and two framework pieces hard-code it: `CoreLib.connection_factory_registry.get_or_reg(cfg.core_lib.data.sqlalchemy)` and `Alembic.__init__`, which builds the migration URL from `core_lib.data.sqlalchemy.config.url`. The base `core_lib` group already supplies `_instance_key_: sqlalchemy_connection` and the `session` pool defaults via the config merge — your lib's yaml declares `_target_` and the keys it overrides. Shape for a NEW lib (env-driven; the older libs carry the same path + `_target_` but hardcode the values):

```yaml
# @package _global_
core_lib:
  data:
    sqlalchemy:
      _target_: core_lib.connection.sql_alchemy_connection_factory.SqlAlchemyConnectionFactory
      config:
        log_queries: ${oc.decode:${oc.env:FOO_DB_LOG_QUERIES,false}}
        create_db: ${oc.decode:${oc.env:FOO_DB_CREATE_DB,false}}
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

  (the reference lib currently keeps its DB block at `core_lib.data.db` and constructs the factory directly — that divergence breaks its `install()` because Alembic can't find the URL, **and the current convention’s yaml also lacks the `alembic.version_table` override, so it would fall back to the shared `alembic_version` table.** Do NOT copy either; `data.sqlalchemy` + a per-lib `version_table` is the contract.)
- `version_table` is ALWAYS overridden per lib: `task_alembic_version`, `workflow_alembic_version`, `custom_field_alembic_version` → yours is `foo_alembic_version`. Without it every lib fights over the shared `alembic_version` table in a shared database.
- Backend/domain sections follow the same env pattern (see the current convention’s storage block: `provider`, `region`, `bucket`, `endpoint_url`, `access_key`, `secret_key`, `use_ssl` (decoded), `addressing_style`, `prefix_originals`, `prefix_markdown`). If code reads a key, the key EXISTS in this yaml — code never `.get()`s around a missing key.
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

- `foo_core_lib/config/__init__.py` MUST exist (empty). Without it `pkg://foo_core_lib.config` is not an importable package in some environments and every compose that lists `- foo_core_lib` dies with `MissingConfigException: Could not load 'foo_core_lib'`. Most reference libs ship it; two were missing it and it cost a debugging session.
- `hydra_plugins/foo_core_lib/__init__.py` is also an empty required file.

### 3.3 Repo-root `core_lib_config.yaml` (install/CLI compose — only for libs with something to install)

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

**(divergence: some older root copies omit `_self_`, and one omits the `hydra:` block — that is the old shape. Match the canonical block and always include `_self_`.)** Optionally ship an install entrypoint like an older lib’s `app_workflow_core_lib_install.py`:

```python
@hydra.main(config_name='core_lib_config', version_base='1.1')
def main(cfg):
    FooCoreLib.install(cfg)
```

### 3.4 Composition rules that bite

- **NEVER compose another repo's config group in your defaults list** (`- other_core_lib`). Resolving `pkg://other_core_lib.config` from a sibling repo fails in some environments with `Could not load 'other_core_lib'`. If your lib composes another CoreLib and needs a section of its config (e.g. one lib needs another's `core_lib.<section>`), provide that section INLINE in your own yaml (and in the test `config.yaml` under `_self_`).
- When a compose file mixes a `defaults:` list with inline keys, the defaults list must contain `_self_` (otherwise hydra warns and the merge order is unspecified).
- The base `core_lib` group defines `core_lib.cache.memcached.url.host` as `${oc.env:MEMCACHED_HOST}` with NO default. OmegaConf interpolation is LAZY, so merely composing `- core_lib` works without the variable (the older libs test suites prove it) — it explodes only when something actually RESOLVES that node (an older lib’s constructor does, eagerly). Set `MEMCACHED_HOST=localhost` in the test `.env` whenever your lib (or a composed sibling) might touch the cache section — it is a one-line insurance against an `InterpolationResolutionError` that appears only at first access.

## 4. Entities (`data_layers/data/db/entities/thing.py`)

```python
import enum

from sqlalchemy import Column, VARCHAR, INTEGER, ForeignKey, JSON, Index, UniqueConstraint

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin
from core_lib.data_layers.data.db.sqlalchemy.types.int_enum import IntEnum


class ThingKind(enum.Enum):
    ALPHA = 1        # IntEnum-column enum values MUST start at 1 — never 0 (see §12)
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

- **Inside the entity class body, `Index`/`UniqueConstraint` columns are STRING literals** (`'workspace_id'`), exactly as above and in every real entity — at class-body time `.key` on a just-declared Column is not usable. The `Entity.col.key` referencing style belongs to MIGRATIONS and query/service code (§11.3), not to `__table_args__`. A unique constraint on a token-mixin entity looks like: `UniqueConstraint('document_id', 'user_id', 'deleted_at_token', name=INDEX_DOCUMENT_USER)` with `INDEX_DOCUMENT_USER = 'uq_document_collaborator_doc_user'`.
- **Mixin choice decides the DataAccess base** (§5). `SoftDeleteMixin` gives `created_at`/`updated_at`/`deleted_at` (all Python-side `default=`, no `server_default`, forced to the end of the table via `_creation_order`). `SoftDeleteTokenMixin` adds ONLY `deleted_at_token` (Integer, default 0) — **an entity used with `CRUDSoftDeleteWithTokenDataAccess` needs BOTH mixins** (`class X(Base, SoftDeleteMixin, SoftDeleteTokenMixin)`), because the token delete stamps both `deleted_at` and `deleted_at_token`.
- **Use the token mixin whenever the table carries a UNIQUE constraint over business columns.** The live-row marker is `deleted_at_token == 0`, so the unique constraint is declared over `(business_cols..., deleted_at_token)` — a soft-deleted row (token = deletion epoch) no longer collides with a re-created live row. **(divergence: the current convention’s `Workspace` has a unique `project_id` index with only `SoftDeleteMixin` — a delete-then-recreate on the same project collides with the dead row. Known latent gap; do not copy it into a new entity.)**
- **Every index and unique constraint gets a class-constant name** referenced from `__table_args__` AND from the migration — the name exists in exactly one place.
- **Any column with a `server_default` MUST also carry the matching Python `default=`** (`default=0, server_default='0'`). With only `server_default`, a freshly inserted ORM row holds `None` for the column until re-fetched — which surfaces as `None` through `@ResultToDict` and as `DetachedInstanceError` under lazy refresh. This was a real bug that hand-written fake-DA tests hid and the real composed stack exposed.
- VARCHAR lengths are always explicit (`VARCHAR(length=255)`, names get 512, keys/paths get 1024). Free text is `Text`. Dict payloads are `JSON` columns named `meta_data` (not `metadata` — that name collides with SQLAlchemy).
- FKs whose child rows must die with the parent declare it in the schema: `ForeignKey('document.id', ondelete='CASCADE')` (collaborators/favorites die with their document — `empty_trash` relies on it).
- The enum class lives in the SAME file as its entity, right above it.
- Derive enum-based strings from the member NAME, not the value: a file extension is `f'.{kind.name.lower()}'` — using `.value` after an IntEnum conversion produced the literal extension `.1` in production code. Real bug.

### 4.0 An entity is where agnosticism is usually lost

The agnosticism rules at the top of this document are enforced or broken HERE, because an entity is where a vocabulary gets written down and a schema is the hardest thing to walk back. Two forms, both of which pass the brand-name check:

**A column whose MEANING is the host's is an opaque scalar. Store it; never read it.**

```python
cadence = Column(IntEnum(Cadence))    # ⛔ WEEKLY/MONTHLY/QUARTERLY — one product's schedule
cadence = Column(INTEGER)             # ✅ opaque; the host defines the value AND owns the scheduling
```

The enum version forces every host onto the three intervals whoever wrote it happened to need, and the moment the library owns those members something will eventually branch on them. Take the value, persist it, hand it back. Say so in the docstring — *"`cadence` is OPAQUE to this library. The host defines the meaning of the value and owns all scheduling; nothing here reads it or branches on it. Do not add logic keyed on its value, and do not reintroduce an enum."* — because the next author's instinct is to "improve" the INTEGER into an enum. **The check: `grep -rn "<column>" ` outside the entity and the migration returns only the create/read payload, never a comparison.**

An enum is right when the LIBRARY branches on the member (`ScoringMode.WEIGHTED_AVG` selects an algorithm this library implements). It is wrong when the library only stores and returns it.

**An enum the library does branch on still must not carry one product's vocabulary.** Name members for the mechanism, not for the instance that prompted them: `Measures.STATE`/`TRAIT` is a property of assessments in general; a member named after one questionnaire's category is that questionnaire leaking into the schema. Ask of every member: would a completely different customer's instrument use this word? If it names *their* thing rather than *a kind of* thing, it belongs in the host's data — a row they store — not in a class here.

Both are the "library is the TOOL, never an instance of it" rule applied to a schema. Neither contains a product name, so only the SECOND litmus question catches them.

### 4.1 Non-persisted data types live in `data_layers/data/data_types/`, NOT in `service/`

First reach for an ENTITY — most "result"/"input"/"node" types are one already, and a dataclass mirroring an entity field-for-field is the duplication rule at the top of this section. But some data genuinely has no table: what a pure engine returns, an aggregate of several entity lists plus computed fields, one validation error. Those are still **data**, and `data_layers/data/` is the data layer:

```
data_layers/
  data/
    data_types/
      __init__.py
      assessment_result.py      # @dataclass AssessmentResult  — what score() returns
      compare_result.py         # @dataclass CompareResult     — one finding
  service/
    scorer_service.py           # the LOGIC that produces them
```

`service/` holds services and the pure engines they call — behaviour, not type declarations. A `@dataclass` under `service/` is a data type filed under the logic layer; move it. The check: **`grep -rn "@dataclass" data_layers/service/` returns nothing.**

- One class per file, file named after the class in snake_case — same rule as entities.
- Dependency direction is one-way: a data type may import entities and other data types, **never a service, DataAccess or engine.** That is what keeps it importable from any layer without a cycle.
- The folder is conditional — a lib whose services only ever return entities doesn't create it.
- Related exception (§A2): a *spec* — a frozen-dataclass DSL a consumer module reads as configuration — stays owned by that consumer module. `data_types/` is for types that flow through the layers, not for a module's private authoring DSL.
- **`error_handling/` beats `data_types/`** — anything error-shaped goes there even when it is a plain `@dataclass` (§4.2). "It is a dataclass, not an exception" is not the test; what the type IS, is.

### 4.2 Everything error-shaped lives in `error_handling/`, one class per file

`core_lib/error_handling/` is the pattern — `status_code_exception.py`, `core_lib_init_exception.py`, one class per file named after the class. Copy that shape; there is no `errors.py` grab-bag. **The check: `grep -c "^class " error_handling/*.py` prints `1` for every file.**

The scope is "error-shaped", not "is an exception". A `ValidationError(code, message)` that `validate()` RETURNS in a list and never raises still lives here, because it is the library's error vocabulary and is exactly what the matching exception carries (`AssessmentValidationError.errors` is a `List[ValidationError]`). Filing it under `data_types/` splits one concept across two packages and hides that the pair belongs together.

Every exception subclasses a lib base which subclasses core-lib's `StatusCodeException`, with the status as a **class attribute, never a constructor argument** and **never defaulted**:

```python
class FooError(StatusCodeException):
    STATUS_CODE = None                       # a default is a trap — see below
    def __init__(self, *args):
        super().__init__(self.STATUS_CODE, *args)
```

- A host maps any of them by reading `error.status_code`, without importing your classes. A bare `Exception` forces every consumer to keep its own mapping table in step with your package.
- Each subclass names ONE situation that always means the same thing to a client, so the code belongs to the class and no raise site can get it wrong.
- Not defaulting `STATUS_CODE` is deliberate: a default means a new error type silently inherits whatever the last one used and is reported as something it is not.
- The docstring says WHY that status (422 = well-formed but unprocessable content, the client shows it to the author; 409 = the request is fine, the STORED state forbids it), which is the part a reviewer cannot re-derive.
- Test by WALKING the package (`pkgutil.iter_modules`), not by scanning one namespace — one class per file means a new error is a new module, and a module nothing imports yet would be invisible.

Full recipe, the status-choice table and the test: [`skills/core-lib-error-handling/SKILL.md`](skills/core-lib-error-handling/SKILL.md).

### 4.3 A column name is NEVER a string literal — anywhere, in any container

The entity owns the name. Every other mention reads it back with `Entity.column.key`, so a rename either propagates or fails at import. This is stated elsewhere for queries (§5) and for dict reads (§13) — but the rule is **not** scoped to those. It covers every form a name can take:

```python
# ⛔ every one of these is the same bug
_NOT_IN_A_TEMPLATE = frozenset({'id', 'project_id', 'published_at'})   # a set
_VERSION_FIELD = 'version'                                            # a constant
SORT_COLUMNS = ('created_at', 'name')                                 # a tuple
if key == 'assessment_id': ...                                        # a comparison
payload.pop('deleted_at', None)                                       # an argument

# ✅
_NOT_IN_A_TEMPLATE = frozenset({
    Assessment.id.key, Assessment.project_id.key, Assessment.published_at.key,
})
```

**Why a set of names is the WORST place to write them as literals.** A stale literal in a query usually explodes — SQLAlchemy raises on an unknown attribute. A stale literal in a *filter set* does nothing at all: the name simply stops matching, so the column is no longer excluded. In the real case that prompted this rule, `_NOT_IN_A_TEMPLATE` listed the bookkeeping columns to strip out of a shared catalogue blob; renaming any of them would have silently started shipping a tenant's `project_id` inside every host's template. The rename compiles, the suite stays green, and the leak is invisible.

Which entity to name when several share a column: the one whose row you are actually describing. `id`, `created_at`, `updated_at`, `deleted_at` and `deleted_at_token` come from the base and the mixins, so any entity in the set can stand for all of them — say so in a comment. A column only a CHILD has (`assessment_id`) must be named off that child, not off the parent.

**The two exceptions, and only these two:**

- **Entity declarations.** A column's own name in `Column(...)`, and the strings inside `__table_args__` (`Index('...', 'workspace_id')`) — at class-body time `.key` on a just-declared Column is not usable, and these DECLARE the name rather than reference it (§4).
- **Migrations.** They pin historical DDL and must not drift with the entity (§11.3).

**Test it by walking the library's own AST** — a grep cannot tell a column name from any other string, and the rule is unenforceable by review alone once names appear in sets and constants:

```python
columns = {c.key for entity in every_entity() for c in entity.__table__.columns}
for path in library_sources():          # excluding entities/ and migrations/
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Constant) and node.value in columns:
            offenders.append(...)
```

Pair it with a "would this catch a planted literal?" test, or an empty offender list silently means the walk stopped working.

## 5. DataAccess (`data_layers/data_access/thing_data_access.py`)

**MUST subclass a core-lib CRUD base. Hand-rolled `session.add()` / `session.flush()` / bespoke get/update/delete loops are rejected in review.** Pick by delete semantics — note the module FILENAMES are not guessable from the class names:

| Base class | import from | get filter | delete does | use when |
|---|---|---|---|---|
| `CRUDDataAccess` | `core_lib.data_layers.data_access.db.crud.crud_data_access` | `id` (404 if missing) | HARD delete, returns rowcount | rows may really vanish |
| `CRUDSoftDeleteDataAccess` | `core_lib.data_layers.data_access.db.crud.crud_soft_data_access` | `id AND deleted_at IS NULL` | stamps `deleted_at=utcnow()`, returns rowcount | normal soft delete |
| `CRUDSoftDeleteWithTokenDataAccess` | `core_lib.data_layers.data_access.db.crud.crud_soft_delete_token_data_access` | `id AND deleted_at_token == 0` | stamps `deleted_at` + `deleted_at_token=epoch`, returns rowcount | soft delete + unique constraints |

Canonical shape (the current convention’s `WorkspaceDataAccess`) with the exact imports:

```python
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_soft_data_access import CRUDSoftDeleteDataAccess
from core_lib.rule_validator.rule_validator import RuleValidator, ValueRuleValidator

from foo_core_lib.data_layers.data.db.entities.workspace import Workspace

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
```

That is the WHOLE class — domain queries aside, there is nothing else to write. **There is no `create`.** See §5.1.

Rules:

- The `rule_validator` (module-level, next to the class) is the allow-list: one `ValueRuleValidator(Entity.col.key, type, custom_validator=...)` per column. Anything not listed is rejected under strict mode with `PermissionError` (§12 for exact semantics).
- **Do not override `create`** — §5.1. `CRUD.create(data: dict)` plus the `rule_validator` above already IS the write API.
- `update` overrides guard immutable columns (strip `project_id`/FKs from the payload) before `super().update(id, data)`.
- Domain queries (`get_by_project`, `full_text_search`, `list_trash`, `search_by_name`, …) live on the DataAccess, written in the query-builder style the other DAs use (`session.query(Entity).filter(...).all()` chains). Do NOT refactor an existing DA's access pattern to a different style — that exact change was rejected in review.
- Normal update paths validate STRICT (the base's plain `validate_dict(data)` — unknown key raises `PermissionError`; tests rely on that). For a PARTIAL metadata-style bulk update where callers may pass a superset dict, use `self._rule_validator.validate_dict(data, strict_mode=False, strict_output=True)` (unknown keys silently DROPPED) and `session.query(...).update(validated, synchronize_session=False)` — `synchronize_session=False` avoids `InvalidRequestError: Invalid expression type` on bulk updates. Library uses the strict form on 2 of 3 update paths and the lenient form only on `DocumentDataAccess.update_metadata` — default to strict.
- Column references in queries/payloads are `Entity.col.key` / `Entity.col` — never string literals. Same for a name in ANY other position: a set, tuple, constant, comparison or argument (§4.3).
- Cross-entity guards live in module-level helpers inside the DA file (the current convention’s `_assert_collection_in_workspace(session, workspace_id, collection_id)` raising `StatusCodeException(404)`), called inside `create`/`update` before writing.
- Errors: DA-level argument guards raise `ValueError`; base-CRUD arg guards are bare `assert` (so `AssertionError`); "not found" on `get` is `StatusCodeException(404)` raised by the base's `@NotFoundErrorHandler()`; uniqueness violations bubble up as `sqlalchemy.exc.IntegrityError` for the service's `@DuplicateErrorHandler` to map.
- **A DB DataAccess is only ever called BY a Service.** Never from a host app, never from a test, never from another lib. (The backend adapter DA — storage — additionally gets its own mocked-client unit file; §13.3.)

### 5.1 Never override `create`. The base plus its RuleValidator IS the write API.

`CRUD.create(data: dict)` already validates through `self._rule_validator` and inserts. A subclass `create` can only do one of three things, and all three are wrong:

```python
# ⛔ ALL THREE ARE REJECTED
def create(self, project_id: int, name: str):
    if not (project_id and name):                    # (1) business logic in a DataAccess
        raise ValueError('create requires ...')
    return super().create(create_rule_validator.validate_dict({   # (2) a SECOND validator
        Workspace.project_id.key: project_id,        # (3) repacking args into the dict
        Workspace.name.key: name,                    #     the base already accepts
    }))
```

1. **Guarding arguments is business logic**, and business logic is the service's. A DataAccess does not check what it is handed — the RuleValidator does.
2. **A second `RuleValidator` beside the first has nowhere to be used.** `CRUD` takes exactly one, in `__init__`, and runs it on both write paths. A `create_rule_validator` can only run from inside an override — so it exists solely to justify the override.
3. **Repacking positional args into a dict** buys nothing: `create(data: dict)` took a dict already. It only means every call site has to be rewritten when a column is added.

The call site passes the whole payload, keyed by `Entity.col.key`:

```python
workspace = self._workspace_da.create({
    Workspace.project_id.key: project_id,
    Workspace.name.key: name,
})
```

**And do not write a create allow-list that restates the schema.** `ValueRuleValidator(Workspace.project_id.key, int, nullable=False)` beside `Column(INTEGER, nullable=False)` is the same fact in two files that drift apart. The database enforces presence, nullability and length itself — a null identity column raises `IntegrityError` at flush, in sqlite as well as Postgres. Declare in the RuleValidator only what the schema **cannot** express: a Python type a permissive DB would coerce, or a `custom_validator` encoding a rule no column type carries.

**Know what create does NOT check.** The two paths differ, and the difference decides what belongs in the list:

```
update(id, data)  -> validate_dict(data)                     strict:     unknown key raises
create(data)      -> validate_dict(data, strict_mode=False)  NOT strict: unknown key passes through
```

So on an append-only table, an allow-list left empty to mean "nothing may ever be updated" also means **create validates nothing at all** — every value reaches its column unchecked on the one path that table actually uses. One list serves both paths; write the columns into it and let immutability be a property of the service surface (no service method issues that update) rather than of an empty list. Assert that with a test over the public API, not by overriding `update` to raise — that is business logic in a DataAccess again.

## 6. Services (`data_layers/service/thing_service.py`)

Every service SUBCLASSES the core-lib base: `from core_lib.data_layers.service.service import Service` → `class ThingService(Service):` — all reference services do. Stateless. `__init__(self, thing_da: ThingDataAccess, ...)` stores `self._thing_da` plus any sibling services it depends on (services may depend on services; they never reach into a sibling's DA).

Decorator stacks — copy these orders exactly (the current convention’s `WorkspaceService`/`DocumentService`):

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
- A write that must also evict a key templated on DIFFERENT params uses the empty-body eviction-hook pattern: a private method decorated `@Cache(OTHER_KEY, handler_name=..., invalidate=True)` whose body is `pass`; the real write calls it with the params that fill the template (the current convention’s `_invalidate_project_mapping(project_id)` called by `delete`).
- **Tenant-boundary discipline:** the external tenant key (`project_id`) is translated to the internal row key (`workspace_id`) in exactly one place — a `resolve_<x>_id(project_id)` (cached read that raises a domain `LookupError` subclass when absent) and/or an idempotent `ensure_<x>(project_id, ...)` get-or-create that recovers from a concurrent-create 409 by re-reading. Every other service method takes `project_id`, resolves it internally, and scopes ALL queries by the internal id — a cross-tenant call is a 0-rowcount/`None`/404, never a leak.
- Missing required args raise `ValueError` at the top of the method. Mutations return the affected rowcount so a caller can detect a no-op (missing row / cross-tenant) without an extra read. Getters return `None` for absent (swallowing the DA's 404); "payload builder" methods that must exist raise `StatusCodeException(HTTPStatus.NOT_FOUND, ...)` themselves.
- **A row's PARENT can be soft-deleted too, and that is still an absence.** Swallowing the 404 on the row you asked for is only half of it: a read that walks stored children and resolves each one's parent hits rows whose parent went away after they were written, and it must skip rather than raise. Get this wrong on ONE method and the surface becomes incoherent — in the case that prompted this rule, `history`, `scores`, `latest_per_scale` and `compare_pair` all returned empty on a soft-deleted parent while `result_for` raised a `ValueError` from a PURE ENGINE's argument guard, so the caller got an error naming a parameter rather than the record. Swallow only 404 (a helper like `row_or_none(get, row_id)` at the library root, since a DataAccess needs it too) — catching the base `StatusCodeException` turns a 409 into a silent "not found".
- Services return plain dicts (via `@ResultToDict`) — a host app or test reads fields as `row[Thing.name.key]`. Enum columns arrive as their INT VALUE, datetimes as epoch floats (§12).
- Pure derivations (key builders, slugs, content types) are module-level `_helpers` at the bottom of the service file — testable without the CoreLib.
- Batch loops that delete/purge use a module-level batch constant (`EMPTY_TRASH_BATCH = 10_000`) so tests can patch the MODULE GLOBAL (allowed) instead of internals (forbidden).

### 6.1 Every file in `service/` ends `_service.py` or `_helper.py`. Nothing else.

Open `data_layers/service/` and you should be able to tell, from the filenames alone, what each module is. Two suffixes, and only two:

| suffix | what it is |
|---|---|
| `thing_service.py` | a `Service` subclass — holds DataAccesses, decorated, part of the public surface |
| `thing_helper.py` | a pure engine or helper — module-level functions, no DataAccess, no I/O, called BY a service |

A bare noun — `comparer.py`, `validator.py`, `definition_loader.py` — tells a reader nothing about which of the two it is, and they had to open each file to find out. Rename to `comparer_helper.py`, `validator_helper.py`, `definition_loader_helper.py`. Keep the whole original name and append the suffix: `definition_loader_helper.py`, not `definition_helper.py` — a convention applied to two of three files is not a convention, and dropping a word to make it read better loses what the module actually is.

**The check: `ls data_layers/service/*.py` shows only `*_service.py` and `*_helper.py`** (plus `__init__.py`).

Corollaries, each of which sends a file OUT of this folder rather than renaming it:

- A `@dataclass` is neither — it is a data type (§4.1) or, if error-shaped, an error (§4.2).
- A helper several LIBS would want is not lib-local at all — check `core_lib` first (`skills/core-lib-reuse`).
- A cross-layer helper a DataAccess also needs goes at the LIBRARY ROOT (`foo_core_lib/helpers.py`), not here: importing it from `service/` would invert the layer dependency.
- Small pure derivations used by exactly one service (key builders, slugs) stay as module-level `_private` functions at the bottom of that service file — a `_helper.py` module is for a body of logic with its own name, not for two three-line functions.

Imports of a helper module are qualified — `import definition_loader_helper` then `definition_loader_helper.scale(...)` — not `from ... import scale`, because the bare names collide with the local variables these functions are usually assigned to.

### 6.2 A function that REPORTS problems may never raise on the input it judges

`validate()` returns a list of `ValidationError` (§4.2) and the caller turns a non-empty list into a 422. So anything it raises instead is a **500 naming no field** — and these functions are usually exposed precisely so an author can run them on a HALF-FINISHED object, which is the input most likely to break them.

Two shapes cause it, and both are guarded ONCE at the top of the module rather than re-checked per rule:

- **A value another rule already reported as missing.** A rule that reports `min` is absent and carries on leaves every later rule doing arithmetic against `None`. Guard the whole precondition (`_has_range()` checking BOTH bounds), not the one bound whose absence you happened to hit first.
- **A JSON column.** It holds a HOST-authored blob and can be a list, a dict, a string or null; every rule that walks it with `option.get(...)` is an `AttributeError` on a bare string and a `TypeError` on `None`. Report the SHAPE once as its own error code (`malformed_options`) and have the per-item rules skip a blob they cannot read. Do not "fix" it by summing with `or 0` — `'x' or 0` is `'x'`, and the sum raises anyway.

Do not paper over this by making callers catch. The check: feed `validate()` a half-declared object and every wrong-typed blob you can think of, and assert it RETURNS for each.

### 6.3 An invariant guarded on one write path is guarded on none

If two paths can set the same column, the bound belongs on both — a publish-time validator does not protect a submit-time path that writes the column directly. In the case that prompted this rule, the validator bounded a configured point value to the declared range, with its own message reading "nothing downstream bounds this"; a second path let a privileged caller supply the number directly, unbounded, and a typed `55` on a `1..5` range stored a normalized `1350`. The table was append-only, so nothing could correct it afterwards.

Ask it as a question, per invariant: **which paths can write this column, and does each one enforce it?** Being the privileged/trusted path is not an answer — a trusted caller still typos.

## 7. Composition root (`foo_core_lib.py`)

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

- Note the Alembic import: **`from core_lib.alembic.alembic import Alembic`** — the class lives in the `alembic.alembic` module (`core_lib/alembic/__init__.py` is empty; the shorter path does not import).
- Order inside `__init__`: `super().__init__()` → `self.config = conf` → guarded registry registrations → connection factory → DAs → services (dependency order — a service that needs `self.workspace` is built after it).
- **DB connection via `CoreLib.connection_factory_registry.get_or_reg(core_cfg.data.sqlalchemy)`** — the registry dedupes on `_instance_key_`, so a host composing several core-libs over one database shares ONE engine, and the test helpers can reach that same engine. **Alembic is NOT part of that sharing** — `Alembic.__init__` builds its OWN engine directly from `core_lib.data.sqlalchemy.config.url`; what it shares with the factory is only the config PATH. (For sqlite `:memory:` that means two engines = two separate databases — exactly why an older lib’s test helper pre-creates tables on the FACTORY engine, §13.4.)
- **Every registry registration is guarded** (`if not CoreLib.cache_registry.get(KEY): register(...)`) — the registries are process-global and `DefaultRegistry.register` RAISES `ValueError` on a duplicate key, so an unguarded register makes the second CoreLib construction in a process (tests; multi-lib hosts) explode. **(divergence: an older lib registers unguarded — the bug pattern, not the convention.)**
- Cache handler choice: `CacheHandlerRam()` for a lib whose cache is per-process, or `instantiate_config(core_cfg.cache.foo)` / `CacheHandlerMemcached(build_url(**core_cfg.cache.foo.url))` when production needs a shared cache. Either way, registered under the ONE `FOO_CORE_LIB_CACHE` constant that every `@Cache(handler_name=...)` in the lib names.
- Composing another CoreLib: construct it with the SAME conf (`self.doc_to_markdown = DocToMarkdownCoreLib(conf)`), expose the piece services need as an attribute (`self.markdown_extractor = self.doc_to_markdown.document`), and pass that into your services. Host-extension hooks are explicit pass-through methods (`def register_extractor(self, extractor: Extractor): self.doc_to_markdown.document.register(extractor)`) — hosts never reach through the composition.
- `install`/`uninstall` staticmethods exactly as above (the `os.path.dirname(inspect.getfile(FooCoreLib))` argument is how Alembic finds `data_layers/data/db/migrations` — §11). Workflow additionally ships `downgrade(cfg)` → `.downgrade("-1")` (one step back) and `create_migration(cfg, name)` statics — copy those when the lib will evolve its schema.
- A stateless lib (no DB) is the same skeleton minus DB/DAs/migrations/`core_lib_config.yaml`: `EmailCoreLib` is `super().__init__()`, `self.config = conf`, `self.mail_client = instantiate_config(self.config.core_lib.email_core_lib.client)`, and public methods that delegate to the client. `DocToMarkdownCoreLib` reads its config directly with pure coercions (`float(...)`, `tuple(...)`) and exposes `self.document`.

## 8. Observers / events (when a host must react to what the lib does)

Follow the older libs exactly (three pieces + wiring):

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

3. In the composition root: a private `Observer`, a GUARDED registry registration under `FOO_CORE_LIB_NAME`, and a typed attach method **named after the domain** (never shadow the base `CoreLib.attach_listener` — **divergence: an older lib shadows it; the older libs's `attach_task_listener`/`attach_workflow_listener` are the convention**):

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

**Contract that bites:** `Observer.notify` catches, logs, and then RE-RAISES a listener's exception. `@Observe` fires AFTER the wrapped function body ran — so a host listener that throws makes the service method raise even though the DB write already committed. Listeners must be defensive (swallow their own errors) unless they intend to fail the service call.

## 9. Jobs (scheduled background work)

- `jobs/thing_due_job.py` (file name matches the class, snake_cased):

```python
class ThingDueJob(Job):
    def initialized(self, data_handler: FooCoreLib):
        assert data_handler and isinstance(data_handler, FooCoreLib)
        self._foo_core_lib = data_handler

    def run(self):
        self._foo_core_lib.thing.notify_overdue_things()
```

- Yaml under the lib's own section (the `_target_` module path must match the real file):

```yaml
  foo_core_lib:
    jobs:
      thing_due:
        initial_delay: startup        # 'boot'/'startup' → runs immediately; else a pytimeparse duration
        frequency: 1d                 # omit for a one-shot job
        handler:
          _target_: foo_core_lib.jobs.thing_due_job.ThingDueJob
```

- Wire in `__init__` (after the services exist): `self.load_jobs(self.config.core_lib.foo_core_lib.jobs, {'thing_due': self})` — the dict maps job name → the `data_handler` passed to `initialized` (one lib passes the whole CoreLib; an older lib passes the one service it needs).
- `initial_delay` is MANDATORY (`load_jobs` raises `ValueError` when falsy). A job that is also a `CoreLibListener` is auto-attached.
- **Test consequence:** a `startup` job queries its table the moment `start_core_lib()` runs — before any test created rows. The test helper must then pre-create tables on the FACTORY engine AND run `install()` before `start_core_lib()` (an older lib’s helper, §13.4). A lib with no startup jobs skips both.

## 10. Non-DB backends (object storage etc.) — the `connections/` pattern

Three pieces, mirroring the DB stack (the current convention’s storage is the reference; the files are named after the BACKEND, with no lib prefix — `storage_connection_factory.py`, `storage_connection.py`, `storage_data_access.py`):

1. **`connections/storage_connection_factory.py`** — `class StorageConnectionFactory(ConnectionFactory)`. Validates EVERY required config key in `__init__` with a dedicated error type (`class StorageConnectionError(ValueError)`) BEFORE building anything — including pairwise rules (`access_key` and `secret_key` both-or-neither). **This validation layer is the ONE sanctioned `.get(...)` site:** it reads each key with `config.get('bucket')` etc. and raises its own explicit, named error — strictly louder and clearer than an attribute crash, which is the point of the no-defensive-reads rule. Builds the client once; `get()` returns a fresh thin `StorageConnection(self._client)`.
   **The heavy SDK import is LAZY** — `import boto3` is the first line INSIDE the `_build_client` staticmethod, never at module top. That keeps the SDK an optional dependency: the lib imports, config-validation tests run, and only actually connecting requires it installed. Consequently `boto3` is NOT in `requirements.txt`.
2. **`connections/storage_connection.py`** — lifecycle only: `__enter__` returns the raw client, `__exit__` does nothing. No verbs here.
3. **`data_layers/data_access/storage_data_access.py`** — `class StorageDataAccess(DataAccess)` owns ALL the verbs (`put`, `get`, `delete`, `exists`, `list` with pagination, `presigned_url`), each opening `with self._factory.get() as client:`. Returns small dataclasses (`StorageObject(key, size, etag)`), not raw SDK responses.

In the composition root the naming is literal: `storage_data_access = StorageDataAccess(StorageConnectionFactory(storage_cfg))` — the variable is named what it is (a bare `storage = ...` was rejected). Key-naming policy (prefixes like `originals/`/`markdown/`) is NOT a connection concern — it lives on the service that owns the keys, passed in as constructor args read from config.

Provider quirks are absorbed in the factory (`provider: minio` + `addressing_style: auto` → `path`). Ship `docker-compose-dev.yaml` with the real local backend (MinIO server + healthcheck + an `mc` one-shot that creates the bucket `--ignore-existing`) so `docker compose -f docker-compose-dev.yaml up -d` gives a working backend with documented stable credentials.

## 11. Migrations — exact conventions (this section was rewritten three times in review; every detail matters)

### 11.1 How Alembic is wired (no alembic.ini exists, anywhere)

`Alembic(core_lib_path, cfg)` — imported as `from core_lib.alembic.alembic import Alembic` — builds the alembic `Config()` IN MEMORY from the yaml node `core_lib.alembic` (base group provides: `script_location: data_layers/data/db/migrations`, `file_template: "%%(year)d-%%(month).2d-%%(day).2d_%%(rev)s_%%(slug)s"`, `version_file_name: '.migration_ver'`, `render_as_batch: false`, `version_table: alembic_version` — which your lib yaml overrides to `foo_alembic_version`). `script_location` is resolved relative to `core_lib_path` = `os.path.dirname(inspect.getfile(FooCoreLib))`, and the DB URL is built from `core_lib.data.sqlalchemy.config.url` — which is WHY the DB block must live at that exact path (§3.1). **Alembic creates its own engine from that URL** (it does not use the connection-factory registry). Migrations run through `EnvironmentContext` directly; `env.py` is stock boilerplate that is effectively bypassed — copy `env.py` and `script.py.mako` verbatim from a sibling lib and never edit them.

### 11.2 The files

- Filename: `<YYYY-MM-DD>_<N>_<reason_slug>.py` — produced by the `file_template`; the date is the creation date, `N` is the revision number, and the slug states the REASON (`create_db`, `add_creator_user_id`, `index_target_custom_field_history_fk`). Filename/sequence examples: an older lib’s `2024-04-02_1_create_db.py` … `2026-06-05_5_add_creator_user_id.py`. **For the BODY style, imitate the current convention’s `2026-06-21_1_create_db.py` — NOT an older lib’s 2024 file, which predates the entity-reference rule (it contains string-literal column/index names; old style, do not copy).**
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
- `.migration_ver` (in the migrations dir) holds the latest revision number as plain text. `Alembic.create_migration(name)` maintains it (`rev_id = str(count + 1)`); if you hand-write a migration, update it yourself — **(divergence: an older lib’s is stale — says 9, has 11 files; don't repeat that)**.
- **While the lib is UNRELEASED there is exactly ONE migration.** Every schema change during initial development is folded into `<date>_1_create_db.py` — never a stack of `2_add_x.py`, `3_fix_x.py` before first release. After release, changes append sequential migrations following the same conventions (prefer `create_migration`-style generation, then hand-edit the body to the entity-referencing style below).

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

- Table names: `Entity.__tablename__`. Column names: `Entity.col.key` (works here — the mapping is fully configured by import time, unlike inside the entity's own class body, §4). Index/constraint names: `Entity.INDEX_*` constants. **The ONLY string literal permitted is the ForeignKey target** (`ForeignKey('workspace.id')`, with `ondelete='CASCADE'` where the entity declares it). Writing `'thing'` or `'workspace_id'` as a literal is exactly the "not paying attention to the smallest details" review rejection.
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
- **`@Cache`:** key is a `str.format` template bound BY PARAMETER NAME from the wrapped function's signature (positional, kwargs, then declared defaults) — a placeholder that names a non-parameter renders as `!M{name}M!`, a falsy param as `!E{name}E!`; newlines are stripped, the key is truncated to 250 chars, and spaces are REPLACED with underscores. Unknown `handler_name` raises `ValueError` at call time. `invalidate=True` runs the function FIRST, then deletes the key, and skips deletion when the function raises. String `expire` (e.g. `'1h'`) is parsed at decoration time. **A `None` result is NEVER cached** — `get`-swallowed-404 lookups (§6) hit the DB every call; there is no negative caching.
- **`IntEnum` TypeDecorator is truthiness-based.** READ side: a stored `0` comes back as `None` (`self._enumtype(value) if value else None`) — so **enum values MUST start at 1**. BIND side: a plain `enum.Enum` member (the convention, §4) is always truthy and binds its `.value` — but a python `enum.IntEnum` member with value 0 is falsy and binds NULL. Both directions are safe as long as values start at 1.
- **Mixins carry Python-side `default=` only** (no `server_default`, no `nullable=False`) and `_creation_order = 9998` pins them to the end of the table.
- **`DefaultRegistry.register` raises `ValueError` on a duplicate key** (hence guarded registration); `unregister` is silent when absent; `get()` with no key falls back to the FIRST registered object; `registered()` lists keys.
- **`start_core_lib()` raises `CoreLibInitException` if called twice** on the same instance.
- **`Observer.notify` re-raises listener exceptions** after logging them (§8) — a throwing host listener fails the service call that fired the event, post-commit.
- **`SqlAlchemyConnectionFactory`:** reads `create_db` (code default TRUE → `Base.metadata.create_all` at construction; base yaml ships `false` — prod relies on `install()`), `log_queries` → `echo`, `session.pool_recycle` (code default 3200) / `pool_pre_ping` always passed; `pool_size`/`max_overflow` are OMITTED for sqlite (unsupported-pool protocols). Session contexts auto-commit on clean exit and rollback on exception.
- **`build_url`:** `{protocol: sqlite, file: ':memory:'}` → `sqlite:///:memory:`.

## 13. Tests — the philosophy and the exact mechanics

### 13.0 The bar: a suite that is HARD to pass

A suite that only walks the happy path is a green light with nothing behind it. Four standing requirements — the full treatment, with checklists, is [`skills/core-lib-tests`](skills/core-lib-tests/SKILL.md):

1. **Try to BREAK the code.** Hunt the input that makes it *silently wrong* — a plausible-but-incorrect number, not a raise; a raise is loud and someone notices. Ask of every method: what claim in the docstring has no assertion behind it, and which guard could I delete and still see green? (Actually try it.) Beware the **symmetric test** — encode/decode, write/read-back — which passes whatever the two halves agree on, including agreeing on the wrong thing; assert the intermediate form directly.
2. **Edge cases are mandatory, not extras.** Empty / exactly one / many; both ends of every boundary and one past each; **ties** (equal timestamps or scores — which wins, deterministically?); nulls on every nullable column; at the length limit and one over; another tenant's id; a soft-deleted row; the same call twice. And remember **empty is often a legitimate answer** — a guard that rejects falsy rejects it.
3. **Drive COMPLETE use cases end to end** through public services — the whole story a user performs, in order, asserting real values at each step. A flow catches what per-method tests structurally cannot: that step 4 still works after step 9 changed the definition, that ids from step 1 are valid at step 8, that two tenants running the same flow never see each other's rows.
4. **Use the REAL thing.** See §13.2 — a mock is a claim about a collaborator, and that claim is what breaks in production.

A test you were confident would pass before running it taught you nothing.

### 13.1 The formula (non-negotiable)

**A test asserts the data you WANT the function to return — recomputed independently — never the data the function happens to return.** Expected values are hardcoded literals or derived from the test's own inputs by DIFFERENT means than the code under test. Never echo a function's output back into its own assertion. Never loosen an assertion so a test passes. **When a test fails, the CODE is wrong — you fix the code, not the test.** A test that adapts itself to broken output is worse than no test. Prove strictness with a mutation check: temporarily break the production code (drop a decorator, flip a filter) and confirm the suite goes RED; revert.

### 13.2 Test the REAL composed stack — fakes hid real bugs

Suites run against the real `FooCoreLib` — real DataAccess, real `@Cache`/`@ResultToDict`/`@DuplicateErrorHandler`, real rule validators, real DB (in-memory sqlite), real backend (moto/MinIO for S3). Hand-written fake DAs/fake storage previously masked three shipped bugs in one lib: (1) a `server_default`-only column returning `None`/`DetachedInstanceError` on the real ORM, (2) a file extension computed from `enum.value` producing `.1`, (3) fake rows returning enum MEMBERS where the real stack returns int values. Permitted doubles, exhaustively:
- a backend that cannot run on a test host (the ~50-binary a newer lib pipeline), injected through a sanctioned seam (§13.4) or through a REAL production constructor parameter (a newer lib’s `DocumentService(extractors=[...])`);
- fake SDK MODULES for per-extractor/adapter units via `mock.patch.dict(sys.modules, {'fitz': fake})` (a newer lib’s `make_fitz_module.py` et al.) — import-level substitution of an uninstallable SDK, confined to those unit files;
- a mocked SDK client in the backend adapter's own unit file (§13.3).
Nothing else — never monkeypatch the composed lib's internals from a test.

### 13.3 Service-only — we test what we expose, and we expose services

- A test calls ONLY public service methods on the composed lib: `self.foo_core_lib.thing.create(...)`. **The DB DataAccess and the storage adapter are internal — never touched by a test: not to create fixtures, not as a read-oracle.** Grep the finished test file for `_da`, `._db`, `_storage`, or any `._<private>` on the lib object: ZERO hits.
- **No standalone DB-DataAccess test files.** The DA is exercised through its service. (Deleted in review: `test_data_access.py`, `test_document_*_data_access.py`, a DA-seeded cascade test, and a DA-direct search test whose behavior `lib.search` already covered.) The ONE sanctioned exception is the backend ADAPTER unit file (the current convention’s `tests/test_storage_data_access.py`): it constructs `StorageDataAccess` directly with a fake factory + mocked SDK client to pin the client-call contract — a "client test", kept OUT of the service suites. **(divergence: an older lib’s suite still builds a test-owned DataAccess for fixture wipes and history reads — legacy, do not copy.)**
- Fixtures are created THROUGH services (`workspace.create` → `collection.create` → `document.upload` → `document_collaborator.grant`); state is verified THROUGH services (`get`, `list`, `list_trash`, `search`, `is_favorite`, `get_markdown`, presigned URLs from `get_download_url`/`get_view_payload`).
- Whatever is only observable by reaching into internals gets re-expressed through the service or DROPPED — deleted categories, for the record: exact blob-key sets in storage; raw `deleted_at` reads ("trashed" is: absent from `get`/`list`, present in `list_trash`); cache-hit proofs that mutate the row behind the cache (cache correctness is observable only as write→read freshness); DA-monkeypatched race simulations (duplicate behavior is exercised by calling the service twice and asserting what it REALLY does); exact intra-type orderings that depend on `created_at` you cannot set through any service (assert set-membership, window sizes, and type-boundary ordering instead — never a flaky exact sequence).
- Storage-backed assertions through the service: markdown content via `get_markdown`; original presence via a presigned URL that contains the document's own `original_key` (taken from the upload's returned dict), a `Signature=` param, and `Expires=` ≈ `now + expiry` (absolute epoch, `assertAlmostEqual(..., delta=60)`).
- Allowed OUTSIDE the service suites, in their own plain-`unittest` files (no CoreLib): entity-introspection tests (`Entity.__table__.indexes` carries the FK index — an older lib’s `test_target_custom_field_history_entity.py` is the reference); pure-helper tests (slug/key derivation functions); the backend client adapter test above; an env-guarded REAL-backend integration test (`@unittest.skipUnless(os.environ.get('FOO_STORAGE_ENDPOINT_URL'), ...)`) that round-trips every verb and cleans up after itself.
- **A stateless pure ENGINE may be constructed directly — additively only.** `ScorerService()` with no arguments (no DataAccess, no DB, nothing faked) is not the bespoke harness this rule bans: nothing stands in for the composed lib, so no wiring bug can hide behind it, and asserting arithmetic against it is clearer than driving the same sum through publish-and-submit. The hard condition is that it never becomes the ONLY coverage: **every mode, branch and rule type tested directly on an engine must ALSO be reached through the public surface by at least one test** — a variant that appears only in engine tests leaves the wiring that selects it unproven while the suite stays green. Verify it per variant rather than assuming ("the engine is covered somewhere" is not the check): `for m in <every variant>; do grep -rl "$m" tests/*.py | xargs grep -l "<service>.<public_method>" || echo "$m is engine-only"; done`. Same for importing a private function into a test: allowed only for a defensive branch genuinely unreachable from the public API, and first ask whether that branch should exist at all (an unreachable arm is usually dead code — §13.0).

### 13.4 `tests/helpers/utils.py` — the one bootstrap

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


class CoreLibInstance(object):
    instance = None
    config = None


threadLock = threading.Lock()

_project_ids = itertools.count(1)


def new_project_id() -> int:
    return next(_project_ids)


def load_config():
    if not CoreLibInstance.config:
        path = os.path.join(os.path.dirname(__file__), '..', 'data')
        load_dotenv(dotenv_path=os.path.join(path, '.env'))

        GlobalHydra.instance().clear()
        hydra.initialize(config_path=os.path.join('..', 'data', 'config'), caller_stack_depth=1)
        CoreLibInstance.config = hydra.compose('config.yaml')
    return CoreLibInstance.config


def sync_create_start_core_lib() -> FooCoreLib:
    threadLock.acquire()
    try:
        if not CoreLibInstance.instance:
            [CoreLib.cache_registry.unregister(key) for key in CoreLib.cache_registry.registered()]
            [CoreLib.observer_registry.unregister(key) for key in CoreLib.observer_registry.registered()]
            CoreLibInstance.instance = FooCoreLib(load_config())
            CoreLibInstance.instance.start_core_lib()

        # Clear the cache
        for key in CoreLib.cache_registry.registered():
            CoreLib.cache_registry.get(key).flush_all()
    except BaseException as e:
        print(''.join(traceback.format_exception(type(e), e, e.__traceback__)))
        raise e
    finally:
        threadLock.release()
    return CoreLibInstance.instance
```

- ONE composed CoreLib per test process, shared by every suite. **The `finally: threadLock.release()` is mandatory** — a lock still held after a failed boot deadlocks the next suite's `setUpClass` silently (the run just hangs). **(divergence: the sibling libs' helpers release only on the success path — a known footgun, already documented for the admin-backend harness; new libs use the `finally` shape above.)**
- `new_project_id()` is a MONOTONIC counter, not `random.randint` — the tenant key is uniquely constrained, so a random collision is a hard 409 mid-suite. (Libs whose tenant key is not unique, like task, may use `random.randint(1000, 10000)` per test file; when in doubt, the counter.)
- **Startup-job variant** (needed ONLY when the lib schedules a `startup` job that queries a table immediately — an older lib’s real helper, at its divergent path `tests/utils/helpers.py`): before constructing the lib, pre-create the tables on the FACTORY engine and run install —
  `db_factory = CoreLib.connection_factory_registry.get_or_reg(config.core_lib.data.sqlalchemy)` → `Thing.__table__.create(db_factory.engine, checkfirst=True)` → construct → `instance.install(config)` → `start_core_lib()`. (Remember §7: Alembic runs on its OWN engine — for `:memory:` sqlite the factory-engine `create` is what the lib's queries actually see.)
- Test-only stand-in entities (rows your queries JOIN against but another lib owns, e.g. a `User`) live in `tests/data/entities/` and are created the same way (`TestUser.__table__.create(engine, checkfirst=True)`) inside the helper.
- **Backend-control seams live HERE, not in tests:** a `@contextmanager def use_markdown_extractor(lib, extractor):` that swaps `lib.document._markdown_extractor` and restores it in `finally`. A test uses the context manager; only utils knows the private attribute. (For a stateless lib, prefer the front door: a newer lib’s orchestration units pass controlled extractors through the REAL production constructor parameter — `DocumentService(selection_service=..., extractors=[...])` — nothing monkeypatched.)

### 13.5 `tests/data/` — config + env

- `config/config.yaml`: `defaults: [core_lib, foo_core_lib, foo_core_lib_test]` where `foo_core_lib_test.yaml` (same dir, starts `# @package _global_`) carries test-safe overrides — an older lib’s sets `create_db: true` + sqlite + `version_table` + job config; an older lib’s sets a fake `api_key: SOME-KEY` so any eager construction succeeds. If the packaged yaml is FULLY env-driven (as in the reference lib), the third group may be unnecessary — then use `defaults: [core_lib, foo_core_lib, _self_]` plus inline keys for anything extra (e.g. a composed sibling's section). Never compose a sibling REPO's config group (§3.4).
- `.env` (loaded by `load_config`): DB → `FOO_DB_PROTOCOL=sqlite`, `FOO_DB_FILE=:memory:`, `FOO_DB_CREATE_DB=true` (tests rely on `create_all`, not Alembic — except one variant); `MEMCACHED_HOST=localhost` (cheap insurance — §3.4); backend endpoints → **`http://127.0.0.1:9000`, NEVER `http://localhost:9000`**: on Windows `localhost` resolves to IPv6 `::1` first and a moto/MinIO bound on IPv4 stalls EVERY NEW connection ~60s before falling back — an 8-second suite becomes ~17 minutes at ~0s CPU, and the only tell is `create_connection` at the top of a `faulthandler` dump.
- Local S3 without Docker: `pip install "moto[server]"`, run exactly ONE `python -m moto.server -p 9000` (several instances on one port scatter requests and stall), create the bucket once via boto3. boto3/moto are dev-env deps, never `requirements.txt`.

### 13.6 Writing the suites

- **One `unittest.TestCase` class per file, every test a method of it.** File `test_thing_service.py` → `class TestThingService`. Merging multiple classes into one was a review requirement, not a preference.
- `setUpClass` is exactly: `cls.foo_core_lib = sync_create_start_core_lib()` — the attribute is the FULL lib name (`cls.foo_core_lib`, `cls.foo_core_lib`), never `cls.lib`.
- Access is inline and fully spelled at every call site: `self.foo_core_lib.thing.create(...)`. **No `@property` accessors, no `service = self.foo_core_lib.thing` aliases, no helper indirection that hides which service a failing line hit.** Small `_seed()`/`_upload()` fixture helpers ON the test class are fine — they still call services with the full spelling.
- The DB (and bucket) are shared across the whole run: every test takes a fresh `new_project_id()`, never assumes an empty table, an absolute autoincrement id, or `id == 1`. "ids are monotonic" is asserted relatively (`second > first`).
- Unknown-id branches probe with a constant far above any autoincrement: `ABSENT_THING_ID = 2_000_000_000` — never `99`/`999` (a long-lived shared DB WILL reach those).
- Dict fields are read with entity keys — `row[Thing.name.key]`, `row[Thing.kind.key]` — never string literals.
- Enum columns assert the INT value (and optionally round-trip: `ThingKind(row[Thing.kind.key]) is ThingKind.ALPHA`).
- Log-contract tests use `assertLogs` on the service's module logger (warning fallbacks, swallowed extraction errors) — asserting the documented side channel, not internals.
- Patching a MODULE-LEVEL tuning constant (`document_service.EMPTY_TRASH_BATCH = 2`) to force loop boundaries is allowed — always restored in `try/finally`. Patching methods/attributes of the composed lib is NOT (the one exception is the utils-owned seam, §13.4).
- Exercise error paths as the service defines them: 409 via a real duplicate through the real DB (`assertRaises(StatusCodeException)` + `status_code == HTTPStatus.CONFLICT`), 404/`None` via the service's own contract, `ValueError` for missing args, `PermissionError` for rule-validator rejections — with a follow-up assertion that the failed call left the data untouched (read it back through the service).
- The composed-lib smoke file (`test_foo_core_lib.py`) asserts the PUBLIC surface only: every service attribute exists and works end to end with one real call each; config threading is proven through BEHAVIOR (an env-value visible in an output), not by reading private fields.
- Suite hygiene facts: the hydra `version_base` UserWarning at bootstrap is expected noise; run with `PYTHONPATH="../core-lib;." python -m unittest discover -s tests -p "test_*.py"` (`;` on native-Windows Python, `:` on POSIX — sibling repos on the path as needed, e.g. library adds `../a newer lib-core-lib`).

## 14. Packaging / repo hygiene

- `requirements.txt` — RUNTIME deps only: `core-lib` first, then real runtime deps (`temporalio`, another `*-core-lib` your lib composes). Test-only deps (hydra, python-dotenv, freezegun, boto3, moto) come from the dev environment — never listed. Optional backends stay optional via the lazy-import pattern (§10). **(divergence: an older lib’s file omits `core-lib` — an inconsistency, not a convention.)**
- If the lib uses coverage: `.coveragerc` with `source = foo_core_lib`, `branch = True`, omit `foo_core_lib/data_layers/data/db/migrations/*`. Never commit the data files (rule at the top of this document) — `.coveragerc` IS tracked, only its output is ignored.
- **`.gitignore` covers every generated artifact, not just the ones this lib happens to produce today.** Bytecode and caches are written by whichever tool someone runs once, and then get swept in by a wide `git add`. The canonical list — keep the repo's own file and `core_lib_generator/template_core_lib/.gitignore` **in step**, since the template is what every generated lib inherits:

  ```gitignore
  # PYTHON
  /venv
  .venv
  **/*.py[cod]          # .pyc AND .pyo AND .pyd in one pattern
  **/__pycache__/
  __pycache__/
  *$py.class

  # CACHES — every tool that writes one, whether or not this lib uses it today
  .pytest_cache/
  .mypy_cache/
  .ruff_cache/
  .hypothesis/
  .tox/

  # COVERAGE — local run artifacts; `.coveragerc` itself stays tracked
  .coverage
  .coverage.*
  coverage.xml
  htmlcov/

  # BUILD
  *.egg-info
  *.eggs
  build/
  dist/
  ```

  Two things the older files got wrong and a new one must not repeat: `/venv` alone misses `.venv` (the leading slash anchors it to the repo root and the dot-form is a different name), and `**/__pycache__/*` ignores a cache directory's CONTENTS but not the directory — pair it with, or replace it by, a trailing-slash `__pycache__/`. Prefer `*.py[cod]` to listing `*.pyc` and `*.pyo` separately; it also covers `.pyd`.
- No `npm run build`-style heavy steps in any Dockerfile — install dependencies only.
- Constants that multiple modules need live in `constants.py` (or a dedicated constants module) — never in a heavyweight module whose import drags in half the lib; that is how circular imports are born.

## 15. Build order (follow it top to bottom)

1. Skeleton: package dirs + every `__init__.py` (§2), `constants.py`, `requirements.txt`, `.gitignore` (+ `.coveragerc` if using coverage).
2. Config: `config/foo_core_lib.yaml` (+ empty `config/__init__.py`), searchpath plugin, repo-root `core_lib_config.yaml` (if the lib has install/CLI). Every future config key goes here FIRST.
3. Entities (+ enums, INDEX_/UQ_ constants, mixins).
4. DataAccess per entity (CRUD base + rule_validator + domain queries).
5. Services per entity (`Service` base, decorators, tenant boundary, events fired via `@Observe` if any).
6. Composition root (guarded registrations, `get_or_reg`, services in dependency order, install/uninstall) — plus observer/jobs wiring if used.
7. The ONE first migration + `env.py`/`script.py.mako` copied from a sibling + `.migration_ver` = `1`. Verify schema identity against `create_all`.
8. Test bootstrap: `tests/helpers/utils.py` (§13.4, with the `finally` release), `tests/data/config/config.yaml` (+ `foo_core_lib_test.yaml` or inline `_self_` keys), `tests/data/.env`.
9. Service test suites, one class per file, written to §13. Entity/helper/adapter plain-unittest files as needed.
10. Run the FULL suite from the repo root; then mutation-check at least the cache decorators and one rule validator; then run a sibling lib's suite to confirm you broke nothing shared.

## 16. Things to AVOID (each rejected in review or debugged at cost)

1. Inventing any pattern the sibling libs don't use (§0) — including "improvements".
2. Hand-rolled CRUD in a DataAccess (`session.add`/`session.flush` loops) instead of the CRUD bases.
2a. A `create` override on a DataAccess, a second `create_rule_validator`, or an allow-list entry restating a column's type or `nullable=False` (§5.1).
2b. A `@dataclass` declared under `data_layers/service/` — data types belong in `data_layers/data/data_types/` (§4.1). (First check it shouldn't just be the entity — §4; and anything error-shaped goes to `error_handling/` instead — §4.2.)
2c. An `errors.py` / `exceptions.py` holding several classes, or an error type filed outside `error_handling/` because "it is a dataclass, not an exception" (§4.2).
2d. A file under `data_layers/service/` whose name ends in neither `_service.py` nor `_helper.py` (§6.1).
2e. A column name written as a string literal anywhere outside an entity declaration or a migration — including inside a set, tuple or module constant, where a stale name fails SILENTLY (§4.3).
2f. A helper whose only callers are its own tests. Coverage proves it RUNS, not that anything needs it — check for a caller in library source (excluding docstring text that merely contains the name), and if the property it guarded is real, re-test it through the path the library actually takes (`skills/core-lib-tests`).
3. Calling or testing a DB DataAccess from outside the lib. Standalone DB-DA test files (the backend client-adapter unit is the one exception — §13.3).
4. A bespoke test harness that wires DAs+services directly instead of `sync_create_start_core_lib()`.
5. Fake DAs / fake storage inside service tests (they hid three real bugs — §13.2).
6. `@property`/alias indirection in tests; `cls.lib`; anything but the full inline spelling.
7. Plural public service attributes (`self.documents`); exposing a DA publicly.
8. `.get('key', default)` / `try` around config reads in composition/services (the connection-factory validation layer is the one sanctioned `.get` site — §10); missing keys in the packaged yaml.
9. Bare `${oc.env:...}` for booleans/numbers in a NEW lib's yaml (string-truthiness bug) — always `oc.decode`.
10. Composing a sibling repo's hydra config group in any defaults list.
11. Missing `config/__init__.py` (or any package `__init__.py`).
12. `localhost` in backend endpoints (Windows `::1` stall) — `127.0.0.1`.
13. More than one moto/MinIO bound to a port; per-run bucket wipes that tests don't need.
14. `random.randint` for a uniquely-constrained tenant key in tests; magic absent-ids like `99`.
15. String literals for table/column/index names in MIGRATIONS (entity refs only — §11.3; note the entity class body itself is the opposite, §4); uuid revision ids; multiple migrations before first release; a stale `.migration_ver`.
16. `server_default` without `default=` on an entity column.
17. Enum values starting at 0 on an `IntEnum`-typed column.
18. Unguarded `cache_registry`/`observer_registry` registration; shadowing `CoreLib.attach_listener` instead of `attach_foo_listener`.
19. Editing a test to make it pass; echo-assertions; exact-order assertions over `created_at` ties; tests that "pass with broken data".
20. Heavy SDK imports at module top for optional backends (`import boto3` belongs inside the client builder); optional backends in `requirements.txt`.
21. Deriving strings from `enum.value` when the NAME is meant (`.1` extension bug).
22. Releasing the test-bootstrap lock only on the success path (deadlocks the whole run on a failed boot — §13.4).
23. Committing `.coverage` files; letting a Dockerfile run build steps beyond dependency installation.

## 17. Final checklist before handing the lib over

- [ ] Package imports clean with NO optional SDKs installed (`python -c "import foo_core_lib"`).
- [ ] `FooCoreLib(compose)` constructs twice in one process without registry explosions (guards work).
- [ ] All public attributes are singular service names; every service subclasses `Service`; no DA reachable publicly.
- [ ] `config/__init__.py` + `hydra_plugins/.../__init__.py` exist; `pkg://foo_core_lib.config` composes from a scratch dir.
- [ ] Every config key code reads exists in `foo_core_lib.yaml`; env-sourced booleans/ints wrapped in `oc.decode`; DB block at `core_lib.data.sqlalchemy`; `version_table: foo_alembic_version` present.
- [ ] ONE migration; filename/date/rev/slug per §11.2; body references entities only (the current convention’s style, not an older lib’s 2024 file); `downgrade()` reverse order; `.migration_ver` = `1`; schema byte-identical to `create_all`; `install()`/`uninstall()` run against a scratch DB.
- [ ] `tests/helpers/utils.py` matches §13.4 including the `finally` lock release (only if startup jobs); `.env` has sqlite `:memory:`, `127.0.0.1` endpoints, `MEMCACHED_HOST`.
- [ ] Every service suite: one class per file; `cls.foo_core_lib`; inline access; fresh `new_project_id()` per test; `ABSENT_* = 2_000_000_000`; `Entity.col.key` for every dict read; zero `_da`/`_db`/`_storage` greps.
- [ ] Mutation check done (break code → red; revert → green). Full suite green from a clean checkout with only the documented env (moto/MinIO where applicable).
- [ ] `requirements.txt` runtime-only; nothing under `.coverage*` tracked.

---

# Appendix — rules from the sibling libs not covered by the recipe

Distilled from the sibling core-libs' own `AGENTS.md` files. They complement
§0–§17; wherever they appear to overlap, **the recipe above wins**.

## A1. No single-letter loop variables (except `i` / `j`)

Loop variables and comprehension bindings get **meaningful names** in both
production code and tests. `for row in rows`, `for document in documents`,
`for cell in row`, `for candidate in candidates` — never `for r in rows`,
`for d in docs`, `for k in storage.blobs`. The only allowed single letters
are `i` / `j` as canonical integer counters in `range(...)` loops; everything
else (`a`, `b`, `c`, `d`, `e`, `k`, `n`, `o`, `p`, `r`, `s`, `t`, `v`, `x`,
…) is banned. Tuple unpacking follows the same rule:
`left, right = sets[i], sets[j]`, not `a, b = sets[i], sets[j]`.

## A2. Specs are frozen dataclasses, not dict literals

When a "spec" — a plain-data description of rules / stages / scores /
config that a consumer module reads — is authored, model it as a **frozen
dataclass DSL owned by the consumer module**, never as a nested-dict literal.

```python
@dataclass(frozen=True)
class Rule:
    field: str
    operator: Operator
    value: Any
    meta_data: Optional[dict] = None

MY_SEED = Seed(
    key='acme', name='...', stages=[
        StageSeed(name='...', eligibility=[in_(RecordTypeField.key, ['user'])],
                  scores=[score_equal(TierField.key, 'premium', 20)]),
    ],
)
```

Renames are then caught by the type checker instead of a string grep, authors
can't typo a field, and reviewers read operator semantics from the helper name
(`score_between`, `gte`) instead of decoding a raw dict. The consumer walks the
dataclass directly; a `to_dict()` (if any) is for logging only, never the
input path. Add helper constructors (`equal`, `gte`, `in_`, …) on demand.

## A3. Keep each layer dependency-pure — enforce direction with a boundary test

Dependencies flow one way: a lower/transport layer stays free of the
higher layer's frameworks. A concern that belongs to the higher layer (a
validation framework like Pydantic, an agent-only contract) lives **in** that
higher layer, so the lower one keeps a minimal dependency set and can be
consumed on its own.

Lock the direction with a **boundary test** that fails if the lower-layer
package imports the higher-layer package. The test — not a comment — is what
keeps the layering from eroding as the code grows.


## A4. State transitions — history + outbox + observer event

Where a service models a stateful entity, every state transition should, in
addition to firing the observer event, write:

- a **history row** (a full snapshot of the changed fields), and
- an **outbox row** (an event log, with optional async-worker metadata),

so downstream consumers and audit trails stay consistent. Pass **raw values**
(enum members, native `datetime` objects) to the history service's `create`
— not values already converted by `@ResultToDict` — because the DA's
`setattr` loop converts `Enum` → `.value` itself.

## A5. Redacting sensitive data — one path, zero disclosure

If the library ever emits a preview / log / error for a value that may be
sensitive (PII, secrets, credentials), redact it to **zero bytes** of the raw
value — e.g. `[REDACTED, len=N]`, pattern name + length only, never a prefix,
suffix, hash, or partial. Route every redaction through **one** function so a
new call site can't reintroduce a leak. A debug flow that genuinely needs more
is a **separate** function with the trade-off stated in its docstring — never a
loosening of the shared one.

---

