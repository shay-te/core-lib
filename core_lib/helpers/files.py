import hashlib


def download_file_handle(request, file_handle):
    with request as r: # NOTE the stream=True parameter below
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:  # filter out keep-alive new chunks
                file_handle.write(chunk)


def download_file(request, local_filename):
    with open(local_filename, 'wb') as f:
        download_file_handle(request, f)


def compare_files_md5(file_1, file_2):
    digests = []
    for filename in [file_1, file_2]:
        hasher = hashlib.md5()
        with open(filename, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
            a = hasher.hexdigest()
            digests.append(a)
    return digests[0] == digests[1]