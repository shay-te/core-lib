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


def compare_files_md5(file_1: str, file_2: str) -> bool:
    digests = []
    for filename in [file_1, file_2]:
        hasher = hashlib.md5()
        with open(filename, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
            a = hasher.hexdigest()
            digests.append(a)
    return digests[0] == digests[1]
