# AGENTS Notes — template_core_lib

## This library is built on core-lib — follow its rulebook

`template_core_lib` is a `*-core-lib`: it follows the shared core-lib
architecture (`data → data_access → service`), conventions, and scaffolding.
Those rules are **not** repeated here — they live in the `core-lib` package, so
there is exactly one source of truth:

| Read | For |
|---|---|
| `core-lib/BUILDING_A_CORE_LIB.md` | **Read first** when building a new layer or feature — the mental model, full anatomy, ordered build sequence, decision guide, recurring mistakes, and Definition of Done. |
| `core-lib/AGENTS.md` | The engineering rules (§1–§8): coding conventions, file/package organization, data layer, service layer, connections, enums, testing. |
| `core-lib/skills/` | Copy-paste scaffolding templates, one per core-lib part. |

Find them in the `core-lib` checkout beside this repo (`../core-lib/`) or in the
installed `core-lib` package.

## MANDATORY — load the matching skill before you write code

**Before you create or modify any part below, first load the matching core-lib
skill** (open and follow it). This is a hard rule, not a suggestion: match the
row and load the skill *before* writing code. Never write core-lib code from
memory when a matching skill exists. If more than one row matches (e.g. a new
entity that also needs a migration), load all that apply.

| If you are about to… | You MUST first load |
|---|---|
| add or change an entity / table / model / column / nested enum | `core-lib-entity` |
| add or change a DataAccess / DAO / repository / query / get_by / list | `core-lib-data-access` |
| add or change a Service / business logic / public method / caching | `core-lib-service` |
| add or change an external client / provider / SDK / connection factory | `core-lib-connection` |
| add a migration / alter / create / drop a table, column, index, constraint | `core-lib-migration` |
| add / fix / restructure tests or raise coverage | `core-lib-tests` |

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
