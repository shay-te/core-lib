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
    file = requests.get(path)
    with open(local_filename, 'wb') as f:
        download_file_handle(file, f)


def get_file_md5(file_name: str) -> str:
    hasher = hashlib.md5()
    with open(file_name, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
        md5_str = hasher.hexdigest()
        return md5_str
