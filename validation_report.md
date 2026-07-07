# UNA-2764 — Unite all core-lib AGENTS.md rules into core-lib/AGENTS.md (+ scaffolding skills)

Consolidated the rules from every `*-core-lib/AGENTS.md` into a single, generic, self-contained rulebook at `core-lib/AGENTS.md`, and added a set of tool-neutral scaffolding skills (one per core-lib part) so any AI agent can build a new core-lib correctly.

Source AGENTS.md files folded in (generalized): `core-lib`, `promise-core-lib`, `library-core-lib`, `agent-core-lib`, `llm-core-lib`. The per-repo AGENTS.md files were left untouched — they keep their own repo-specific lessons.

Files changed:
- AGENTS.md
  Rewrote `core-lib/AGENTS.md` as the canonical generic rulebook for every `*-core-lib`. Sections: a leading "this library is AGNOSTIC" block (no host/product knowledge, minimal deps, self-contained + fully tested, inject host-specific behavior, litmus test); (1) Coding conventions — fetch→validate→use, variable naming, no single-letter loop vars, parameter-list layout, raise-not-assert, keep-functions-simple for static analysis; (2) File & package organization; (3) Data layer — pure-CRUD DataAccess, never returns soft-deleted rows, entity-introspection writes, entity-derived column names, INTEGER not Integer; (4) Service layer — public/private surface, enum boundaries, DuplicateErrorHandler, cache-where-the-win-is-real, cache/invalidation invariants, history+outbox+observer, invalidate-on-mutation; (5) Connections & clients — connection-factory shape, lazy SDK imports, typed errors, dependency/extras_require policy, in-memory registries; (6) priority-ordered enums; (7) core-lib repo-specific context. Made the file fully self-contained: removed every `architecture.md` / "workspace" cross-reference so core-lib references no file outside itself. Added a "Scaffolding skills" index table linking the tool-neutral `skills/` guides.
- skills/core-lib-entity/SKILL.md
  Guide to scaffold a SQLAlchemy entity (Base, soft-delete mixins, IntEnum/INTEGER columns, plain-Enum nested enums).
- skills/core-lib-data-access/SKILL.md
  Guide to scaffold a pure-CRUD DataAccess on the real CRUD base classes, with RuleValidator and entity-introspection writes.
- skills/core-lib-service/SKILL.md
  Guide to scaffold a Service: decorator order (@DuplicateErrorHandler → @Cache → @ResultToDict), cache-key/invalidation rules, enum boundaries.
- skills/core-lib-connection/SKILL.md
  Guide to scaffold an outbound integration (ConnectionFactory + Connection): fetch→validate→use, lazy SDK import, typed errors.
- skills/core-lib-migration/SKILL.md
  Guide to create an Alembic migration (sa.INTEGER, literal column names allowed, matching downgrade).
- skills/core-lib-tests/SKILL.md
  Guide to write tests: one TestCase per file, real collaborators over mocks, agnostic fixtures, end-to-end test_flow.py.
- skills/core-lib-new/SKILL.md
  Orchestrator guide to scaffold a whole new core-lib end to end (layout, main class composition root, singleton, Hydra config/plugin, first vertical slice).
- .claude/skills/core-lib-*/SKILL.md (7 files)
  Thin pointer skills (name/description front-matter + link) for Claude Code native discovery, each pointing at the canonical tool-neutral guide under `skills/` so there is a single source of truth and no drift.

Cross-agent note: the canonical guides live in the tool-neutral `skills/` directory and are indexed in `AGENTS.md` (the de-facto cross-agent convention), so non-Claude agents discover and use them; `.claude/skills/` only holds pointers for Claude Code's native skill UX.

Files changed (outside this repo, committed separately by the orchestration layer):
- architecture.md (workspace root)
  Added a pointer under "core-lib framework conventions" noting that `core-lib/AGENTS.md` is the consolidated generic rulebook for every `*-core-lib`, and that workspace-wide convention changes should update both places.
