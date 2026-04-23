---
id: web
title: Web Helpers
sidebar: core_lib_doc_sidebar
permalink: web.html
folder: core_lib_doc
toc: false
---

Django and Flask return responses differently. Web Helpers abstracts that difference so your service code doesn't need to know which framework is running. Set the server type once at startup, then use the same `response_json`, `response_ok`, and `response_status` functions everywhere.

# WebHelpersUtils

*core_lib.web_helpers.web_helprs_utils.WebHelpersUtils* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/web_helprs_utils.py#L4){:target="_blank"}

This class is used to set the type of web framework that will be utilized in the application i.e. `Django` or `Flask`.

## Functions

### init()

*core_lib.web_helpers.web_helprs_utils.WebHelpersUtils.init()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/web_helprs_utils.py#L13){:target="_blank"}

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

*core_lib.web_helpers.web_helprs_utils.WebHelpersUtils.get_server_type()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/web_helprs_utils.py#L17){:target="_blank"}

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

*core_lib.web_helpers.request_response_helpers.response_status()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/request_response_helpers.py#L14){:target="_blank"}

Returns empty data with [`HTTPStatus`](https://docs.python.org/3/library/http.html#http.HTTPStatus){:target="_blank"} value provided, as a response object.

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

*core_lib.web_helpers.request_response_helpers.response_ok()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/request_response_helpers.py#L18){:target="_blank"}

Returns message `ok` with [`HTTPStatus`](https://docs.python.org/3/library/http.html#http.HTTPStatus){:target="_blank"} value provided, as a response object.

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

*core_lib.web_helpers.request_response_helpers.response_message()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/request_response_helpers.py#L22){:target="_blank"}

Returns message with [`HTTPStatus`](https://docs.python.org/3/library/http.html#http.HTTPStatus){:target="_blank"} value provided, as a response object.

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

*core_lib.web_helpers.request_response_helpers.response_json()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/request_response_helpers.py#L22){:target="_blank"}

Returns message with [`HTTPStatus`](https://docs.python.org/3/library/http.html#http.HTTPStatus){:target="_blank"} value provided, and data transformed to JSON.

```python
def response_json(data: Union[dict, list], status: int = HTTPStatus.OK.value):
```

**Arguments**

- **`data`** *`(dict, list)`*: Data to be sent in the response — either a dict or a list.
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

### response_error()

*core_lib.web_helpers.request_response_helpers.response_error()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/request_response_helpers.py){:target="_blank"}

Returns an error response. Wraps the message in `{'error': message}` and defaults to status 500. If no message is provided, uses the standard HTTP reason phrase for the given status code.

```python
def response_error(message='', status: int = HTTPStatus.INTERNAL_SERVER_ERROR.value):
```

**Arguments**

- **`message`**: Default `''`, error message to send. Falls back to the HTTP reason phrase if empty.
- **`status`** *`(int)`*: Default `HTTPStatus.INTERNAL_SERVER_ERROR.value`, HTTP status code.

**Example**

```python
from http import HTTPStatus

from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
from core_lib.web_helpers.request_response_helpers import response_error

WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

response_error('something went wrong')  # status 500, {'error': 'something went wrong'}
response_error(status=HTTPStatus.BAD_REQUEST)  # status 400, {'error': 'Bad Request'}
```

### request_body_dict()

*core_lib.web_helpers.request_response_helpers.request_body_dict()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/request_response_helpers.py){:target="_blank"}

Parses the request body as JSON and returns it as a dict. Works transparently with both Django and Flask request objects.

```python
def request_body_dict(request):
```

**Arguments**

- **`request`**: The framework request object (Django `HttpRequest` or Flask `Request`).

**Returns**

*`(dict)`*: The parsed JSON body.

**Example**

```python
from core_lib.web_helpers.request_response_helpers import request_body_dict

def create_user(request):
    data = request_body_dict(request)
    return response_json(core_lib.user.create(data))
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/handle_exceptions.html"><< Previous</a></button>
</div>