from omegaconf import OmegaConf
from enum import Enum
from core_lib.helpers.shell_utils import input_str, input_yes_no, input_enum
from core_lib.helpers.string import any_to_pascal
from core_lib_generator.config_collectors.cache import generate_cache_template
from core_lib_generator.config_collectors.data_access import generate_data_access_template
from core_lib_generator.config_collectors.database import generate_db_template
from core_lib_generator.config_collectors.db_entity import generate_db_entity_template
from core_lib_generator.config_collectors.job import generate_job_template
from core_lib_generator.config_collectors.service import generate_service_template
from core_lib_generator.config_collectors.setup_collector import generate_setup_template


def _get_env_variables(data):
    key_list = list(data.keys())
    env_variables = {}
    if 'env' in key_list:
        return data['env']
    else:
        [env_variables.update(data[key]['env']) for key in key_list]
        return env_variables


class ServerType(Enum):
    DJANGO = 1
    FLASK = 2
    NOSERVER = 3


config = {}
config.setdefault('data', [])
config.setdefault('cache', [])
config.setdefault('jobs', [])
setup = {}
setup.setdefault('data', {})
env = {}
data_layers = {}
data_layers.setdefault('data', [])
data_layers.setdefault('data_access', [])
data_layers.setdefault('service', [])
server_type: int


def _get_data_layers_config():
    want_db = input_yes_no('Will you be using a Database?', True)
    if want_db:
        print('Please fill out the requested Database information.')
        db = generate_db_template()
        env.update(_get_env_variables(db))
        for db_name in db:
            config['data'].append(db[db_name]['connection'])
        want_entities = input_yes_no('\nWould you like to add entities to your database?', True)
        if want_entities:
            print('Please fill out the requested information for creating entities in Database.')
            db_entity = generate_db_entity_template(db)
            data_layers.setdefault('data', {})
            data_layers['data'] = db_entity
            want_data_access = input_yes_no('\nDo you want to create a data access for the entities?', True)
            if want_data_access:
                print('Please fill out the requested information for creating Data Access for entities.')
                data_access = generate_data_access_template(db_entity)
                data_layers.setdefault('data_access', [])
                data_layers['data_access'] = data_access
                want_service = input_yes_no('\nDo you want to create services?', True)
                if want_service:
                    print('Please fill out the requested information for creating Service for Data Accesses.')
                    service = generate_service_template(data_access, True if len(config['cache']) > 0 else False)
                    data_layers.setdefault('service', [])
                    data_layers['service'] = service


def _get_cache_config():
    print('Please fill out the requested Cache information.')
    cache_list = generate_cache_template()
    for cache in cache_list:
        if 'env' in cache:
            env.update(_get_env_variables(cache))
        config['cache'].append(cache['cache'])


def _get_setup_details():
    print('\nPlease provide the following information for setup.py')
    setup['data'] = generate_setup_template()


def _get_jobs_config(core_lib_name: str):
    print('Please fill out the requested information for Job.')
    job = generate_job_template(core_lib_name)
    config['jobs'] = job


def create_yaml_file(core_lib_name: str):
    conf = OmegaConf.create(
        {
            'core_lib': {
                'name': core_lib_name,
                'env': env,
                'connections': config['data'],
                'caches': config['cache'],
                'jobs': config['jobs'],
                'entities': data_layers['data'],
                'data_accesses': data_layers['data_access'],
                'services': data_layers['service'],
                'setup': setup['data'],
                'server_type': server_type,
            }
        }
    )

    with open(f'{core_lib_name}.yaml', 'w+') as file:
        OmegaConf.save(config=conf, f=file.name)


def ask_server_type() -> int:
    return input_enum(ServerType,
                      '\nWhat kind of server type would you like?\n'
                      '1-Django\n'
                      '2-Flask\n'
                      '3-None\n',
                      default_value=ServerType.NOSERVER.value,
                      )


def generate_core_lib_yaml():
    core_lib_name = any_to_pascal(input_str('Please enter the name for your Core-lib', 'MyCoreLib'))

    want_cache = input_yes_no('\nWould you like to use cache?', True)
    if want_cache:
        _get_cache_config()

    _get_data_layers_config()

    want_job = input_yes_no('\nWould you like to create a Job?', False)
    if want_job:
        _get_jobs_config(core_lib_name)

    global server_type
    server_type = ask_server_type()

    want_setup = input_yes_no('\nDo you want to add setup.py?', True)
    if want_setup:
        _get_setup_details()

    create_yaml_file(core_lib_name)
    return f'{core_lib_name}.yaml'


if __name__ == '__main__':
    generate_core_lib_yaml()
