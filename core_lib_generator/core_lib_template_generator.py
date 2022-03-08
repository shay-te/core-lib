def get_data():
    x = input('Enter your age : ')
    x = int(x)
    print(f'Hello, {x}')


def generate_db_template() -> dict:
    db_name = input('What is the name of the DB connection? ')
    db_name = str(db_name)

    db_list = ['SQLite', 'Postgresql', 'MySQL', 'Oracle', 'MS-SQL', 'Firebird', 'Sybase']
    [print(db_list.index(i) + 1, i) for i in db_list]

    db_type = input('From the following list, select the relevant number for DB type: ')
    db_type = db_list[int(db_type) - 1]

    if db_type == 'SQLite':
        in_memory = input('Do you want the SQLite DB in memory?(Y/N): ')
        if in_memory.upper() == 'Y':
            db_log_queries = input('Do you want to log queries?(true/false): ')
            db_log_queries = 'false' if not db_log_queries else db_log_queries
            db_create = input('Do you want create Database?(true/false): ')
            db_create = 'false' if not db_create else db_create
            db_pool_recycle = input('Enter the pool recycle time: ')
            db_pool_pre_ping = input('Do you want to set pool pre ping?(true/false): ')
            db_pool_pre_ping = 'false' if not db_pool_pre_ping else db_pool_pre_ping
            print('\nInput recorded.')
            return {
                'log_queries': db_log_queries.lower(),
                'create_db': db_create.lower(),
                'session': {
                    'pool_recycle': db_pool_recycle,
                    'pool_pre_ping': db_pool_pre_ping.lower(),
                },
                'url': {
                    'protocol': db_type.lower(),
                },
            }
    db_port = input('Enter the port no. of your DB: ')
    db_port = int(db_port)
    db_host = input('Enter host of your DB: ')
    db_host = str(db_host)
    db_username = input('Enter your DB username: ')
    db_username = str(db_username)
    db_password = input('Enter your DB password: ')
    db_password = str(db_password)
    print('\nInput recorded.')
    return {
        'env': {
            db_name.upper() + '_USER': db_username,
            db_name.upper() + '_PASSWORD': db_password,
            db_name.upper() + '_PORT': db_port,
            db_name.upper() + '_DB': db_name,
            db_name.upper() + '_HOST': db_host,
        },
        'config': {
            'protocol': db_type.lower(),
            'username': db_username,
            'password': db_password,
            'host': db_host,
            'port': db_port,
            'file': db_name,
        },
    }


def generate_solr_template() -> dict:
    solr_protocol = input('Enter solr protocol (http/https): ')
    solr_protocol = str(solr_protocol)
    solr_port = input('Enter solr port no.: ')
    solr_port = str(solr_port)
    solr_host = input('Enter solr host: ')
    solr_host = str(solr_host)
    solr_file = input('Enter solr file name (solr/core_name): ')
    solr_file = str(solr_file)
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
    cache_list = ['Memcached', 'Memory', 'Empty']
    [print(cache_list.index(i) + 1, i) for i in cache_list]

    cache_type = input('From the following list, select the relevant number for cache type: ')
    cache_type = cache_list[int(cache_type) - 1]

    if cache_type == 'Memcached':
        memcache_port = input('Enter your memcached server port no.: ')
        memcache_port = str(memcache_port)
        memcache_host = input('Enter your memcached server host: ')
        memcache_host = str(memcache_host)
        print('\nInput recorded.')
        return {
            'env': {
                'MEMCACHED_HOST': memcache_host,
                'MEMCACHED_PORT': memcache_port,
            },
            'config': {
                'type': cache_type.lower(),
                'host': memcache_host,
                'port': memcache_port,
            },
        }
    elif cache_type == 'Memory':
        print('\nInput recorded.')
        return {
            'config': {
                'type': cache_type.lower(),
            }
        }
    else:
        print('\nInput recorded.\nNo cache handler set.')


def generate_db_entity_template() -> dict:
    column_count = input('How many columns will you have in your table? ')
    column_count = int(column_count)
    entities = {}
    column_list = ['INTEGER', 'VARCHAR', 'DATETIME', 'DATE', 'BOOLEAN']
    for i in range(0, column_count):
        column_name = input(f'{i + 1}. Enter the name of column: ')
        column_name = str(column_name)

        [print(column_list.index(i) + 1, i) for i in column_list]
        column_type = input(f'{i + 1}. From the following list, select the relevant number for datatype: ')
        column_type = column_list[int(column_type) - 1]

        column_default = input(f'{i + 1}. Enter the default value of column: ')
        column_default = str(column_default)
        entities[i] = {'name': column_name, 'type': column_type, 'default': column_default}

    is_soft_delete = input('Do you want to implement Soft Delete?(true/false): ')
    is_soft_delete = 'false' if not is_soft_delete else is_soft_delete
    is_soft_delete_token = input('Do you want to implement Soft Delete Token?(true/false): ')
    is_soft_delete_token = 'false' if not is_soft_delete_token else is_soft_delete_token

    return {
        'entities': entities,
        'is_soft_delete': is_soft_delete,
        'is_soft_delete_token': is_soft_delete_token,
    }


def generate_data_access_template(entities: list) -> dict:
    data_access_name = input('Please enter the name of the data access you\'d want to create: ')
    data_access_name = str(data_access_name)

    data_access_list = ['CRUD', 'Soft Delete', 'Soft Delete Token']
    [print(data_access_list.index(i) + 1, i) for i in data_access_list]

    data_access_type_list = []
    data_access_type = input(
        'From the following list, select the relevant number for data access type (seperate number with space for multiple selection or type A to select all): ')
    if data_access_type == 'A':
        data_access_type_list = data_access_list
    else:
        entity_index = list(map(int, data_access_type.split()))
        for i in entity_index:
            data_access_type_list.append(data_access_list[int(i) - 1])

    data_access_crud_entities_list = []
    if any('CRUD' in type for type in data_access_type_list):
        [print(entities.index(i) + 1, i) for i in entities]
        data_access_crud_entities = input(
            'From the following list, select the relevant number of entity to apply crud on (seperate number with space for multiple selection or type A to select all): '
        )
        if data_access_crud_entities == 'A':
            data_access_crud_entities_list = entities
        else:
            entity_index = list(map(int, data_access_crud_entities.split()))
            for i in entity_index:
                data_access_crud_entities_list.append(entities[int(i) - 1])
    create_service = input('Do you want to create a service for the data access?(true/false): ')
    create_service = 'false' if not create_service else create_service

    return {
        'name': data_access_name,
        'type': data_access_type_list,
        'crud_entities': data_access_crud_entities_list,
        'create_service': create_service
    }


def generate_job_template() -> dict:
    job_class_name = input('Please enter the class name of the Job you\'d want to create: ')
    job_class_name = ''.join(x for x in job_class_name.title() if not x.isspace())

    return {
        'job_class_name': job_class_name,
    }


def generate_db_config() -> dict:
    migrate = input('Do you want to use migrations?(true/false): ')
    migrate = 'false' if not migrate else migrate

    return {
        'migrate': migrate
    }


if __name__ == "__main__":
    print(generate_db_config())
