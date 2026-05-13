import hashlib

import requests
from requests import Response


def download_file_handle(file: Response, file_handle):
    with file as r:  # NOTE the stream=True parameter below
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:  # filter out keep-alive new chunks
                file_handle.write(chunk)


def download_file(path: str, local_filename: str):
    # `stream=True` — previously the whole response was buffered into memory
    # before iter_content() chunked it, OOM-risking large downloads.
    file = requests.get(path, stream=True)
    with open(local_filename, 'wb') as f:
        download_file_handle(file, f)


def get_file_md5(file_name: str) -> str:
    # Stream in 64-KiB chunks instead of `buf = f.read()` (the previous
    # implementation loaded the entire file into memory before hashing —
    # an OOM risk on multi-GB files).
    hasher = hashlib.md5()
    with open(file_name, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            hasher.update(chunk)
    return hasher.hexdigest()
