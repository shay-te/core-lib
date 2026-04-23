---
id: advantages
title: Advantages
sidebar: core_lib_doc_sidebar
permalink: advantages.html
folder: core_lib_doc
toc: false
---

### Decoupled business logic

Your services don't depend directly on Flask, SQLAlchemy, or external services. The web layer calls into your `CoreLib` — your `CoreLib` doesn't know the web layer exists.

When your framework changes, you replace the thin web layer. Your services, data access, and most tests stay the same.

---

### Change infrastructure without rewriting your app

Switching databases, HTTP clients, or payment providers stays in wiring code — not scattered through business logic. The change is isolated to your `CoreLib.__init__`, not spread across 40 files.

```python
# consumer instance
consumer_app = YourCoreLib(consumer_config)  # SQLite, Stripe, cookie auth

# enterprise instance — same class, different wiring
enterprise_app = YourCoreLib(enterprise_config)  # Postgres, invoice billing, SSO
```

---

### Run the same logic everywhere

The same `CoreLib` instance runs behind web APIs, background jobs, scripts, and tests. No duplication. No special cases.

```python
# web
your_core_lib.user.get(user_id)

# background job
self.core_lib.user.sync_all()

# test
self.app.user.create({'name': 'Jane'})
```

---

### Fast, reliable tests

Tests initialize the full application with an override config — SQLite instead of Postgres, mock clients instead of real services. No Docker. No external dependencies. No environment setup. Fast, isolated tests.

```python
class TestUserService(unittest.TestCase):
    def setUp(self):
        config = load_core_lib_config('./tests/config', 'test_config.yaml')
        self.app = YourCoreLib(config)  # full app, in-memory DB, mock clients
```

---

### Consistent structure across teams

Core-Lib enforces a shared vocabulary across every project:

- `Service` — business logic and orchestration
- `DataAccess` — database queries
- `Client` — external APIs and third-party services
- `Job` — scheduled or background tasks

Every engineer working in any `CoreLib` knows where everything lives.

---

### Prevent architecture drift

Most systems become tightly coupled over time — not by design, but through shortcuts. One imported session here, one `request` object there.

Core-Lib prevents this by keeping all dependencies at the edge of your application from day one, wired in via config instead of leaking into your codebase.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/index.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/project_structure.html">Next >></a></button>
</div>
