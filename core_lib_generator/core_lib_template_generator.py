import enum

from pytimeparse import parse

from core_lib.helpers.shell_utils import input_enum, input_str, input_yes_no, input_int, input_bool, input_list


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
    __order__ = 'INTEGER VARCHAR BOOLEAN'
    INTEGER = 1
    VARCHAR = 2
    BOOLEAN = 3


class CacheTypes(enum.Enum):
    __order__ = 'Memcached Memory Empty'
    Memcached = 1
    Memory = 2
    Empty = 3


class DataAccessTypes(enum.Enum):
    __order__ = 'CRUD CRUDSoftDelete CRUDSoftDeleteToken'
    CRUD = 1
    CRUDSoftDelete = 2
    CRUDSoftDeleteToken = 3


default_db_ports = {
    DBTypes.Postgresql.name: 5432,
    DBTypes.MySQL.name: 3306,
    DBTypes.Oracle.name: 1521,
    DBTypes.MSSQL.name: 1433,
    DBTypes.Firebird.name: 3050,
    DBTypes.Sybase.name: 5000,
}


def _generate_db_config(
    db_type: int,
    db_name: str,
    db_username: str,
    db_password: str,
    db_port: int,
    db_host: str = 'localhost',
    db_log_queries: bool = False,
    db_create: bool = True,
    db_pool_recycle: int = 3200,
    db_pool_pre_ping: bool = False,
) -> dict:
    env = {}
    if db_type == DBTypes.SQLite.value:
        url = {
            'protocol': DBTypes(db_type).name.lower(),
        }
    else:
        url = {
            'protocol': DBTypes(db_type).name.lower(),
            'username': f'${{oc.env:{db_name.upper()}_USER}}',
            'password': f'${{oc.env:{db_name.upper()}_PASSWORD}}',
            'host': f'${{oc.env:{db_name.upper()}_HOST}}',
            'port': f'${{oc.env:{db_name.upper()}_PORT}}',
            'file': f'${{oc.env:{db_name.upper()}_DB}}',
        }
        env = {
            f'{db_name.upper()}_USER': db_username,
            f'{db_name.upper()}_PASSWORD': db_password,
            f'{db_name.upper()}_PORT': db_port,
            f'{db_name.upper()}_DB': db_name,
            f'{db_name.upper()}_HOST': db_host,
        }
    return {
        'env': env,
        'config': {
            'log_queries': db_log_queries,
            'create_db': db_create,
            'session': {
                'pool_recycle': db_pool_recycle,
                'pool_pre_ping': db_pool_pre_ping,
            },
            'url': url,
        },
    }


def _generate_data_access_config(
    name: str, crud: bool = False, crud_soft_delete: bool = False, crud_soft_delete_token: bool = False
) -> dict:
    if crud_soft_delete_token:
        return {
            'entity': name,
            'is_crud': True,
            'is_crud_soft_delete': True,
            'is_crud_soft_delete_token': True,
        }
    elif crud_soft_delete:
        return {
            'entity': name,
            'is_crud': True,
            'is_crud_soft_delete': True,
        }
    elif crud:
        return {
            'entity': name,
            'is_crud': True,
        }
    else:
        return {
            'entity': name,
        }


def generate_db_template() -> dict:
    db_template = {}
    add_db = True
    while add_db:
        db_name = input_str('What is the name of the DB connection?')
        while f'{db_name.lower()}_db' in db_template:
            db_name = input_str(f'DB connection with name `{db_name}` already created, please enter a different name.')

        db_type = input_enum(
            DBTypes, 'From the following list, select the relevant number for DB type', DBTypes.SQLite.value
        )

        db_log_queries = input_yes_no('Do you want to log queries?', False)
        db_create = input_yes_no('Do you want create Database?', True)
        db_pool_recycle = input_int('Enter the pool recycle time', 3200)
        db_pool_pre_ping = input_yes_no('Do you want to set pool pre ping?', False)
        if db_type == DBTypes.SQLite.value:
            print('SQLite in memory.')
            add_db = input_yes_no('Do you want to add another DB connection?', False)
            db_template[f'{db_name.lower()}_db'] = _generate_db_config(
                db_type,
                db_name,
                None,
                None,
                None,
                None,
                db_log_queries,
                db_create,
                db_pool_recycle,
                db_pool_pre_ping,
            )
            continue
        db_port = input_int('Enter the port no. of your DB', default_db_ports[DBTypes(db_type).name])
        db_host = input_str('Enter host of your DB', 'localhost')
        db_username = input_str('Enter your DB username', 'user')
        db_password = input_str(
            'Enter your DB password',
        )
        print(f'Database type {DBTypes(db_type).name} on {db_host}:{db_port}')
        add_db = input_yes_no('Do you want to add another DB connection?', False)
        db_template[f'{db_name.lower()}_db'] = _generate_db_config(
            db_type,
            db_name,
            db_username,
            db_password,
            db_port,
            db_host,
            db_log_queries,
            db_create,
            db_pool_recycle,
            db_pool_pre_ping,
        )
    return db_template


def generate_solr_template() -> dict:
    solr_protocol = input_str('Enter solr protocol (http/https)', 'https')
    solr_port = input_int('Enter solr port no.', 8983)
    solr_host = input_str('Enter solr host', 'localhost')
    solr_file = input_str('Enter solr file name (solr/core_name)', 'solr/mycore')
    print(f'Solr on {solr_host}:{solr_port}')
    return {
        'env': {
            'SOLR_HOST': solr_host,
            'SOLR_PORT': solr_port,
        },
        'config': {
            'url': {
                'protocol': solr_protocol,
                'host': f'${{oc.env:SOLR_HOST}}',
                'port': f'${{oc.env:SOLR_PORT}}',
                'file': solr_file,
            },
        },
    }


