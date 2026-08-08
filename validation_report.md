# UNA-2764 — Complete "how to architect a core-lib" documentation

Eliminates the recurring gap: every project implementing core-lib hit the same missing documentation on how to architect a *complete* core-lib, so the AI kept missing pieces and the operator kept re-explaining. This delivers three coordinated, tool-neutral, agnostic docs so a new core-lib can be built correctly end-to-end without re-explanation.

The information architecture:
- **`BUILDING_A_CORE_LIB.md`** (NEW) — the end-to-end architecture guide: mental model, complete anatomy, the three layers in depth, composition root, config/hydra wiring, external integrations, testing strategy, packaging, the ordered build sequence, a decision guide, the recurring-mistakes list, and a Definition-of-Done checklist. This is the "how to architect it" narrative that was missing.
- **`AGENTS.md`** — the structured, enforceable rulebook (§1–§8), consolidated from every `*-core-lib/AGENTS.md`. The guide cites these rules as `§x.y`.
- **`skills/`** — copy-paste-ready per-part scaffolding templates, enforced by the MANDATORY routing gate in AGENTS.md.

Files changed:
- BUILDING_A_CORE_LIB.md (new)
  The complete architecture guide (12 sections). Agnostic and self-contained; grounded in the real core-lib APIs and Hydra `_target_` config shape. Every `§x.y` reference resolves to an AGENTS.md rule; guide-internal cross-references use "section N" (a distinct namespace, no collision with AGENTS §). Includes the "recurring mistakes the AI keeps getting wrong" list — each mistake linked to the rule that prevents it — which is the direct gap-closer.
- AGENTS.md
  Added a prominent pointer in the header to read `BUILDING_A_CORE_LIB.md` first when building a whole lib or a substantial feature; clarifies AGENTS.md is the rules and the guide is the how-to-architect-it. (Rulebook content unchanged from the prior consolidated state: AGNOSTIC principles + Engineering rules §1–§8.)
- skills/core-lib-new/SKILL.md
  Points to `BUILDING_A_CORE_LIB.md` as the plan to read first (build sequence §9, decision guide §10, recurring mistakes §11, Definition of Done §12) before mechanical scaffolding.

Verification: guide is agnostic (no host/product/architecture.md/kato leakage); all 25 `§x.y` references resolve to real AGENTS.md anchors; guide-internal refs disambiguated to "section N"; links (`AGENTS.md`↔guide, skill→`../../BUILDING_A_CORE_LIB.md`) resolve.

Files changed (outside this repo, committed separately by the orchestration layer):
- architecture.md (workspace root)
  Pointer noting `core-lib/AGENTS.md` is the consolidated generic rulebook for every `*-core-lib`.
