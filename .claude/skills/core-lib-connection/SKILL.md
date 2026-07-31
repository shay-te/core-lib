---
name: core-lib-connection
description: MANDATORY — load this skill BEFORE you add or change an external client, provider, API or SDK integration, HTTP client, connection factory, or any wrapper around a third-party service (LLM, object storage/S3, payment gateway) in a *-core-lib; do not write it from memory. Creates a ConnectionFactory that builds the SDK client once (fetch→validate→use, lazy import) plus a Connection with typed errors.
---

The canonical, tool-neutral version of this skill lives at
[`skills/core-lib-connection/SKILL.md`](../../../skills/core-lib-connection/SKILL.md)
(kept tool-neutral so non-Claude agents can use it too). **Read that file and
follow it.**
