def build_database_connection_string(protocol: str, username: str, password: str, host: str, port: str, database: str):
    if protocol == 'sqlite':
        return '{}:///{}'.format(protocol, database)
    else:
        return '{}://{}:{}@{}:{}/{}'.format(protocol, username, password, host, port, database)
