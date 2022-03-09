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
db_config = generate_db_config
