import enum

from core_lib.helpers.shell_utils import input_str, input_enum, input_yes_no, input_int


def generate_db_template() -> dict:
    db_template = {}

    def is_exists_conn(user_input: str):
        return False if user_input in db_template else True

    add_db = True
    while add_db:
        db_name = input_str('What is the name of the DB connection?', None, False, is_exists_conn)

        db_type = input_enum(
            DBTypes, 'From the following list, select the relevant number for DB type', DBTypes.SQLite.value
        )
        db_username = None
        db_password = None
        db_port = None
        db_host = None
        db_log_queries = input_yes_no('Do you want to log queries?', False)
        db_create = input_yes_no('Do you want create Database?', True)
        db_pool_recycle = input_int('Enter the pool recycle time', 3200)
        db_pool_pre_ping = input_yes_no('Do you want to set pool pre ping?', False)
        migrate = input_yes_no(f'Do you want to create a migration?', False)
        if db_type != DBTypes.SQLite.value:
            db_port = input_int('Enter the port no. of your DB', default_db_ports[DBTypes(db_type).name])
            db_host = input_str('Enter host of your DB', 'localhost')
            db_username = input_str('Enter your DB username', 'user')
            db_password = input_str(
                'Enter your DB password',
            )
        print(f'Database type {DBTypes(db_type).name}')
        add_db = input_yes_no('Do you want to add another DB connection?', False)
        db_template[f'{db_name}'] = _generate_db_config(
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
            migrate
        )
    return db_template


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
    migrate: bool = False
) -> dict:
    config = _build_url(db_type, db_name, db_username, db_password, db_port, db_host)
    return {
        'env': config['env'],
        'connection': {
            'key': db_name,
            'migrate': migrate,
            'log_queries': db_log_queries,
            'create_db': db_create,
            'session': {
                'pool_recycle': db_pool_recycle,
                'pool_pre_ping': db_pool_pre_ping,
            },
            'url': config['url'],
        },
    }


def _build_url(
    db_type: int, db_name: str, db_username: str, db_password: str, db_port: int, db_host: str = 'localhost'
):
    url = {}
    env = {}
    if db_type != DBTypes.SQLite.value:
        if db_name:
            url.setdefault('file', f'${{oc.env:{db_name.upper()}_DB}}')
            env.setdefault(f'{db_name.upper()}_DB', db_name)
    if db_type:
        url.setdefault('protocol', DBTypes(db_type).name.lower())
    if db_username:
        url.setdefault('username', f'${{oc.env:{db_name.upper()}_USER}}')
        env.setdefault(f'{db_name.upper()}_USER', db_username)
    if db_password:
        url.setdefault('password', f'${{oc.env:{db_name.upper()}_PASSWORD}}')
        env.setdefault(f'{db_name.upper()}_PASSWORD', db_password)
    if db_port:
        url.setdefault('port', f'${{oc.env:{db_name.upper()}_PORT}}')
        env.setdefault(f'{db_name.upper()}_PORT', db_port)
    if db_host:
        url.setdefault('host', f'${{oc.env:{db_name.upper()}_HOST}}')
        env.setdefault(f'{db_name.upper()}_HOST', db_host)

    return {
        'env': env,
        'url': url,
    }
