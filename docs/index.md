---
id: main
title: Getting Started
sidebar: core_lib_doc_sidebar
permalink: index.html
folder: core_lib_doc
toc: false
---
<p><img src="images/core-lib.png" alt="Core-Lib" width="240"/></p>

---

**Core-Lib is a Python application skeleton. Your application is exposed through one `CoreLib` class — business logic stays in services; web frameworks, databases, and external services plug in from the outside.**

The result: when Flask, SQLAlchemy, or your payment provider changes, the change stays at the edge of your app. It doesn't ripple through forty files.

---

## Without Core-Lib vs. with Core-Lib

```python
# Without Core-Lib — the Service can only run inside Flask, against the live DB,
# with the real Stripe SDK. Tests need all three.
from flask import request
from app.db import session
import stripe

def create_subscription(plan):
    customer = stripe.Customer.create(email=request.json['email'])
    session.add(Subscription(user_id=request.user.id, plan=plan, ext_id=customer.id))
    session.commit()
    return {'ok': True}
```

```python
# With Core-Lib — the Service receives its collaborators. Same code runs from
# Flask, FastAPI, a background job, or a test with mocked clients.
class SubscriptionService(Service):
    def __init__(self, sub_da, billing_client):
        self.sub_da = sub_da
        self.billing_client = billing_client

    def create(self, user_id, email, plan):
        customer = self.billing_client.create_customer(email)
        return self.sub_da.create(user_id, plan, customer.id)
```

The route handler does the framework-specific work (reading `request`, returning a response). The Service does business logic. Nothing in `SubscriptionService` knows what web framework, what database, or which payment provider is behind it.

---

## What Core-Lib is

Core-Lib is an **application-structure framework** for Python backends. It standardizes how you wire services, data access, external clients, jobs, and tests — so your business logic stays independent from Flask, Django, SQLAlchemy, and everything else you build on top of.

Your application is exposed through a class that inherits from `CoreLib`. That class wires services, data access, and clients together — it has no knowledge of any web framework or database library. It is just Python. The framework sits on top and calls into it.

```python
class UserCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        super().__init__()
        db = SqlAlchemyConnectionFactory(config.core_lib.your_core_lib.data.db)  # connection at the edge
        self.user = UserService(UserDataAccess(db))                              # business logic
```

When the framework beneath you changes — and it will — you replace the thin web layer. Your services, your data access, and most of your tests stay the same.

```python
# Flask today
@app.route('/api/user')
def get_user():
    return response_json(app_instance.user.get(request.user.id))

# FastAPI tomorrow — UserService didn't change, not one line
@router.get('/api/user')
def get_user():
    return app_instance.user.get(current_user.id)
```

---

## What Core-Lib is not

**Not a web framework.** It is not in the same space as FastAPI or Django. No router, no request lifecycle. It works alongside any web framework — you bring the web layer, Core-Lib handles everything behind it.

**Not a replacement for SQLAlchemy, Redis, or MongoDB.** You still write SQLAlchemy models. You still use Redis commands. Core-Lib does not hide them — it stops them from spreading through your entire codebase.

**Not opinionated about your domain.** It gives you structure for the layers, not rules about what goes inside them.

---

## "Yes, it adds a layer. What do I get for it?"

Core-Lib does add a dependency. That trade-off is deliberate, and here is what you get in return:

- **One place where infrastructure is created.** Connections, clients, and caches are constructed in `CoreLib.__init__` and nowhere else. Your service code never imports a session, a Redis client, or a Stripe SDK.
- **The same business logic runs from web requests, jobs, scripts, and tests.** No duplicate wiring, no `if running_in_tests:` branches.
- **Tests boot the full app against SQLite and mock clients with one config override.** No Docker, no fixtures for external services.
- **Config-driven swaps.** Postgres → MySQL, Memcached → Redis, payment provider A → B happens in YAML, not across business logic — assuming each provider is wrapped behind the same `Client` interface (e.g. `charge_customer()`, `create_subscription()`). Core-Lib gives you the seam; you write the adapter.

If your app is a script or a prototype, you should not pay this cost. The "When to use Core-Lib" section below is honest about that.

