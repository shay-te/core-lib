---
id: client_base
title: Client Base
sidebar: core_lib_doc_sidebar
permalink: client_base.html
folder: core_lib_doc
toc: false
---

Every service that calls an external HTTP API repeats the same setup: base URL, auth headers, timeouts, request encoding, response parsing. `ClientBase` handles that boilerplate so each client just lists its endpoints.

> **Where it fits:** Client layer. A `ClientBase` subclass wraps one external HTTP API; `Service` classes receive that client and call domain methods like `billing.charge_customer()`.

*core_lib.client.client_base.ClientBase* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/client/client_base.py#L5){:target="_blank"}

## Typical usage: subclass `ClientBase`

Each `Client` in your app is a subclass of `ClientBase` that exposes domain-specific methods. The `_get` / `_post` / `_put` / `_delete` methods are protected — they're meant to be called from inside the subclass, not from outside.

```python
from core_lib.client.client_base import ClientBase


class UserClient(ClientBase):
    def __init__(self, base_url):
        super().__init__(base_url)
        self.set_headers({'Authorization': 'Bearer my-token'})
        self.set_timeout(30)

    def get(self, user_id: int) -> dict:
        return self._get(f'/user/{user_id}').json()

    def create(self, data: dict) -> dict:
        return self._post('/user', data).json()

    def update(self, user_id: int, data: dict) -> dict:
        return self._put(f'/user/{user_id}', data).json()

    def delete(self, user_id: int) -> None:
        self._delete(f'/user/{user_id}')
```

A `Service` then receives this client through `CoreLib.__init__` (see [Project Structure](/project_structure.html)).

---

## Configuration methods

### `set_headers()`

*core_lib.client.client_base.ClientBase.set_headers()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/client/client_base.py#L12){:target="_blank"}

Default headers attached to every request.

```python
def set_headers(self, headers: dict):
```

- **`headers`** *`(dict)`*: Headers to attach to every outgoing request.

### `set_timeout()`

*core_lib.client.client_base.ClientBase.set_timeout()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/client/client_base.py#L15){:target="_blank"}

Default timeout in seconds for every request.

```python
def set_timeout(self, timeout: int):
```

- **`timeout`** *`(int)`*: Seconds before the request times out.

### `set_auth()`

*core_lib.client.client_base.ClientBase.set_auth()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/client/client_base.py#L18){:target="_blank"}

HTTP authentication credentials attached to every request.

```python
def set_auth(self, auth: dict):
```

- **`auth`** *`(dict)`*: Auth credentials passed to `requests` (e.g. `HTTPBasicAuth`).

---

## Protected HTTP methods

These wrap the matching `requests.*` function with your configured headers, timeout, and auth. Call them from inside your `ClientBase` subclass.

### `_get(path, *args, **kwargs)`

Makes a `GET` request to `base_url + path`. Returns a `requests.Response`.

### `_post(path, *args, **kwargs)`

Makes a `POST` request. Returns a `requests.Response`.

### `_put(path, *args, **kwargs)`

Makes a `PUT` request. Returns a `requests.Response`.

### `_delete(path, *args, **kwargs)`

Makes a `DELETE` request. Returns a `requests.Response`.

`*args` and `**kwargs` are forwarded to the underlying `requests` function — use them for query params, JSON bodies, etc.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/sqlalchemy_types.html">Previous</a></button>
    <button class="pageNext-btn"><a href="/error_handler.html">Next</a></button>
</div>
