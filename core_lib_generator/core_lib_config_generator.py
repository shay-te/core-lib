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

print('\nPlease fill out the requested Database information.')
db = generate_db_template()

print('\nPlease fill out the requested solr information.')
solr = generate_solr_template()

print('\nPlease fill out the requested Cache information.')
cache = generate_cache_template()

print('\nPlease fill out the requested information for creating entities in Database.')
db_entity = generate_db_entity_template()

print('\nPlease fill out the requested information for creating Data Access for entities.')
data_access = generate_data_access_template(list(db_entity.keys()))

print('\nPlease fill out the requested information for Job.')
job = generate_job_template()

print('\nPlease fill out the requested information for Database configuration.')
db_config = generate_db_config()

core_lib_name = input_str('Please enter the name for your Core-lib: ', 'MyCoreLib')
conf = OmegaConf.create(
    {
        'core_lib_name': core_lib_name,
        'db': db,
        'solr': solr,
        'cache': cache,
        'db_entity': db_entity,
        'job': job,
        'db_config': db_config,
    }
)
print(OmegaConf.to_yaml(conf))
with open(f'{core_lib_name}.yaml', 'w+') as file:
    OmegaConf.save(config=conf, f=file.name)
