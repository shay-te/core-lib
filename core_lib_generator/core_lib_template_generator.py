import enum

from core_lib.helpers.shell_utils import input_enum, input_str, input_yes_no, input_int, input_list


class DBTypes(enum.Enum):
    __order__ = 'SQLite Postgresql MySQL Oracle MSSQL Firebird Sybase'
    SQLite = 1
    Postgresql = 2
    MySQL = 3
    Oracle = 4
    MSSQL = 5
    Firebird = 6
    Sybase = 7


class DBDatatypes(enum.Enum):
    __order__ = 'INTEGER VARCHAR DATETIME DATE BOOLEAN'
    INTEGER = 1
    VARCHAR = 2
    DATETIME = 3
    DATE = 4
    BOOLEAN = 5


class CacheTypes(enum.Enum):
    __order__ = 'Memcached Memory Empty'
    Memcached = 1
    Memory = 2
    Empty = 3


class DataAccessTypes(enum.Enum):
    CRUD = 1
    SoftDelete = 2
    SoftDeleteToken = 3
    CRUDSoftDelete = 4
    CRUDSoftDeleteToken = 5


def generate_db_template() -> dict:
    db_name = input_str('What is the name of the DB connection?')

    db_type = input_enum(
        DBTypes, 'for DB type'
    )

    if db_type == DBTypes.SQLite.value:
        in_memory = input_yes_no('Do you want the SQLite DB in memory?', True)
        if in_memory:
            db_log_queries = input_yes_no('Do you want to log queries?', False)
            db_create = input_yes_no('Do you want create Database?', True)
            db_pool_recycle = input_str('Enter the pool recycle time: ', 3200)
            db_pool_pre_ping = input_yes_no('Do you want to set pool pre ping?', False)
            print('\nSQLite created in memory.')
            return {
                'log_queries': db_log_queries,
                'create_db': db_create,
                'session': {
                    'pool_recycle': db_pool_recycle,
                    'pool_pre_ping': db_pool_pre_ping,
                },
                'url': {
                    'protocol': db_type,
                },
            }
    default_db_ports = {
        DBTypes.SQLite.name: None,
        DBTypes.Postgresql.name: 5432,
        DBTypes.MySQL.name: 3306,
        DBTypes.Oracle.name: 1521,
        DBTypes.MSSQL.name: 1433,
        DBTypes.Firebird.name: 3050,
        DBTypes.Sybase.name: 5000,
    }
    db_port = input_int('Enter the port no. of your DB', default_db_ports[DBTypes(db_type).name])
    db_host = input_str('Enter host of your DB', 'localhost')
    db_username = input_str('Enter your DB username', 'user')
    db_password = input_str('Enter your DB password', 'password')
    print(f'\n{db_type} with {db_host}:{db_port} created')
    return {
        'env': {
            f'{db_name.upper()}_USER': db_username,
            f'{db_name.upper()}_PASSWORD': db_password,
            f'{db_name.upper()}_PORT': db_port,
            f'{db_name.upper()}_DB': db_name,
            f'{db_name.upper()}_HOST': db_host,
        },
        'config': {
            'protocol': DBTypes(db_type).name.lower(),
            'username': db_username,
            'password': db_password,
            'host': db_host,
            'port': db_port,
            'file': db_name,
        },
    }


def generate_solr_template() -> dict:
    solr_protocol = input_str('Enter solr protocol (http/https)', 'https')
    solr_port = input_str('Enter solr port no.', 8983)
    solr_host = input_str('Enter solr host', 'localhost')
    solr_file = input_str('Enter solr file name (solr/core_name)', 'solr/mycore')
    print('\nInput recorded.')
    return {
        'env': {
            'SOLR_HOST': solr_host,
            'SOLR_PORT': solr_port,
        },
        'config': {
            'protocol': solr_protocol,
            'host': solr_host,
            'port': solr_port,
            'file': solr_file,
        },
    }


def generate_cache_template() -> dict:
    cache_type = input_enum(CacheTypes, 'for cache type')

    if cache_type == 1:
        memcache_port = input_int('Enter your memcached server port no.', 11211)
        memcache_host = input_str('Enter your memcached server host', 'localhost')
        print(f'\nCache type {CacheTypes(cache_type).name} on {memcache_host}:{memcache_port}')
        return {
            'env': {
                'MEMCACHED_HOST': memcache_host,
                'MEMCACHED_PORT': memcache_port,
            },
            'config': {
                'type': CacheTypes(cache_type).name.lower(),
                'host': memcache_host,
                'port': memcache_port,
            },
        }
    elif cache_type == 2:
        print(f'\nCache type {CacheTypes(cache_type).name}')
        return {
            'config': {
                'type': CacheTypes(cache_type).name.lower(),
            }
        }
    else:
        print('\nNo cache set.')


def generate_db_entity_template() -> dict:
    column_count = input_int('How many columns will you have in your table? ', 0)
    entities = {}
    for i in range(0, column_count):
        column_name = input_str(f'{i + 1}. Enter the name of column: ')

        column_type = input_enum(DBDatatypes, f'{i + 1}. for datatype: ')

        column_default = input_str(f'{i + 1}. Enter the default value of column: ', ' ')

        entities[i] = {'name': column_name, 'type': column_type, 'default': column_default}

    is_soft_delete = input_yes_no('Do you want to implement Soft Delete?', False)
    if is_soft_delete:
        is_soft_delete_token = input_yes_no('Do you want to implement Soft Delete Token?', False)
    else:
        is_soft_delete_token = False

    return {
        'entities': entities,
        'is_soft_delete': is_soft_delete,
        'is_soft_delete_token': is_soft_delete_token,
    }


def generate_data_access_template(entities: list) -> dict:
    data_access_name = input_str('Please enter the name of the data access you\'d want to create: ', 'UserDataAccess')

    data_access_type = input_enum(DataAccessTypes, 'for data access type')

    data_access_crud_entity = None
    if data_access_type in [DataAccessTypes.CRUD.value, DataAccessTypes.CRUDSoftDelete.value,
                            DataAccessTypes.CRUDSoftDeleteToken.value]:
        data_access_crud_entity = input_list(entities, 'of entity to apply crud on')
    create_service = input_yes_no('Do you want to create a service for the data access?', False)

    return {
        'name': data_access_name,
        'type': DataAccessTypes(data_access_type).name,
        'crud_entity': data_access_crud_entity,
        'create_service': create_service
    }


def generate_job_template() -> dict:
    job_class_name = input_str('Please enter the class name of the Job you\'d want to create: ')
    job_class_name = ''.join(x for x in job_class_name.title() if not x.isspace())

    return {
        'job_class_name': job_class_name,
    }


def generate_db_config() -> dict:
    migrate = input_yes_no('Do you want to use migrations?', False)

    return {
        'migrate': migrate
    }


if __name__ == "__main__":
    print(generate_db_entity_template())
