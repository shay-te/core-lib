---
id: constants
title: Constants
sidebar: core_lib_doc_sidebar
permalink: constants.html
folder: core_lib_doc
toc: false
---

Enums for strings that HTTP code repeats: MIME types (`MediaType`), HTTP methods (`HttpMethod`) and header names (`HttpHeaders`), plus a `TimeUnit` enum. Writing `HttpHeaders.CONTENT_TYPE.value` instead of `'Content-Type'` turns a typo into an `AttributeError` instead of a header nobody reads.

> **Optional utility.** You can use Core-Lib without these. The one place Core-Lib itself expects them is the [web helpers](web.html), which take a `MediaType` member for the response content type.
>
> **Where it fits:** Anywhere HTTP strings appear, most often in web routes and in `Client` subclasses.

These are plain `enum.Enum` classes, not string enums. A member is not equal to its string (`MediaType.APPLICATION_JSON == 'application/json'` is `False`), so use `.value` wherever a string is expected.

*core_lib.helpers.constants* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/constants.py){:target="_blank"}

## MediaType

MIME type strings for use in `Content-Type` and `Accept` headers.

```python
from core_lib.helpers.constants import MediaType
```

| Member | Value |
|---|---|
| `MEDIA_TYPE_WILDCARD` | `*` |
| `WILDCARD` | `*/*` |
| `APPLICATION_XML` | `application/xml` |
| `APPLICATION_ATOM_XML` | `application/atom+xml` |
| `APPLICATION_XHTML_XML` | `application/xhtml+xml` |
| `APPLICATION_SVG_XML` | `application/svg+xml` |
| `APPLICATION_JSON` | `application/json` |
| `APPLICATION_FORM_URLENCODED` | `application/x-www-form-urlencoded` |
| `APPLICATION_JSON_PATCH_JSON` | `application/json-patch+json` |
| `APPLICATION_OCTET_STREAM` | `application/octet-stream` |
| `APPLICATION_PDF` | `application/pdf` |
| `MULTIPART_FORM_DATA` | `multipart/form-data` |
| `TEXT_PLAIN` | `text/plain` |
| `TEXT_XML` | `text/xml` |
| `TEXT_HTML` | `text/html` |
| `SERVER_SENT_EVENTS` | `text/event-stream` |
| `IMAGE_JPEG` | `image/jpeg` |
| `IMAGE_PNG` | `image/png` |

**Example**

```python
from core_lib.helpers.constants import HttpHeaders, MediaType

headers = {HttpHeaders.CONTENT_TYPE.value: MediaType.APPLICATION_JSON.value}
print(headers)  # {'Content-Type': 'application/json'}
```

Core-Lib's web helpers take the member itself, not `.value`:

```python
from flask import Flask

from core_lib.helpers.constants import HttpHeaders, MediaType
from core_lib.web_helpers.request_response_helpers import response_download_content
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
flask_app = Flask(__name__)


@flask_app.route('/report')
def report():
    return response_download_content(b'report bytes', MediaType.APPLICATION_PDF, 'report.pdf')


response = flask_app.test_client().get('/report')
print(response.headers[HttpHeaders.CONTENT_TYPE.value])         # application/pdf
print(response.headers[HttpHeaders.CONTENT_DISPOSITION.value])  # attachment; filename="report.pdf"
```

## HttpMethod

Standard HTTP verb strings.

```python
from core_lib.helpers.constants import HttpMethod
```

| Member | Value |
|---|---|
| `GET` | `GET` |
| `POST` | `POST` |
| `DELETE` | `DELETE` |
| `PUT` | `PUT` |

**Example**

```python
from core_lib.helpers.constants import HttpMethod

method = HttpMethod.GET.value
print(method)  # GET
```

## HttpHeaders

Common HTTP header names, for reading request headers or building response headers.

```python
from core_lib.helpers.constants import HttpHeaders
```

| Member | Value |
|---|---|
| `ACCEPT` | `Accept` |
| `ACCEPT_CHARSET` | `Accept-Charset` |
| `ACCEPT_ENCODING` | `Accept-Encoding` |
| `ACCEPT_LANGUAGE` | `Accept-Language` |
| `ACCEPT_RANGES` | `Accept-Ranges` |
| `ACCESS_CONTROL_ALLOW_CREDENTIALS` | `Access-Control-Allow-Credentials` |
| `ACCESS_CONTROL_ALLOW_HEADERS` | `Access-Control-Allow-Headers` |
| `ACCESS_CONTROL_ALLOW_METHODS` | `Access-Control-Allow-Methods` |
| `ACCESS_CONTROL_ALLOW_ORIGIN` | `Access-Control-Allow-Origin` |
| `ACCESS_CONTROL_EXPOSE_HEADERS` | `Access-Control-Expose-Headers` |
| `ACCESS_CONTROL_MAX_AGE` | `Access-Control-Max-Age` |
| `ACCESS_CONTROL_REQUEST_HEADERS` | `Access-Control-Request-Headers` |
| `ACCESS_CONTROL_REQUEST_METHOD` | `Access-Control-Request-Method` |
| `ALLOW` | `Allow` |
| `AUTHORIZATION` | `Authorization` |
| `CACHE_CONTROL` | `Cache-Control` |
| `CONNECTION` | `Connection` |
| `CONTENT_ENCODING` | `Content-Encoding` |
| `CONTENT_DISPOSITION` | `Content-Disposition` |
| `CONTENT_LANGUAGE` | `Content-Language` |
| `CONTENT_LENGTH` | `Content-Length` |
| `CONTENT_LOCATION` | `Content-Location` |
| `CONTENT_RANGE` | `Content-Range` |
| `CONTENT_TYPE` | `Content-Type` |

`HttpHeaders.ACCEPT_RANGERS` (an old misspelling) still works. It is an alias of `ACCEPT_RANGES`: the same member, so `HttpHeaders.ACCEPT_RANGERS is HttpHeaders.ACCEPT_RANGES` is `True` and its `.name` is `'ACCEPT_RANGES'`. Use `ACCEPT_RANGES` in new code.

**Example**

```python
from core_lib.helpers.constants import HttpHeaders, MediaType

request_headers = {HttpHeaders.ACCEPT.value: MediaType.APPLICATION_JSON.value}
print(request_headers)  # {'Accept': 'application/json'}
```

## TimeUnit

An integer-coded time-unit enum, provided for your own code. **Nothing in Core-Lib reads it.** Do not pass it where Core-Lib expects a duration: `@Cache(expire=...)` takes a `timedelta` or a string such as `'1 hour'` (see [Cache](cache.html)), and job `initial_delay` / `frequency` are strings such as `'5m'` (see [Jobs](job.html)). `@Cache(expire=TimeUnit.HOUR)` does not work: with the RAM cache handler, the second call to the method raises `TypeError`.

```python
from core_lib.helpers.constants import TimeUnit
```

| Member | Value |
|---|---|
| `SECOND` | `101` |
| `MINUTE` | `102` |
| `HOUR` | `103` |
| `DAY` | `104` |
| `WEEK` | `105` |
| `MONTH` | `106` |
| `YEAR` | `107` |

**Example**

```python
from core_lib.helpers.constants import TimeUnit

print(TimeUnit.HOUR.value)  # 103
print(TimeUnit(103))        # TimeUnit.HOUR
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="thread.html">Previous</a></button>
    <button class="pageNext-btn"><a href="test_core_lib.html">Next</a></button>
</div>
