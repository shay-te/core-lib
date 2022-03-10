from omegaconf import OmegaConf

from core_lib.helpers.shell_utils import input_str
from core_lib_generator.core_lib_template_generator import (
    generate_db_template,
    generate_solr_template,
    generate_cache_template,
    generate_db_entity_template,
    generate_data_access_template,
    generate_job_template,
    generate_db_config,
)


def _get_env_variables(data):
    key_list = list(data.keys())
    env_variables = {}
    if 'env' in key_list:
        return data['env']
    else:
        [env_variables.update(data[key]['env']) for key in key_list]
        return env_variables


def _get_config(name, data):
    return data[name]['config']


# core_lib_template = {'config': {}, 'env': {}}
config = {}
env = {}
data_layers = {}
jobs = {}
core_lib_name = input_str('Please enter the name for your Core-lib: ', 'MyCoreLib')
# core_lib_template.setdefault(core_lib_name, {})
# core_lib_template['config'].setdefault('data', {})

print('\nPlease fill out the requested Database information.')
db = generate_db_template()
env.update(_get_env_variables(db))
config.setdefault('data', {})
config['data'].setdefault('db', {})
for db_name in db:
    config['data']['db'][db_name] = db[db_name]['config']

print('\nPlease fill out the requested solr information.')
solr = generate_solr_template()
env.update(_get_env_variables(solr))
config['data']['solr'] = solr['config']

print('\nPlease fill out the requested Cache information.')
cache = generate_cache_template()
if 'env' in cache:
    env.update(_get_env_variables(cache))
config['cache'] = cache['config']

print('\nPlease fill out the requested information for creating entities in Database.')
db_entity = generate_db_entity_template()
data_layers.setdefault('data', {})
for entity_name in db_entity:
    data_layers['data'][entity_name] = db_entity[entity_name]

print('\nPlease fill out the requested information for creating Data Access for entities.')
data_access = generate_data_access_template(list(db_entity.keys()))
data_layers.setdefault('data_access', {})
data_layers['data_access'] = data_access
data_layers.setdefault('service', {})
data_layers['data_access'] = data_access['create_service']

print('\nPlease fill out the requested information for Job.')
job = generate_job_template()
jobs = job

print('\nPlease fill out the requested information for Database configuration.')
db_config = generate_db_config()
config['data']['db']['migration'] = db_config

conf = OmegaConf.create(
    {
        core_lib_name: {
            'env': env,
            'config': config,
            'data_layers': data_layers,
            'jobs': jobs,
        }
    }
)
print(OmegaConf.to_yaml(conf))
with open(f'{core_lib_name}.yaml', 'w+') as file:
    OmegaConf.save(config=conf, f=file.name)
