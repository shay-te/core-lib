---
id: web
title: Web Helpers
sidebar: core_lib_doc_sidebar
permalink: web.html
folder: core_lib_doc
toc: false
---

Web Helpers are small functions that build HTTP responses (`response_json`, `response_ok`, `response_status`, ...) and read request bodies. Flask and Django use different response classes; you tell Core-Lib once at startup which framework you run, and the same helper calls then return the right response object. [`@HandleException`](handle_exceptions.html) and [`@RequireLogin`](user_security.html) use these helpers too.

Use them in your route handlers. Keep business logic in `Service` classes; a view reads the request, calls your `CoreLib` object, and returns a response built with these helpers.

**Supported frameworks: Flask and Django only.** Both are installed as dependencies of Core-Lib, whichever one you use. On FastAPI or any other framework, call your `CoreLib` object from your routes and build responses with that framework's own tools; there is no Core-Lib helper for it.

> **Where it fits:** Web edge only. Route handlers call these to build framework-specific responses; Services and DataAccess never touch them.

## WebHelpersUtils

*core_lib.web_helpers.web_helprs_utils.WebHelpersUtils* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/web_helprs_utils.py){:target="_blank"}

Stores which web framework, Flask or Django, the helpers should build responses for. The setting is a class attribute: one value for the whole process. Call `init()` once at startup, before any `response_*` helper, `@HandleException` or `@RequireLogin` builds a response.

### `init()`

*core_lib.web_helpers.web_helprs_utils.WebHelpersUtils.init()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/web_helprs_utils.py){:target="_blank"}

Sets the server type. Pass a member of `WebHelpersUtils.ServerType`.

**ServerType Class**

```python
class ServerType(enum.Enum):
    FLASK = 'flask'
    DJANGO = 'django'
```

```python
def init(server_type: ServerType):
```

**Arguments**

- **`server_type`** *`(ServerType)`*: `WebHelpersUtils.ServerType.FLASK` or `WebHelpersUtils.ServerType.DJANGO`.

**Example**

```python
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
```

### `get_server_type()`

*core_lib.web_helpers.web_helprs_utils.WebHelpersUtils.get_server_type()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/web_helprs_utils.py){:target="_blank"}

Returns the server type set by `init()`. Raises `ValueError('WebHelpersUtils never initialized')` if `init()` was not called. Every helper on this page calls it, so they all raise that error until `init()` runs.

```python
def get_server_type() -> ServerType:
```

**Returns**

*`(ServerType)`*: `WebHelpersUtils.ServerType.FLASK` or `WebHelpersUtils.ServerType.DJANGO`.

**Example**

```python
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
WebHelpersUtils.get_server_type()  # WebHelpersUtils.ServerType.FLASK
```

## Request / response helpers

Each `response_*` function returns a Flask `Response` or a Django `HttpResponse`, depending on the server type set with `WebHelpersUtils.init()`. Return it from your view.

All examples below assume `WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)` has run. The comments show the status and the response body.

### `response_status()`

*core_lib.web_helpers.request_response_helpers.response_status()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/request_response_helpers.py){:target="_blank"}

Returns a response with the given [`HTTPStatus`](https://docs.python.org/3/library/http.html#http.HTTPStatus){:target="_blank"} and an empty body.

```python
def response_status(status: int = HTTPStatus.OK.value):
```

**Arguments**

- **`status`** *`(int)`*: Default `200`. An `HTTPStatus` member or a plain int.

**Example**

```python
from http import HTTPStatus

from core_lib.web_helpers.request_response_helpers import response_status

response_status(HTTPStatus.OK)                     # 200, empty body
response_status(HTTPStatus.INTERNAL_SERVER_ERROR)  # 500, empty body
```

### `response_ok()`

*core_lib.web_helpers.request_response_helpers.response_ok()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/request_response_helpers.py){:target="_blank"}

Returns the message `ok` as JSON, with the given status.

```python
def response_ok(status: int = HTTPStatus.OK.value):
```

**Arguments**

- **`status`** *`(int)`*: Default `200`.

**Example**

```python
from http import HTTPStatus

from core_lib.web_helpers.request_response_helpers import response_ok

response_ok()                    # 200, {"message": "ok"}
response_ok(HTTPStatus.CREATED)  # 201, {"message": "ok"}
```

### `response_message()`

*core_lib.web_helpers.request_response_helpers.response_message()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/request_response_helpers.py){:target="_blank"}

Returns a message as JSON, with the given status. For a status of 500 or above the message is under the key `error`; otherwise it is under `message`. If `message` is empty, the standard reason phrase for the status is used.

```python
def response_message(message='', status: int = HTTPStatus.OK.value):
```

**Arguments**

