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
    __order__ = 'CRUD SoftDelete SoftDeleteToken CRUDSoftDelete CRUDSoftDeleteToken'
    CRUD = 1
    SoftDelete = 2
    SoftDeleteToken = 3
    CRUDSoftDelete = 4
    CRUDSoftDeleteToken = 5


default_db_ports = {
    DBTypes.SQLite.name: None,
    DBTypes.Postgresql.name: 5432,
    DBTypes.MySQL.name: 3306,
    DBTypes.Oracle.name: 1521,
    DBTypes.MSSQL.name: 1433,
    DBTypes.Firebird.name: 3050,
    DBTypes.Sybase.name: 5000,
}


def _generate_memorydb_config(db_log_queries: bool,
                              db_create: bool,
                              db_pool_recycle: int,
                              db_pool_pre_ping: bool,
                              db_type: int) -> dict:
    return {
        'env': {
        },
        'config': {
            'log_queries': db_log_queries,
            'create_db': db_create,
            'session': {
                'pool_recycle': db_pool_recycle,
                'pool_pre_ping': db_pool_pre_ping,
            },
            'url': {
                'protocol': DBTypes(db_type).name.lower(),
            },
        }
    }


def _generate_db_config(db_name: str, db_username: str, db_password: str, db_port: int, db_host: str,
                        db_type: int) -> dict:
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
            'username': f'${{oc.env:{db_name.upper()}_USER}}',
            'password': f'${{oc.env:{db_name.upper()}_PASSWORD}}',
            'host': f'${{oc.env:{db_name.upper()}_HOST}}',
            'port': f'${{oc.env:{db_name.upper()}_PORT}}',
            'file': f'${{oc.env:{db_name.upper()}_DB}}',
        },
    }


def generate_db_template() -> dict:
    db_template = {}
    add_db = True
    while add_db:
        db_name = input_str('What is the name of the DB connection?')
        while db_name in db_template:
            db_name = input_str(f'DB connection with name `{db_name}` already created, please enter a different name.')

        db_type = input_enum(DBTypes, 'From the following list, select the relevant number for DB type',
                             DBTypes.Postgresql.value)

        if db_type == DBTypes.SQLite.value:
            in_memory = input_yes_no('Do you want the SQLite DB in memory?', True)
            if in_memory:
                db_log_queries = input_yes_no('Do you want to log queries?', False)
                db_create = input_yes_no('Do you want create Database?', True)
                db_pool_recycle = input_int('Enter the pool recycle time: ', 3200)
                db_pool_pre_ping = input_yes_no('Do you want to set pool pre ping?', False)
                print('\nSQLite created in memory.')
                add_db = input_yes_no('\nDo you want to add another DB connection?', False)
                db_template[db_name] = _generate_memorydb_config(db_log_queries,
                                                                 db_create,
                                                                 db_pool_recycle,
                                                                 db_pool_pre_ping,
                                                                 db_type)
                continue
        db_port = input_int('Enter the port no. of your DB', default_db_ports[DBTypes(db_type).name])
        db_host = input_str('Enter host of your DB', 'localhost')
        db_username = input_str('Enter your DB username', 'user')
        db_password = input_str('Enter your DB password', )
        print(f'\n{DBTypes(db_type).name} with {db_host}:{db_port} created')
        add_db = input_yes_no('\nDo you want to add another DB connection?', False)
        db_template[db_name] = _generate_db_config(db_name, db_username, db_password, db_port, db_host, db_type)
    return db_template


def generate_solr_template() -> dict:
    solr_protocol = input_str('Enter solr protocol (http/https)', 'https')
    solr_port = input_int('Enter solr port no.', 8983)
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
            'host': f'${{oc.env:SOLR_HOST}}',
            'port': f'${{oc.env:SOLR_PORT}}',
            'file': solr_file,
        },
    }


def generate_cache_template() -> dict:
    cache_type = input_enum(CacheTypes, 'From the following list, select the relevant number for cache type',
                            CacheTypes.Memory.value)

    if cache_type == CacheTypes.Memcached.value:
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
                'host': f'${{oc.env:MEMCACHED_HOST}}',
                'port': f'${{oc.env:MEMCACHED_PORT}}',
            },
        }
    elif cache_type == CacheTypes.Memory.value:
        print(f'\nCache type {CacheTypes(cache_type).name}')
        return {
            'config': {
                'type': CacheTypes(cache_type).name.lower(),
            }
        }
    else:
        print('\nNo cache set.')


def generate_db_entity_template() -> dict:
    entities = {}
    add_entity = True
    while add_entity:
        is_soft_delete = False
        is_soft_delete_token = False
        entity_name = input_str('Enter the name of the entity you\'d like to create', 'User')
        while entity_name in entities:
            entity_name = input_str(f'Entity with name `{entity_name}` already created, please enter a different name')
        column_count = input_int('How many columns will you have in your entity? ', 0)
        columns = {}
        if column_count != 0:
            for i in range(0, column_count):
                column_name = input_str(f'Enter the name of column #{i + 1}: ')

                column_type = input_enum(DBDatatypes,
                                         f'From the following list, select the relevant number for datatype #{i + 1}',
                                         DBDatatypes.VARCHAR.value)

                column_default = input_str(f'Enter the default value of column #{i + 1}', ' ')

                columns[column_name] = {
                    'name': column_name,
                    'type': DBDatatypes(column_type).name,
                    'default': column_default
                }

            is_soft_delete = input_yes_no('Do you want to implement Soft Delete?', False)
            if is_soft_delete:
                is_soft_delete_token = input_yes_no('Do you want to implement Soft Delete Token?', False)
        add_entity = input_yes_no('\nDo you want to add another entity?', False)
        entities[entity_name] = {
            'name': entity_name,
            'columns': columns,
            'is_soft_delete': is_soft_delete,
            'is_soft_delete_token': is_soft_delete_token,
        }

    return entities


def generate_data_access_template(entities: list) -> dict:
    data_access_name = input_str('Please enter the name of the data access you\'d want to create: ', 'UserDataAccess')

    data_access_type = input_enum(DataAccessTypes,
                                  'From the following list, select the relevant number for data access type',
                                  DataAccessTypes.CRUD.value)

    data_access_crud_entity = None
    if data_access_type in [DataAccessTypes.CRUD.value, DataAccessTypes.CRUDSoftDelete.value,
                            DataAccessTypes.CRUDSoftDeleteToken.value]:
        data_access_crud_entity = input_list(entities, 'of entity to apply crud on', 1)
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
    print(generate_db_template())