---

## "But Core-Lib still leaks the third-party library through."

Yes — and that is the point.

Core-Lib is **not** an abstraction layer over SQLAlchemy or PyMongo. It does not invent a new query API. Inside a `with db.get() as session:` block, `session` is a real `sqlalchemy.orm.Session`. Inside `with mongo.get() as client:`, you get a real `MongoClient`. The same pattern, the same skills, the same docs — but the lifecycle (open, commit, close) is handled for you.

What Core-Lib **does** standardize is the seam: every data source, regardless of vendor, is wrapped in the same `with conn.get() as x:` context manager and constructed at the edge of the app. So your business logic only depends on a `DataAccess` class, not on whichever library is behind it. Swapping the library is a wiring change; the call sites do not move.

It is a structural framework, not a vendor-neutral data layer. If you wanted the latter, this is not it — and that is intentional.

---

## The framework that killed the project

A team built a complete production system on Play Framework 1.2. Controllers, models, business logic — all written to Play's API. It worked. Shipped. Users depended on it.

Then Play 2.0 came out — completely different architecture. Not an upgrade. A rewrite. The migration cost was indistinguishable from rebuilding the product from scratch.

**The project was dropped.**

The framework didn't fail them. The coupling did. When the framework changed, there was no separation between "the thing we built" and "the thing we built it on."

Most teams don't get killed by one big rewrite. They get slowed down by hundreds of small places where framework code leaked into business code — until the day a major version drops and all of those places need to change at once.

This is what Core-Lib is designed to prevent.

---

## When to use Core-Lib

Use it when:
- Your backend will live for years, not weeks
- Multiple engineers will touch the same codebase
- You want to run the same business logic from web requests, background jobs, scripts, and tests
- You need to swap infrastructure (DB, cache, HTTP client) without touching business logic

Don't use it when:
- Your app is a prototype, script, or simple CRUD app
- There's no long-term maintenance expectation
- Your app is small and unlikely to change much

---

## Why not just use SQLAlchemy (or Flask, or Redis) directly?

You can. And for a small script, you should.

The problem appears at scale. When you use SQLAlchemy directly across 40 files, your business logic is coupled to database sessions. When you use Flask's `request` object in your service layer, your service layer can't run without Flask. When your tests need a real Redis instance to start, your test suite becomes slow and fragile.

You don't notice the problem when writing code. You notice it when you try to change it.

Core-Lib draws a hard line: database sessions, HTTP clients, and external services are wired in at startup via config, not imported across your codebase. Your service layer never touches a session object. Your tests spin up the full application against SQLite and a mock HTTP client — no Docker, no external services, no environment setup.

When you need to swap Postgres for MySQL, or Redis for Memcached, or one payment provider for another — the change stays in wiring code instead of spreading through business logic.

---

## Why not just enforce this with discipline, without the library?

You can do that too. Core-Lib exists because teams rarely keep these boundaries clean by convention alone. Architecture drift happens gradually — one shortcut here, one imported session there — until the boundaries are gone.

Core-Lib makes the right structure the path of least resistance. It provides:

- A standard connection lifecycle for every supported database and cache
- A bootstrapping pattern that works identically from web, job, script, and test
- Config-driven wiring — swap any collaborator by changing YAML, not code
- Test helpers that initialize the full app with a single config override
- A shared vocabulary (`Service`, `DataAccess`, `Client`, `Job`) that makes architecture decisions explicit across the team

Without that, the correct architecture depends on every engineer remembering it every day.

---

## The layers

```
CoreLib              your application — the single entry point
  ├── Service            business logic and orchestration
  ├── DataAccess         database queries
  │     └── Connection       sessions and connection pooling
  ├── Client             HTTP clients and third-party API wrappers
  └── Job                scheduled or background tasks
```

Every tool in Core-Lib exists to serve one of these layers. Services don't know about database sessions. DataAccess doesn't know about business rules. Clients don't know about services. The structure is a shared mental model the whole team can reason about.

---

## A real scenario: launching a B2B tier

