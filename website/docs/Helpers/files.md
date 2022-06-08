---
id: files
title: Files
sidebar_label: Files
---

This helper provides us with functions that help us to download and compare files.

*core_lib.helpers.files* [[source]](https://github.com/shay-te/core-lib/blob/massive-update/core_lib/helpers/files.py)

## Functions

### download_file()

*core_lib.helpers.files.download_file()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/helpers/files.py#L12)

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


### compare_files_md5()

*core_lib.helpers.files.compare_files_md5()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/helpers/files.py#L17)

Compares 2 given files of any type and returns `True` and `False` as per the outcome of the comparison.

```python
def compare_files_md5(file_1: str, file_2: str) -> bool:
```

**Arguments**

- **`file_1`** *`(str)`*: Path of the first file.
- **`file_2`** *`(str)`*: Path of the second file.

**Returns**

*`(bool)`*: Returns `True` and `False` as per the outcome of the comparison.

**Example**
```python
from core_lib.helpers.files import compare_files_md5

compare_files_md5(path_to_file_1, path_to_file_2) # True if both contain the same data else False
```
