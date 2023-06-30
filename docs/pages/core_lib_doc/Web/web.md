---
id: web
title: Web Helpers
sidebar: core_lib_doc_sidebar
permalink: web.html
folder: core_lib_doc
toc: false
---

Web Helpers provides various response functions that help the users return data over a `Django` or `Flask` API.

# WebHelpersUtils

*core_lib.web_helpers.web_helprs_utils.WebHelpersUtils* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/web_helprs_utils.py#L4)

This class is used to set the type of web framework that will be utilized in the application i.e. `Django` or `Flask`.

## Functions

### init()

*core_lib.web_helpers.web_helprs_utils.WebHelpersUtils.init()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/web_helprs_utils.py#L13)

Used to set the server type used in the application, users must select the server type from the `ServerType` class provided by the `WebHelpersUtils` class.

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

- **`server_type`** *`(ServerType)`*: Sets the server type.

**Example**

```python
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
```

### get_server_type()

*core_lib.web_helpers.web_helprs_utils.WebHelpersUtils.get_server_type()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/web_helprs_utils.py#L17)

Returns the server type set by the `init()`.

```python
def get_server_type() -> ServerType:
```

**Returns**

*`(ServerType)`*: Server type `Django` or `Flask`.

**Example**

```python
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

WebHelpersUtils.get_server_type() # returns flask
```

# Request Response Helpers

Depending on the server type set in `WebHelpersUtils` class, request and response functions return data.

## Functions 

### response_status()

*core_lib.web_helpers.request_response_helpers.response_status()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/request_response_helpers.py#L14)

Returns empty data with [`HTTPStatus`](https://docs.python.org/3/library/http.html#http.HTTPStatus) value provided, as a response object.

```python
def response_status(status: int = HTTPStatus.OK.value):
```

**Arguments**

- **`status`** *`(int)`*: Default `HTTPStatus.OK.value`, `HTTPStatus` value to be set.

**Returns**

Returns response object with the set `status`.

**Example**

```python
from http import HTTPStatus

from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
from core_lib.web_helpers.request_response_helpers import response_status

WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

response_status(HTTPStatus.OK) # returns status 200 with empty data
response_status(HTTPStatus.INTERNAL_SERVER_ERROR) # returns status 500 with empty data
```


### response_ok()

*core_lib.web_helpers.request_response_helpers.response_ok()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/request_response_helpers.py#L18)

Returns message `ok` with [`HTTPStatus`](https://docs.python.org/3/library/http.html#http.HTTPStatus) value provided, as a response object.

```python
def response_ok(status: int = HTTPStatus.OK.value):
```

**Arguments**

- **`status`** *`(int)`*: Default `HTTPStatus.OK.value`, `HTTPStatus` value to be set.

**Returns**

Returns response object with the set `status` and message `ok`.

**Example**

```python
from http import HTTPStatus

from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
from core_lib.web_helpers.request_response_helpers import response_ok

WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

response_ok(HTTPStatus.OK) # returns status 200 with data {'message': 'ok'}
```

### response_message()

*core_lib.web_helpers.request_response_helpers.response_message()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/request_response_helpers.py#L22)

Returns message with [`HTTPStatus`](https://docs.python.org/3/library/http.html#http.HTTPStatus) value provided, as a response object.

```python
def response_message(message='', status: int = HTTPStatus.OK.value):
```

**Arguments**

- **`message`**: Default `''`, message to be sent in the response.
- **`status`** *`(int)`*: Default `HTTPStatus.OK.value`, `HTTPStatus` value to be set.

> If `HTTPStatus` is set to `500` the data will be returned in `error` key.

**Returns**

Returns response object with the set `status` and message.

**Example**

```python
from http import HTTPStatus

from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
from core_lib.web_helpers.request_response_helpers import response_message

WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

response_message('success', HTTPStatus.OK) # returns status 200 with data {'message': 'success'}
response_message('some error occurred', HTTPStatus.INTERNAL_SERVER_ERROR) # returns status 500 with data {'error': 'some error occurred'}
```

### response_json()

*core_lib.web_helpers.request_response_helpers.response_json()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/request_response_helpers.py#L22)

Returns message with [`HTTPStatus`](https://docs.python.org/3/library/http.html#http.HTTPStatus) value provided, and data transformed to JSON.

```python
def response_json(data: dict, status: int = HTTPStatus.OK.value):
```

**Arguments**

- **`data`** *`(dict)`*: Dictionary data to be sent in the response.
- **`status`** *`(int)`*: Default `HTTPStatus.OK.value`, `HTTPStatus` value to be set.

**Returns**

Returns response object with the set `status` and data transformed to JSON.

**Example**

```python
from http import HTTPStatus

from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
from core_lib.web_helpers.request_response_helpers import response_json

WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

response_json({'username': 'Jon Doe'}, HTTPStatus.OK) # returns status 200 with data {'username': 'Jon Doe'}
response_json({'error': 'Server Error'}, HTTPStatus.INTERNAL_SERVER_ERROR) # returns status 500 with data {'error': 'Server Error'}
response_json({'error': 'file not found'}, HTTPStatus.NOT_FOUND) # returns status 404 with data {'error': 'file not found'}
```
