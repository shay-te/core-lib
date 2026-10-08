---
id: files
title: Files
sidebar: core_lib_doc_sidebar
permalink: files.html
folder: core_lib_doc
toc: false
---

Three small wrappers around `requests` and `hashlib`: write an HTTP response to a file handle, download a URL to a file, and compute a file's MD5.

> **Optional utility.** You can use Core-Lib without them, and each is only a few lines over `requests` and `hashlib`. Their limits, stated once: `download_file` does not stream (the whole body is held in memory), and on an HTTP error it raises `requests.HTTPError` and leaves an empty file behind. `get_file_md5` reads the whole file into memory. For large files, call `requests.get(url, stream=True)` yourself and pass the response to `download_file_handle`.
>
> **Where it fits:** A Service or a [Client](client_base.html) that needs to download or check a file.

*core_lib.helpers.files* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/files.py){:target="_blank"}

## Functions

### download_file_handle()

*core_lib.helpers.files.download_file_handle()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/files.py#L7){:target="_blank"}

Writes a `requests.Response` into any writable file handle in 8 KB chunks: an open file, a temp file, an `io.BytesIO` buffer. It first calls `raise_for_status()`, so a 4xx or 5xx response raises `requests.HTTPError` before anything is written. It closes the response when it is done. Make the request with `stream=True`; without it, `requests` has already read the whole body into memory before this function sees it.

```python
def download_file_handle(file: Response, file_handle):
```

**Arguments**

- **`file`** *`(requests.Response)`*: An open `Response` object (should be made with `stream=True`).
- **`file_handle`**: Any writable object with a `write(bytes)` method.

**Example**

```python
import requests
from core_lib.helpers.files import download_file_handle

response = requests.get('https://example.com/report.pdf', stream=True)
with open('report.pdf', 'wb') as file_handle:
    download_file_handle(response, file_handle)
```

### download_file()

*core_lib.helpers.files.download_file()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/files.py#L15){:target="_blank"}

Downloads `path` with `requests.get` and writes it to `local_filename`. The response is not streamed, so the whole file is held in memory first. The output file is opened before the status is checked: on a 4xx or 5xx response it raises `requests.HTTPError` and leaves an empty `local_filename` behind.

```python
def download_file(path: str, local_filename: str):
```

**Arguments**

- **`path`** *`(str)`*: The URL to download.
- **`local_filename`** *`(str)`*: Where to save it.

**Example**

```python
from core_lib.helpers.files import download_file

download_file('https://example.com/report.pdf', 'report.pdf')  # saves report.pdf in the current directory
```


### get_file_md5()

*core_lib.helpers.files.get_file_md5()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/files.py#L21){:target="_blank"}

Returns the MD5 hash of a file as a hex string, for checking that a download is complete or that a file changed. It reads the whole file into memory in one go.

```python
def get_file_md5(file_name: str) -> str:
```

**Arguments**

- **`file_name`** *`(str)`*: Path of the file.

**Returns**

*`(str)`*: The MD5 hex digest of the file.

**Example**
```python
from core_lib.helpers.files import get_file_md5

with open('hello.txt', 'wb') as file_handle:
    file_handle.write(b'hello\n')

print(get_file_md5('hello.txt'))  # b1946ac92492d2347c6235b4d2611184
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="datetime_utils.html">Previous</a></button>
    <button class="pageNext-btn"><a href="function_utils.html">Next</a></button>
</div>