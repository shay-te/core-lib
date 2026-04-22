[![PyPI](https://img.shields.io/pypi/v/core-lib)](https://pypi.org/project/core-lib/)
![PyPI - License](https://img.shields.io/pypi/l/core-lib)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/core-lib)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/core-lib.svg)](https://pypistats.org/packages/core-lib)
[![GitHub stars](https://img.shields.io/github/stars/shay-te/core-lib?style=social)](https://github.com/shay-te/core-lib)

# Core-Lib

**Core-Lib keeps Flask, SQLAlchemy, and external services out of your business logic — so changing them doesn't mean rewriting your app.**

Without this separation, those dependencies spread through your codebase — and every future change gets more expensive.

---

Most Python backends start simple — then slowly become tightly coupled:
- Your services import Flask's `request`
- Your business logic depends on SQLAlchemy sessions
- Your tests require real external services to run

Everything works — until you try to change something. Then it turns into a rewrite.

Core-Lib exists to prevent that.

---

## What it is

Core-Lib is an **application-structure framework** for Python backends — the place where your application lives, while everything else (web frameworks, databases, APIs) plugs into it from the outside.

Core-Lib doesn't invent a new pattern — it enforces one consistently, so it survives beyond the first few months of development — when shortcuts start creeping in.

```python
class YourCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        CoreLib.__init__(self)
        db = SqlAlchemyConnectionFactory(config.core_lib.data.db)  # connection at the edge
        self.user = UserService(      # business logic
            UserDataAccess(db)        # database queries
        )
```

When the framework beneath you changes — and it will — you replace the thin web layer (not the entire codebase). Your services, data access, and most tests stay the same.

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

## What it is not

**Not a web framework.** No router, no request lifecycle. It works alongside Flask, Django, FastAPI — you bring the web layer.

**Not a replacement for SQLAlchemy, Redis, or MongoDB.** You still write SQLAlchemy models. You still use Redis commands. Core-Lib handles the connection lifecycle and stops those dependencies from spreading through your business logic.

---

## When to use it

Use it when:
- Your backend will live for years, not weeks
- Multiple engineers will touch the same codebase
- You want to run the same logic from web, jobs, scripts, and tests
- You need to swap infrastructure (DB, cache, HTTP client) without touching business logic

Don't use it when:
- Your app is a prototype, script, or simple CRUD app
- Your app is small and unlikely to change much

---

## Quickstart

```bash
pip install core-lib
```

**Requirements:** Python >= 3.7

---

## Documentation

Full documentation, examples, and guides: [https://shay-te.github.io/core-lib/](https://shay-te.github.io/core-lib/)

---

## Running tests

```bash
python -m unittest discover -v
```

## License

Core-Lib is licensed under [MIT](https://github.com/shay-te/core-lib/blob/master/LICENSE)
