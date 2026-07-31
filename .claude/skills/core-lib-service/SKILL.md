---
name: core-lib-service
description: MANDATORY — load this skill BEFORE you add or change a Service, business-logic layer, public core-lib method or API, caching or cache invalidation, unique-constraint (409) handling, or state-transition/observer logic in a *-core-lib; do not write it from memory. Creates a Service over a DataAccess with @Cache/@ResultToDict/@DuplicateErrorHandler and history+outbox. Raw queries go in core-lib-data-access.
---

The canonical, tool-neutral version of this skill lives at
[`skills/core-lib-service/SKILL.md`](../../../skills/core-lib-service/SKILL.md)
(kept tool-neutral so non-Claude agents can use it too). **Read that file and
follow it.**
