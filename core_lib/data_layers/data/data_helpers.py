
def build_url(protocol: str = None, username: str = None, password: str = None, host: str = None, port: str = None, path: str = None, file: str = None, *args, **kwargs):
    result = []
    if protocol:
        result.append(protocol)
        result.append('://')

    if username or password:
        if username:
            result.append(username)
            if password:
                result.append(':{}'.format(password))
        result.append('@')

    if host:
        result.append(host)

    if port:
        result.append(':{}'.format(port))

    if path:
        result.append('/{}'.format(path.lstrip('/')))

    if file:
        result.append('/{}'.format(file.lstrip('/')))

    return ''.join(result)
