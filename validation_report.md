# UNA-2764 — Consolidated generic core-lib/AGENTS.md + mandatory scaffolding skills

Consolidated every `*-core-lib/AGENTS.md` into a single, generic, self-contained rulebook at `core-lib/AGENTS.md`, added tool-neutral scaffolding skills (one per core-lib part), and made skill loading a mandatory routing gate so any AI agent (not just Claude Code) picks them up reliably.

Source AGENTS.md files folded in (generalized): `core-lib`, `promise-core-lib`, `library-core-lib`, `agent-core-lib`, `llm-core-lib`, `funnel-core-lib`, `user-journey-core-lib`. Per-repo AGENTS.md files were left untouched.

Files changed:
- AGENTS.md
  Canonical generic rulebook for every `*-core-lib`. Structure: a "this library is AGNOSTIC" principles block (unnumbered headings), then a `# Engineering rules — every core-lib` H1 with the canonical numbered sections §1–§7 (coding conventions; file/package org; data layer; service layer; connections; enums; repo-specific context). Skills reference these as `§<section>.<rule>`. The skills section is a MANDATORY routing gate (imperative "you MUST first load the matching skill" + trigger→skill table). Self-contained — references no file outside this library (satisfies the lessons.md rule that a core-lib AGENTS.md must not reference architecture.md).
- skills/core-lib-entity/SKILL.md, skills/core-lib-data-access/SKILL.md, skills/core-lib-service/SKILL.md, skills/core-lib-connection/SKILL.md, skills/core-lib-migration/SKILL.md, skills/core-lib-tests/SKILL.md, skills/core-lib-new/SKILL.md
  Canonical tool-neutral guides, grounded in the real core-lib APIs (verified: CRUD base classes, Service, Cache/ResultToDict, DuplicateErrorHandler→409, DefaultRegistry.registered(), Factory.get(), instantiate_config, IntEnum/soft-delete mixins). Descriptions carry an imperative `MANDATORY — load this skill BEFORE you …` lead with rich trigger vocabulary and sibling boundaries. YAML-safe; every `§X.Y` reference resolves to a real AGENTS.md anchor.
- .claude/skills/core-lib-*/SKILL.md (7 files)
  Thin pointer skills for Claude Code native discovery; front-matter descriptions kept identical to the canonical guides (single source of truth). `.claude/` is not gitignored, so these are tracked.

Cross-agent note: canonical guides live in the tool-neutral `skills/` dir and are enforced via the mandatory routing gate in `AGENTS.md`; `.claude/skills/` holds only pointers for Claude Code's native UX.

Files changed (outside this repo, committed separately by the orchestration layer):
- architecture.md (workspace root)
  Pointer under "core-lib framework conventions" noting `core-lib/AGENTS.md` is the consolidated generic rulebook for every `*-core-lib`.
