def build_database_connection_string(protocol: str, username: str, password: str, host: str, port: str, datebase: str):
    if protocol == 'sqlite':
        return '{}:///{}'.format(protocol, datebase)
    else:
        return '{}://{}:{}@{}:{}/{}'.format(protocol, username, password, host, port, datebase)
