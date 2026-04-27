---
id: constants
title: Constants
sidebar: core_lib_doc_sidebar
permalink: constants.html
folder: core_lib_doc
toc: false
---

Hardcoded strings like `"application/json"` or `"Content-Type"` scattered through service code are error-prone and hard to refactor. These enums centralise the common HTTP and time constants so your code stays readable and typo-free.

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
from core_lib.helpers.constants import MediaType

response.headers['Content-Type'] = MediaType.APPLICATION_JSON.value
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

method = HttpMethod.GET.value  # 'GET'
```

## HttpHeaders

Common HTTP header name strings for use with `request.headers` or response builders.

```python
from core_lib.helpers.constants import HttpHeaders
```

| Member | Value |
|---|---|
| `ACCEPT` | `Accept` |
| `ACCEPT_CHARSET` | `Accept-Charset` |
| `ACCEPT_ENCODING` | `Accept-Encoding` |
| `ACCEPT_LANGUAGE` | `Accept-Language` |
| `ACCEPT_RANGERS` | `Accept-Ranges` |
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

**Example**

```python
from core_lib.helpers.constants import HttpHeaders

content_type = request.headers.get(HttpHeaders.CONTENT_TYPE.value)
```

## TimeUnit

Named time-unit constants used by cache TTL and scheduling configuration.

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

ttl_unit = TimeUnit.HOUR
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/thread.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/test_core_lib.html">Next >></a></button>
</div>