- **`message`** *`(str)`*: Default `''`. The message to send.
- **`status`** *`(int)`*: Default `200`.

**Example**

```python
from http import HTTPStatus

from core_lib.web_helpers.request_response_helpers import response_message

response_message('success', HTTPStatus.OK)                                 # 200, {"message": "success"}
response_message('some error occurred', HTTPStatus.INTERNAL_SERVER_ERROR)  # 500, {"error": "some error occurred"}
response_message(status=HTTPStatus.NOT_FOUND)                              # 404, {"message": "Not Found"}
```

### `response_json()`

*core_lib.web_helpers.request_response_helpers.response_json()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/request_response_helpers.py){:target="_blank"}

Returns `data` serialized as JSON (with `json.dumps`), with the given status and the `application/json` content type.

```python
def response_json(data: Union[dict, list], status: int = HTTPStatus.OK.value):
```

**Arguments**

- **`data`** *`(dict, list)`*: The data to send. It must be JSON-serializable; the dicts your services return through `@ResultToDict` are.
- **`status`** *`(int)`*: Default `200`.

**Example**

```python
from http import HTTPStatus

from core_lib.web_helpers.request_response_helpers import response_json

response_json({'username': 'Jon Doe'})                         # 200, {"username": "Jon Doe"}
response_json([1, 2, 3])                                       # 200, [1, 2, 3]
response_json({'error': 'file not found'}, HTTPStatus.NOT_FOUND)  # 404, {"error": "file not found"}
```

### `response_error()`

*core_lib.web_helpers.request_response_helpers.response_error()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/request_response_helpers.py){:target="_blank"}

Returns `{"error": message}` as JSON, with status 500 by default. If `message` is empty, the standard reason phrase for the status is used. Unlike `response_message()`, the key is always `error`, whatever the status.

```python
def response_error(message='', status: int = HTTPStatus.INTERNAL_SERVER_ERROR.value):
```

**Arguments**

- **`message`** *`(str)`*: Default `''`. The error message.
- **`status`** *`(int)`*: Default `500`.

**Example**

```python
from http import HTTPStatus

from core_lib.web_helpers.request_response_helpers import response_error

response_error('something went wrong')         # 500, {"error": "something went wrong"}
response_error(status=HTTPStatus.BAD_REQUEST)  # 400, {"error": "Bad Request"}
```

### `response_download_content()`

*core_lib.web_helpers.request_response_helpers.response_download_content()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/request_response_helpers.py){:target="_blank"}

Returns `content` as a file download: status 200, the given content type, and a `Content-Disposition: attachment; filename="..."` header.

```python
def response_download_content(content, media_type: MediaType, file_name: str):
```

**Arguments**

- **`content`** *`(bytes or str)`*: The file content.
- **`media_type`** *`(MediaType)`*: The content type, from [`core_lib.helpers.constants.MediaType`](constants.html).
- **`file_name`** *`(str)`*: The file name the browser saves it as.

**Example**

```python
from core_lib.helpers.constants import MediaType
from core_lib.web_helpers.request_response_helpers import response_download_content

response_download_content(b'id,email\n1,ada@example.com\n', MediaType.TEXT_PLAIN, 'users.csv')
# 200, Content-Type: text/plain, Content-Disposition: attachment; filename="users.csv"
```

### `request_body_dict()`

*core_lib.web_helpers.request_response_helpers.request_body_dict()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/request_response_helpers.py){:target="_blank"}

Returns the request's JSON body as a dict (or list), for either framework.

```python
def request_body_dict(request):
```

**Arguments**

- **`request`**: The framework's request object: Flask's `flask.request`, or the Django `HttpRequest` your view receives.

**Returns**

*`(dict)`*: The parsed JSON body.

- **Flask:** returns `request.json`. If the body is not sent as `application/json`, or is not valid JSON, Flask raises its own 415 or 400 error.
- **Django:** parses `request.body` with `json.loads`. An empty or invalid body raises `json.JSONDecodeError`.

Under `@HandleException`, both of these become a 500 response (see [What the client gets](handle_exceptions.html#what-the-client-gets)).

**Example**

`core_lib` is your `CoreLib` instance, and `core_lib.user.create()` is your user service's method.

```python
# Flask: the view takes no request argument; import flask.request
from flask import request

from core_lib.web_helpers.request_response_helpers import request_body_dict, response_json


@app.route('/users', methods=['POST'])
def create_user():
    data = request_body_dict(request)
    return response_json(core_lib.user.create(data))
```

```python
# Django: the view receives the request
from core_lib.web_helpers.request_response_helpers import request_body_dict, response_json


def create_user(request):
    data = request_body_dict(request)
    return response_json(core_lib.user.create(data))
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="handle_exceptions.html">Previous</a></button>
</div>
