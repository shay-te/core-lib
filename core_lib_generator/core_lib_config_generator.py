from omegaconf import OmegaConf

from core_lib.helpers.shell_utils import input_str, input_yes_no
from core_lib_generator.core_lib_template_generator import (
    generate_db_template,
    generate_solr_template,
    generate_cache_template,
    generate_db_entity_template,
    generate_data_access_template,
    generate_job_template,
)


def _get_env_variables(data):
    key_list = list(data.keys())
    env_variables = {}
    if 'env' in key_list:
        return data['env']
    else:
        [env_variables.update(data[key]['env']) for key in key_list]
        return env_variables


config = {}
env = {}
data_layers = {}
jobs = {}
core_lib_name = input_str('Please enter the name for your Core-lib: ', 'MyCoreLib')

want_db = input_yes_no('\nWill you be using a Database?', True)
if want_db:
    print('\nPlease fill out the requested Database information.')
    db = generate_db_template()
    env.update(_get_env_variables(db))
    config.setdefault('data', {})
    for db_name in db:
        config['data'][db_name] = db[db_name]['config']

want_solr = input_yes_no('\nWill you be using Solr?', False)
if want_solr:
    print('\nPlease fill out the requested solr information.')
    solr = generate_solr_template()
    env.update(_get_env_variables(solr))
    config['data']['solr'] = solr['config']

want_cache = input_yes_no('\nWould you like to use cache?', True)
if want_cache:
    print('\nPlease fill out the requested Cache information.')
    cache = generate_cache_template()
    if 'env' in cache:
        env.update(_get_env_variables(cache))
    config['cache'] = cache['config']

want_job = input_yes_no('\nWould you like to create a Job?', False)
if want_job:
    print('\nPlease fill out the requested information for Job.')
    job = generate_job_template()
    config['data']['jobs'] = job

if want_db:
    want_entities = input_yes_no('\nWould you like to add entities?', True)
    if want_entities:
        print('\nPlease fill out the requested information for creating entities in Database.')
        db_entity = generate_db_entity_template()
        data_layers.setdefault('data', {})
        for entity_name in db_entity:
            data_layers['data'] = db_entity

        want_data_access = input_yes_no('\nDo you want to create a data access for the entities?', True)
        if want_data_access:
            print('\nPlease fill out the requested information for creating Data Access for entities.')
            data_access = generate_data_access_template(db_entity)
            data_layers.setdefault('data_access', {})
            data_layers['data_access'] = data_access

# print('\nPlease fill out the requested information for Database configuration.')
# db_config = generate_db_config()
# config['data']['db']['migration'] = db_config

conf = OmegaConf.create(
    {
        core_lib_name: {
            'env': env,
            'config': config,
            'data_layers': data_layers,
        }
    }
)
print(OmegaConf.to_yaml(conf))
# with open(f'{core_lib_name}.yaml', 'w+') as file:
#     OmegaConf.save(config=conf, f=file.name)
