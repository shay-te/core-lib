---
id: files
title: Files
sidebar: core_lib_doc_sidebar
permalink: files.html
folder: core_lib_doc
toc: false
---

This helper provides us with functions that help us to download and compare files.

*core_lib.helpers.files* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/files.py){:target="_blank"}

## Functions

### download_file()

*core_lib.helpers.files.download_file()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/files.py#L12){:target="_blank"}

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

download_file('https://path.to.file.pdf', 'mypdf.pdf') # will download ans save the file by name `mypdf.pdf`
```


### get_file_md5()

*core_lib.helpers.files.get_file_md5()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/files.py#L21){:target="_blank"}

Compares 2 given files of any type and returns `True` and `False` as per the outcome of the comparison.

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