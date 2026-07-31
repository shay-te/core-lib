---
name: core-lib-tests
description: MANDATORY — load this skill BEFORE you add, fix, or restructure any test for a *-core-lib (entity/data-access/service/connection), raise coverage, or de-mock a test; do not write it from memory. Enforces one unittest.TestCase per file (filename mirrors the class), real collaborators over mocks (mock only DB/SDK/clock boundaries), agnostic fixtures, and an end-to-end test_flow.py.
---

The canonical, tool-neutral version of this skill lives at
[`skills/core-lib-tests/SKILL.md`](../../../skills/core-lib-tests/SKILL.md)
(kept tool-neutral so non-Claude agents can use it too). **Read that file and
follow it.**
