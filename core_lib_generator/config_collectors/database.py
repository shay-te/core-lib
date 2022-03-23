import enum

from core_lib.helpers.shell_utils import input_str, input_enum, input_yes_no, input_int


class DBTypes(enum.Enum):
    __order__ = 'SQLite Postgresql MySQL Oracle MSSQL Firebird Sybase'
    SQLite = 1
    Postgresql = 2
    MySQL = 3
    Oracle = 4
    MSSQL = 5
    Firebird = 6
    Sybase = 7


default_db_ports = {
    DBTypes.Postgresql.name: 5432,
    DBTypes.MySQL.name: 3306,
    DBTypes.Oracle.name: 1521,
    DBTypes.MSSQL.name: 1433,
    DBTypes.Firebird.name: 3050,
    DBTypes.Sybase.name: 5000,
}


def generate_db_template() -> dict:
    db_template = {}
    add_db = True
    while add_db:
        db_name = input_str('What is the name of the DB connection?')
        while f'{db_name.lower()}' in db_template:
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
            db_template[f'{db_name.lower()}'] = _generate_db_config(
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
        db_template[f'{db_name.lower()}'] = _generate_db_config(
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
