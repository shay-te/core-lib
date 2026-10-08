---
id: client_base
title: Client Base
sidebar: core_lib_doc_sidebar
permalink: client_base.html
folder: core_lib_doc
toc: false
---

Every client for an external HTTP API repeats the same setup: joining a base URL and a path, default headers, a timeout, auth, and a shared `requests.Session`. `ClientBase` does that setup. Your subclass lists the endpoints and decides how to encode request bodies and read responses.

**What it adds over `requests`:** not much, on purpose. It is a thin layer over one `requests.Session` (so connections are pooled and kept alive), with your headers, timeout and auth applied to every call. It does not encode bodies, parse responses or check status codes; you call `.json()` or `.raise_for_status()` yourself, as with plain `requests`.

> **Where it fits:** Client layer. A `ClientBase` subclass wraps one external HTTP API. `CoreLib.__init__` builds it, and `Service` classes call its domain methods, like `user_client.get(user_id)`.

*core_lib.client.client_base.ClientBase* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/client/client_base.py){:target="_blank"}

## Typical usage: subclass `ClientBase`

Each client in your app is a subclass of `ClientBase` with domain methods. The `_get` / `_post` / `_put` / `_delete` methods are protected: call them from inside the subclass, not from outside.

```python
from core_lib.client.client_base import ClientBase


class UserClient(ClientBase):
    def __init__(self, base_url: str, token: str):
        super().__init__(base_url)
        self.set_headers({'Authorization': f'Bearer {token}'})
        self.set_timeout(30)

    def get(self, user_id: int) -> dict:
        return self._get(f'/user/{user_id}').json()

    def create(self, data: dict) -> dict:
        return self._post('/user', json=data).json()

    def update(self, user_id: int, data: dict) -> dict:
        return self._put(f'/user/{user_id}', json=data).json()

    def delete(self, user_id: int) -> None:
        self._delete(f'/user/{user_id}')
```

With `UserClient('https://api.example.com/v1', token)`, `get(1)` sends `GET https://api.example.com/v1/user/1` with the `Authorization` header and a 30-second timeout. `create` and `update` send `data` as a JSON body because of `json=data`. Passing the dict as the second positional argument instead would send it form-encoded, which is what `requests` does with `data=`.

A `Service` then receives this client through `CoreLib.__init__` (see [Project Structure](project_structure.html)).

---

## Configuration methods

### `set_headers()`

*core_lib.client.client_base.ClientBase.set_headers()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/client/client_base.py){:target="_blank"}

Headers merged into every request.

```python
def set_headers(self, headers: dict):
```

- **`headers`** *`(dict)`*: Headers to add to every request. Headers passed to a single `_get` / `_post` / ... call are kept, but when both set the same header, the value set here wins.

### `set_timeout()`

*core_lib.client.client_base.ClientBase.set_timeout()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/client/client_base.py){:target="_blank"}

Default timeout for every request.

```python
def set_timeout(self, timeout: int):
```

- **`timeout`** *`(int)`*: Seconds before the request times out. A `timeout=` passed to a single call wins over this value. If you never set one, `requests` waits without a time limit.

### `set_auth()`

*core_lib.client.client_base.ClientBase.set_auth()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/client/client_base.py){:target="_blank"}

HTTP authentication for every request.

```python
def set_auth(self, auth: dict):
```

- **`auth`** *(tuple or `requests.auth.AuthBase`)*: Passed to `requests` as `auth=`, for example `('user', 'pass')` or `HTTPBasicAuth('user', 'pass')`. A plain dict does not work, even though the type hint in the source says `dict`. Once set, it replaces any `auth=` passed to a single call.

---

## Protected HTTP methods

These call the client's shared `requests.Session` (`self.session`) with your configured headers, timeout and auth. Call them from inside your `ClientBase` subclass. You can also use `self.session` directly, for example to mount a retry adapter.

### `_get(path, *args, **kwargs)`

Makes a `GET` request to the base URL joined with `path`. Returns a `requests.Response`.

### `_post(path, *args, **kwargs)`

Makes a `POST` request. Returns a `requests.Response`.

### `_put(path, *args, **kwargs)`

Makes a `PUT` request. Returns a `requests.Response`.

### `_delete(path, *args, **kwargs)`

Makes a `DELETE` request. Returns a `requests.Response`.

The URL is `base_url` without its trailing `/`, then `/`, then `path` without its leading `/`. So `'/user/1'` and `'user/1'` give the same URL, and a path in `base_url` (like `/v1`) is kept.

`*args` and `**kwargs` are passed on to the `requests.Session` method, so use the usual `requests` arguments: `params=` for the query string, `json=` for a JSON body, `data=` for a form body.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="join_config.html">Previous</a></button>
    <button class="pageNext-btn"><a href="error_handler.html">Next</a></button>
</div>
