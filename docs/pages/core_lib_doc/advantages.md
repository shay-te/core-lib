---
id: advantages
title: Advantages
sidebar: core_lib_doc_sidebar
permalink: advantages.html
folder: core_lib_doc
toc: false
---

Core-Lib is useful when a backend has to outlive its frameworks, change its infrastructure, and stay readable while several engineers work on it. The advantages below come from one habit: business logic lives in `Service` classes, and web frameworks, databases and external APIs are created in your `CoreLib` class and used only by route handlers, `DataAccess` and `Client` classes.

> **Where it fits:** Overview. Read this after [What is Core-Lib?](index.html) if you want the practical reasons behind the six-layer structure. The costs are listed on that page under [The cost](index.html#the-cost).

## Decoupled business logic

Your services don't depend directly on Flask, SQLAlchemy, or external services. The web layer calls into your `CoreLib`; your `CoreLib` doesn't know the web layer exists.

When your framework changes, you replace the route functions. Your services, data access, and most tests stay the same. The home page shows [the same `HelloApp` behind Flask and FastAPI](index.html#calling-it-from-flask-or-fastapi).

---

## Change infrastructure without rewriting your app

A database, HTTP client or payment provider sits behind one adapter: a `DataAccess` class for data sources, a `Client` class for external APIs, and `CoreLib.__init__` for the wiring.

- Same library, different backend (Postgres → MySQL, Memcached → Redis): a config change, when the class or URL comes from YAML.
- Different library or API (SQLAlchemy → MongoDB, one payment provider → another): you rewrite that adapter. Your `Service` code does not change as long as the adapter keeps the same methods and returns the same shapes.

The next section is a worked example.

---

## Adding an enterprise tier

Your app sells subscriptions to consumers: card payments, one shared Postgres. Now enterprise customers want to pay by invoice and want their data in a database of their own.

The service does not know which payment provider or database it talks to:

```python
# shop/subscription_service.py
from core_lib.data_layers.service.service import Service
from core_lib.data_transform.result_to_dict import ResultToDict

from shop.entities import Subscription      # a SQLAlchemy model: email, plan, billing_ref


class SubscriptionService(Service):
    def __init__(self, subscription_data_access, billing_client):
        self._subscription_data_access = subscription_data_access
        self._billing_client = billing_client

    @ResultToDict()
    def create(self, email: str, plan: str) -> dict:
        billing_ref = self._billing_client.start_subscription(email, plan)
        return self._subscription_data_access.create({
            Subscription.email.key: email,
            Subscription.plan.key: plan,
            Subscription.billing_ref.key: billing_ref,
        })
```

The `ShopCoreLib` on the home page ([with and without Core-Lib](index.html#why-not-just-do-this-with-discipline-without-the-library)) builds the database connection and the billing client from config with `instantiate_config`. So the enterprise tier is the same code, deployed a second time with a different YAML file:

```yaml
# config/consumer.yaml
core_lib:
  shop:
    data:
      db:
        _target_: core_lib.connection.sql_alchemy_connection_factory.SqlAlchemyConnectionFactory
        config:
          url: {protocol: postgresql, host: shared-db.internal, username: shop, password: '${oc.env:DB_PASSWORD}', file: shop}
    client:
      billing:
        _target_: shop.clients.CardBillingClient
        base_url: https://api.card-payments.example
```

```yaml
# config/enterprise.yaml: only what differs from consumer.yaml
defaults:
  - consumer
  - _self_

core_lib:
  shop:
    data:
      db:
        config:
          url: {host: acme-db.internal}
    client:
      billing:
        _target_: shop.clients.InvoiceBillingClient
        base_url: https://api.invoicing.example
```

Each deployment boots one `ShopCoreLib` from a `@hydra.main` entry point (see [The CoreLib Class](core_lib_main_class.html)), and you pick the file when you deploy:

```bash
python main.py                            # consumer deployment
python main.py --config-name=enterprise   # enterprise deployment
```

- **You write:** `InvoiceBillingClient`, with the two methods `CardBillingClient` already has (`start_subscription(email, plan)` and `is_paid(billing_ref)`), and `enterprise.yaml`.
- **Unchanged:** `SubscriptionService`, `SubscriptionDataAccess`, `ShopCoreLib`, your routes and your existing tests.
- **Not done for you:** SSO, organizations, seats and roles. Core-Lib has none of these. If enterprise accounts need them, that is domain work you would write either way.
- **One tier per process.** The cache, observer and connection registries, the job scheduler and `SecurityHandler` are class-level: one per process, shared by every `CoreLib` in it. Run each tier as its own deployment, not as two differently wired instances side by side.
- **Many tenants in one process** is a different design: one `CoreLib`, a tenant id column on your entities that every `DataAccess` query filters on, and the tenant id in cache keys (`@Cache('user_{tenant_id}_{user_id}')`). Core-Lib does not do that filtering for you.

If your hand-written app already injects the billing client, you get the same isolation without Core-Lib. What Core-Lib adds is that the choice is a `_target_` line in YAML instead of an `if` in your startup code.

---

## Run the same logic everywhere

The same `CoreLib` class runs behind web APIs, background jobs, scripts, and tests. Each process creates one instance at startup; tests create their own with a test config.

```python
# in a Flask or FastAPI route
hello_app.user.greet(user_id)

# in a Job: load_jobs() passes the object you map it to (usually your CoreLib) to initialized()
self.hello_app.user.greet(user_id)

# in a test
self.hello_app.user.greet(jane[User.id.key])
```

---

## Fast, reliable tests

Tests build the full application from a test config: SQLite instead of Postgres, fake clients instead of real services. If your queries also run on SQLite, that means no Docker and no external services.

```python
# tests/test_user.py
import unittest

from core_lib.helpers.test import load_core_lib_config

from hello_core_lib import HelloApp, User


class TestUserService(unittest.TestCase):
    def setUp(self):
        config = load_core_lib_config('./config', 'test_config.yaml')  # tests/config/, relative to this file
        self.hello_app = HelloApp(config)   # the class production uses, built from the test YAML

    def test_greet(self):
        jane = self.hello_app.user.create('Jane')
        self.assertEqual(self.hello_app.user.greet(jane[User.id.key]), 'Hello, Jane!')
```

`HelloApp` and `User` come from the [one-file example](index.html#a-complete-core-lib-app-in-one-file), and `tests/config/test_config.yaml` holds the same keys as its config: `db: {create_db: true, url: {protocol: sqlite}}`. See [Testing Core-Lib](test_core_lib.html) for larger configs, fake clients, and sharing one instance across test files.

---

## Consistent structure across teams

Core-Lib gives every project the same six names:

- `CoreLib` — single entry point, wires everything below it
- `Service` — business logic and orchestration
- `DataAccess` — database queries
- `Client` — external APIs and third-party services
- `Job` — scheduled or background tasks
- `Connection` — session lifecycle for any data source

In a project that follows them, every engineer knows where everything lives. Projects created with `core_lib generate` start with the `CoreLib` class and the `DataAccess` and `Service` modules already in place.

---

## Keep architecture from drifting

Most systems become tightly coupled over time, not by design but through shortcuts: one imported session here, one `request` object there.

Core-Lib makes the boundary the easy path: connections and clients are built once, in your `CoreLib` class, and handed to services, so importing a session into a service is the extra work. It does not police the boundary. If you want it checked, add an import rule to CI, for example an [import-linter](https://import-linter.readthedocs.io/){:target="_blank"} `forbidden` contract that fails when your `service` package imports `flask`, `django` or `sqlalchemy`.

---

## Long-lived code

A team built a complete production system on Play Framework 1.2, with controllers, models and business logic all written to Play's API. Then Play 2.0 came out with a different architecture. Moving to it cost about as much as rebuilding the product, and the project was dropped. The framework didn't fail them; the coupling did. Most teams are not killed by one big rewrite, but slowed down by hundreds of small places where framework code leaked into business code.

A Python example: SQLAlchemy 2.0 made `Query.get()` legacy in favour of `Session.get()`. In a Core-Lib app, SQLAlchemy calls live in `DataAccess` classes, so that change touches those files and not your services. The honest trade-off: Core-Lib's own `CRUDDataAccess` still calls `Query.get()` today (run with `python -W default` to see the `LegacyAPIWarning`), so for that part you wait for a Core-Lib release.

---

## Composing Core-Libs

Each Core-Lib that `core_lib generate` creates ships a Hydra search-path plugin. Once it is installed as a package, another project can list its YAML under `defaults:`, the same way `- core_lib` works, and build it from `_target_` (see [Instantiate Config](instantiate_config.html) and [The CoreLib Class](core_lib_main_class.html)).

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="index.html">Previous</a></button>
    <button class="pageNext-btn"><a href="project_structure.html">Next</a></button>
</div>
