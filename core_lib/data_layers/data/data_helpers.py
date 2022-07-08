def build_url(
    protocol: str = None,
    username: str = None,
    password: str = None,
    host: str = None,
    port: int = None,
    path: str = None,
    file: str = None,
    *args,
    **kwargs,
) -> str:
    result = []
    if protocol:
        result.append(protocol)
        result.append('://')

    if username or password:
        if username:
            result.append(username)
            if password:
                result.append(f':{password}')
        result.append('@')

    if host:
        result.append(host)

    if port:
        result.append(f':{port}')

    if path:
        result.append('/{}'.format(path.lstrip('/')))

    if file:
        result.append('/{}'.format(file.lstrip('/')))

    return ''.join(result)
