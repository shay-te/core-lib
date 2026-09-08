# AGENTS Notes — template_core_lib

## This library is built on core-lib — follow its rulebook

`template_core_lib` is a `*-core-lib`: it follows the shared core-lib
architecture (`data → data_access → service`), conventions, and scaffolding.
Those rules are **not** repeated here — they live in the `core-lib` package, so
there is exactly one source of truth:

| Read | For |
|---|---|
| `core-lib/AGENTS.md` | **Read first.** The AGNOSTIC principles, then the canonical recipe (§0–§17): naming, folder tree, config, entities, data types, error handling, DataAccess, services, composition root, observers, jobs, migrations, tests, packaging/`.gitignore`, build order, things to avoid, final checklist. |
| `core-lib/skills/` | Copy-paste scaffolding templates, one per core-lib part. |

Find them in the `core-lib` checkout beside this repo (`../core-lib/`) or in the
installed `core-lib` package.

## MANDATORY — load the matching skill before you write code

**Before you create or modify any part below, first load the matching core-lib
skill** (open and follow it). This is a hard rule, not a suggestion: match the
row and load the skill *before* writing code. Never write core-lib code from
memory when a matching skill exists. If more than one row matches (e.g. a new
entity that also needs a migration), load all that apply.

The table below is a convenience copy. **`core-lib/AGENTS.md` holds the
authoritative one — if they disagree, it wins, and `core-lib/skills/` is the
real inventory.** Check there for a skill this copy has not caught up with;
whoever adds a skill must add the row in both places.

| If you are about to… | You MUST first load |
|---|---|
| add or change an entity / table / model / column / nested enum | [`core-lib-entity`](../core-lib/skills/core-lib-entity/SKILL.md) |
| add or change a DataAccess / DAO / repository / query / get_by / list / filter | [`core-lib-data-access`](../core-lib/skills/core-lib-data-access/SKILL.md) |
| add or change a Service / business logic / public method / caching / invalidation | [`core-lib-service`](../core-lib/skills/core-lib-service/SKILL.md) |
| add or change an external client / provider / SDK / API integration / connection factory | [`core-lib-connection`](../core-lib/skills/core-lib-connection/SKILL.md) |
| add a migration / alter / create / drop a table, column, index, constraint | [`core-lib-migration`](../core-lib/skills/core-lib-migration/SKILL.md) |
| add / fix / restructure tests or raise coverage | [`core-lib-tests`](../core-lib/skills/core-lib-tests/SKILL.md) |
| write ANY helper / utility / converter / guard / parser, or a `helpers.py` — **check what `core_lib` already ships first** | [`core-lib-reuse`](../core-lib/skills/core-lib-reuse/SKILL.md) |
| add / change / raise / catch any exception, error class, error code, or validation-failure type; pick an HTTP status | [`core-lib-error-handling`](../core-lib/skills/core-lib-error-handling/SKILL.md) |

## This library is AGNOSTIC

Like every core-lib, this package must know **nothing** about the host
application that consumes it — no brand, no host env-var names, no
host-specific text, in source, tests, comments, docstrings, field names, or
fixtures. Anything host-specific is *injected* as a parameter with a safe
neutral default. The full rule is the "this library is AGNOSTIC" block in
`core-lib/AGENTS.md`.

## template_core_lib-specific notes

_Nothing yet. Record lessons that are specific to **this** library here._

_Anything generic — a rule every core-lib should follow — belongs in
`core-lib/AGENTS.md` instead, so every core-lib inherits it. If you catch
yourself re-explaining the same thing in a prompt, that is the signal to add it
there._