Your app starts as B2C — Postgres, Stripe, cookie auth, one user type. Then you land enterprise customers who need an isolated database, invoice-based billing, and SSO login.

Without Core-Lib, "enterprise support" means grepping for every place Stripe is called, every place the session is used, every place the user model is assumed. That's not a feature. That's a partial rewrite.

With Core-Lib, `UserService`, `OrderService`, and `SubscriptionService` don't change at all. You wire two instances of the same class with two configs:

```python
# Consumer: shared Postgres, Stripe, cookie auth
consumer_app = YourCoreLib(consumer_config)

# Enterprise: per-tenant Postgres, invoice billing client, SAML auth handler
enterprise_app = YourCoreLib(enterprise_config)

consumer_app.subscription.create(user_id=42, email='jane@acme.com', plan='pro')
enterprise_app.subscription.create(user_id=42, email='jane@acme.com', plan='enterprise')
# Same SubscriptionService code; different SubscriptionDataAccess and BillingClient under it.
```

The condition: enterprise's `BillingClient` exposes the same methods (`create_customer`, `charge`, …) as Stripe's. The `Client` adapter is the work — but it's local work, in one file, not scattered through the codebase.

---

## A minimal example

### `your_core_lib.yaml`

```yaml
# @package _global_
core_lib:
  your_core_lib:
    data:
      db:
        log_queries: false
        create_db: true
        url:
          protocol: sqlite
```

### `your_core_lib.py`

```python
from omegaconf import DictConfig
from core_lib.core_lib import CoreLib
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory

class YourCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        super().__init__()
        db = SqlAlchemyConnectionFactory(config.core_lib.your_core_lib.data.db)
        self.user = UserService(UserDataAccess(db))
```

### `main.py`

```python
import hydra
from omegaconf import DictConfig

@hydra.main(config_path='.', config_name='your_core_lib.yaml')
def main(cfg: DictConfig):
    app = YourCoreLib(cfg)

if __name__ == '__main__':
    main()
```

### Hooking up a web framework

Build the `CoreLib` instance once at startup and call into it from your route handlers. The route only knows about `your_core_lib.user` — it has no idea what database, cache, or HTTP client is behind it.

```python
# Flask
app = Flask(__name__)
your_core_lib = YourCoreLib(load_config())

@app.route('/api/user/<int:user_id>')
def get_user(user_id):
    return your_core_lib.user.get(user_id)
```

The same `your_core_lib.user.get(user_id)` call works the same way from a Django view, a background job, a script, or a test. Auth, exception handling, and JSON responses are all opt-in — see [Web Helpers](/web.html) and [User Security](/user_security.html).

---

## Testing

Tests initialize the same `CoreLib` class with a config that points to SQLite and mock clients. No Docker. No external services. No test environment to maintain.

```python
import unittest
from core_lib.helpers.test import load_core_lib_config

class TestUserService(unittest.TestCase):
    def setUp(self):
        config = load_core_lib_config('./tests/config', 'test_config.yaml')
        self.app = YourCoreLib(config)

    def test_create_and_retrieve_user(self):
        user = self.app.user.create({'name': 'Jane'})
        self.assertEqual(self.app.user.get(user['id'])['name'], 'Jane')
```

The test config overrides only what differs from production:

```yaml
# tests/config/test_config_override.yaml
core_lib:
  your_core_lib:
    data:
      db:
        url:
          protocol: sqlite   # in-memory SQLite instead of production Postgres
```

---

## Installing

```bash
pip install core-lib
```

**Requirements:** Python > 3.7

## Running tests

```bash
python -m unittest discover
```

## Source

[https://github.com/shay-te/core-lib](https://github.com/shay-te/core-lib){:target="_blank"}

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426){:target="_blank"} for details on the code of conduct and the process for submitting pull requests.

## Author

**Shay Tessler** — [GitHub](https://github.com/shay-te){:target="_blank"}

## License

MIT — see the [LICENSE](https://github.com/shay-te/core-lib/blob/master/LICENSE){:target="_blank"} file for details.

<div style="margin-top:2em">
  <button class="pageNext-btn"><a href="/advantages.html">Next >></a></button>
</div>
