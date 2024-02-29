---
id: client_base
title: Client Base
sidebar: core_lib_doc_sidebar
permalink: client_base.html
folder: core_lib_doc
toc: false
---

*core_lib.client.client_base.ClientBase* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/client/client_base.py#L5){:target="_blank"}

`Client Base` class provides functions by which we can interface with the `HTTP` APIs.

## Initializing

```python
def __init__(self, base_url):
```

**Arguments**

- **`base_url`**: Base URL of the API to be used.

**Example**

```python
from core_lib.client.client_base import ClientBase

client = ClientBase('https://example.com/')
```

## Functions

### _get()

*core_lib.client.client_base.ClientBase._get()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/client/client_base.py#L18){:target="_blank"}

Will make a `GET` request to the path provided. Used to fetch data.

```python
def _get(self, path: str, *args, **kwargs) -> Response:
```

**Arguments**

- **`path`** *`(str)`*: The API path to make the request.
- __*args, **kwargs__: The args and kwargs of the function, if the API accepts some parameters, will be passed to the `requests.get` function.

**Returns**

*`(Response)`*: The response object is returned by the API.

**Example**

```python
from core_lib.client.client_base import ClientBase

client = ClientBase('https://example.com/')
user_data = client._get('user/1')
print(user_data) # will print the response returned by the API.
```

### _put()

*core_lib.client.client_base.ClientBase._put()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/client/client_base.py#L21){:target="_blank"}

Will make a `PUT` request to the path provided. Used to create or replace data.

```python
def _put(self, path: str, *args, **kwargs) -> Response:
```

**Arguments**

- **`path`** *`(str)`*: The API path to make the request.
- __*args, **kwargs__: The args and kwargs of the function, if the API accepts some parameters, will be passed to the `requests.put` function.

**Returns**

*`(Response)`*: The response object is returned by the API.

**Example**

```python
from core_lib.client.client_base import ClientBase

client = ClientBase('https://example.com/')
data = client._put('update/user', {'id': 1 , 'username': 'Jon Doe'})
print(data) # will print the response returned by the API.
```

### _post()

*core_lib.client.client_base.ClientBase._post()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/client/client_base.py#L24){:target="_blank"}

Will make a `POST` request to the path provided. Used to send data to the backend.

```python
def _post(self, path: str, *args, **kwargs) -> Response:
```

**Arguments**

- **`path`** *`(str)`*: The API path to make the request.
- __*args, **kwargs__: The args and kwargs of the function, if the API accepts some parameters, will be passed to the `requests.post` function.

**Returns**

*`(Response)`*: The response object is returned by the API.

**Example**

```python
from core_lib.client.client_base import ClientBase

client = ClientBase('https://example.com/')
data = client._post('create/user', {'username': 'Jon Doe', 'password': 'password',...})
print(data) # will print the response returned by the API.
```

### _delete()

*core_lib.client.client_base.ClientBase._delete()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/client/client_base.py#L24){:target="_blank"}

Will make a `DELETE` request to the path provided. Used to delete data.

```python
def _delete(self, path: str, *args, **kwargs) -> Response:
```

**Arguments**

- **`path`** *`(str)`*: The API path to make the request.
- __*args, **kwargs__: The args and kwargs of the function, if the API accepts some parameters, will be passed to the `requests.delete` function.

**Returns**

*`(Response)`*: The response object is returned by the API.

**Example**

```python
from core_lib.client.client_base import ClientBase

client = ClientBase('https://example.com/')
data = client._delete('user/1')
print(data) # will print the response returned by the API.
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/soft_delete.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/error_handler.html">Next >></a></button>
</div>