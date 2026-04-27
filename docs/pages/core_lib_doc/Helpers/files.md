---
id: files
title: Files
sidebar: core_lib_doc_sidebar
permalink: files.html
folder: core_lib_doc
toc: false
---

Downloading files over HTTP and computing checksums are repetitive tasks with fiddly edge cases — temp files, stream handling, hash encoding. These helpers cover the common patterns so you don't re-implement them.

*core_lib.helpers.files* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/files.py){:target="_blank"}

## Functions

### download_file_handle()

*core_lib.helpers.files.download_file_handle()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/files.py#L7){:target="_blank"}

Streams a `requests.Response` object into any writable file handle in 8 KB chunks. Use this when you already have a `Response` and need to write to something other than a plain file — a temp file, an in-memory buffer, or an open socket.

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

response = requests.get('https://path.to.file.pdf', stream=True)
with open('output.pdf', 'wb') as fh:
    download_file_handle(response, fh)
```

### download_file()

*core_lib.helpers.files.download_file()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/files.py#L15){:target="_blank"}

Downloads the file provided at the specific URL and saves it by the specified name.

```python
def download_file(path: str, local_filename: str):
```

**Arguments**

- **`path`** *`(str)`*: The URL path at which the file is located.
- **`local_filename`** *`(str)`*: Name of the downloaded file.

**Example**

```python
from core_lib.helpers.files import download_file

download_file('https://path.to.file.pdf', 'mypdf.pdf') # will download and save the file by name `mypdf.pdf`
```


### get_file_md5()

*core_lib.helpers.files.get_file_md5()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/files.py#L21){:target="_blank"}

Returns the MD5 hash of the given file as a hex string. Useful for verifying file integrity or detecting changes.

```python
def get_file_md5(file_name: str) -> str:
```

**Arguments**

- **`file_name`** *`(str)`*: Path of the file.

**Returns**

*`(str)`*: Returns `md5` hash for the given file.

**Example**
```python
from core_lib.helpers.files import get_file_md5

get_file_md5(path_to_file) # returns md5 hash string of the file
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/datetime_utils.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/function_utils.html">Next >></a></button>
</div>