def generate_cache_template() -> dict:
    cache_type = input_enum(
        CacheTypes, 'From the following list, select the relevant number for cache type', CacheTypes.Memory.value
    )

    if cache_type == CacheTypes.Memcached.value:
        memcache_port = input_int('Enter your memcached server port no.', 11211)
        memcache_host = input_str('Enter your memcached server host', 'localhost')
        print(f'Cache type {CacheTypes(cache_type).name} on {memcache_host}:{memcache_port}')
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
        print(f'Cache type {CacheTypes(cache_type).name}')
        return {
            'config': {
                'type': CacheTypes(cache_type).name.lower(),
            }
        }
    else:
        print('No cache set.')


def generate_db_entity_template(db_conn_list: list) -> dict:
    entities = {}
    add_entity = True
    while add_entity:
        is_soft_delete = False
        is_soft_delete_token = False
        entity_name = input_str('Enter the name of the database entity you\'d like to create')
        if len(db_conn_list) > 1:
            entity_db = input_list(
                db_conn_list,
                f'From the following list, select the relevant number of db connection for {entity_name} entity',
                1,
            )
        else:
            entity_db = db_conn_list[0]
        while entity_name in entities:
            entity_name = input_str(f'Entity with name `{entity_name}` already created, please enter a different name')
        column_count = input_int('How many columns will you have in your entity? ', 0)
        columns = {}
        if column_count != 0:
            for i in range(0, column_count):
                column_name = input_str(f'Enter the name of column #{i + 1}')

                column_type = input_enum(
                    DBDatatypes,
                    f'From the following list, select the relevant number for datatype #{i + 1}',
                    DBDatatypes.VARCHAR.value,
                )
                if column_type == DBDatatypes.INTEGER.value:
                    column_default = input_int(f'Enter the default value of column #{i + 1}', 0)
                elif column_type == DBDatatypes.VARCHAR.value:
                    column_default = input_str(f'Enter the default value of column #{i + 1}', '', True)
                else:
                    column_default = input_bool(
                        f'Enter the default value of column #{i + 1} (true, false, 0(false), 1(true))', 'true'
                    )

                columns[column_name] = {
                    'name': column_name,
                    'type': DBDatatypes(column_type).name,
                    'default': column_default,
                }

            is_soft_delete = input_yes_no('Do you want to implement Soft Delete?', False)
            if is_soft_delete:
                is_soft_delete_token = input_yes_no('Do you want to implement Soft Delete Token?', False)
        add_entity = input_yes_no('Do you want to add another entity?', False)
        entities[entity_name.title()] = {
            'name': entity_name.title(),
            'db_connection': entity_db,
            'columns': columns,
            'is_soft_delete': is_soft_delete,
            'is_soft_delete_token': is_soft_delete_token,
        }
    migrate = input_yes_no('Do you want to create a migration for these entities?', False)
    entities['migrate'] = migrate
    return entities


def generate_data_access_template(db_entities: dict) -> dict:
    data_access = {}
    db_entities.pop('migrate', None)
    for entity in db_entities:
        data_access_name = input_str(
            f'Please enter the name of the data access you\'d want to create for `{entity}`',
            f'{entity.lower()}_data_access',
        )
        if db_entities[entity]['is_soft_delete'] and db_entities[entity]['is_soft_delete_token']:
            is_crud_soft_delete_token = input_yes_no(
                'Do you want to implement CRUD Soft Delete Token on your data access?', True
            )
            if is_crud_soft_delete_token:
                data_access[data_access_name] = _generate_data_access_config(entity, True, True, True)
            else:
                data_access[data_access_name] = _generate_data_access_config(entity)
        elif db_entities[entity]['is_soft_delete'] and not db_entities[entity]['is_soft_delete_token']:
            is_crud_soft_delete = input_yes_no('Do you want to implement CRUD Soft Delete on your data access?', True)
            if is_crud_soft_delete:
                data_access[data_access_name] = _generate_data_access_config(entity, True, True)
            else:
                data_access[data_access_name] = _generate_data_access_config(entity)
        else:
            is_crud = input_yes_no('Do you want to implement CRUD on your data access?', True)
            if is_crud:
                data_access[data_access_name] = _generate_data_access_config(entity, True)
            else:
                data_access[data_access_name] = _generate_data_access_config(entity)
    print(f'{list(data_access.keys())} created')
    return data_access


def generate_job_template() -> dict:
    name = input_str('Enter the name of the job', 'my_job')
    class_name = input_str('Please enter the Class Name for the job (UpdateCache)')
    initial_delay = input_str(
        'Please set the initial delay for the job (boot, startup, 1s, 1m, 1h, 1h30m ...)', 'startup'
    )
    if initial_delay in ['boot', 'startup']:
        initial_delay = '0s'
    while parse(initial_delay) is None:
        initial_delay = input_str(
            'Please input a relevant value for initial delay (boot, startup, 1s, 1m, 2m ...)', '1m'
        )
    frequency = input_str('Please set the frequency of the job (1s, 1m, 1h, 1h30m ...)', '', True)
    while frequency and parse(frequency) is None:
        frequency = input_str('Please input a relevant value for frequency (1s, 1m, 1h, 1h30m ...)', '', True)
    print(f'{name} job created')
    return {name: {'initial_delay': initial_delay, 'frequency': frequency, 'class_name': class_name}}


if __name__ == "__main__":
    print(generate_db_entity_template(['user', 'memoer']))
