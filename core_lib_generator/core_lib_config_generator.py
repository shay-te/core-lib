from omegaconf import OmegaConf

from core_lib_generator.core_lib_template_generator import (
    generate_db_template,
    generate_solr_template,
    generate_cache_template,
    generate_db_entity_template,
    generate_data_access_template,
    generate_job_template,
    generate_db_config,
)

db = generate_db_template()
solr = generate_solr_template()
cache = generate_cache_template()
db_entity = generate_db_entity_template()
data_access = generate_data_access_template()
job = generate_job_template()
db_config = generate_db_config()

conf = OmegaConf.create(
    {
        'db': db,
        'solr': solr,
        'cache': cache,
        'db_entity': db_entity,
        'job': job,
        'db_config': db_config,
    }
)
print(OmegaConf.to_yaml(conf))
with open('core_lib_config.yaml', 'w+') as file:
    OmegaConf.save(config=conf, f=file.name)
