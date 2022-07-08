from omegaconf import OmegaConf

from core_lib.data_transform.helpers import get_dict_attr
from core_lib_generator.file_generators.template_generator import TemplateGenerator


class ConfigGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        core_lib_config = {}
        data = {}
        solr = {}
        neo4j = {}
        caches = {}
        jobs = {}
        for elem in yaml_data:
            if elem == 'connections':
                config_conn = get_dict_attr(yaml_data, 'connections')
                if config_conn:
                    for conn in config_conn:
                        conn = dict(conn)
                        conn_name = get_dict_attr(conn, 'key')
                        conn.pop('key', None)
                        conn.pop('migrate', None)
                        conn_data = {}
                        conn_type = get_dict_attr(conn, 'type')
                        if conn['config_instantiate']:
                            conn.pop('config_instantiate', None)
                            conn['_target_'] = conn_type
                            conn.pop('type', None)
                            conn_data = conn
                        else:
                            conn_data = get_dict_attr(conn, 'config')
                        if 'SqlAlchemyConnectionRegistry' in conn_type:
                            data.setdefault(conn_name, conn_data)
                        elif 'SolrConnectionRegistry' in conn_type:
                            solr.setdefault(conn_name, conn_data)
                        elif 'Neo4jConnectionRegistry' in conn_type:
                            neo4j.setdefault(conn_name, conn_data)
                    if data:
                        core_lib_config.setdefault('data', data)
                    if solr:
                        core_lib_config.setdefault('solr', solr)
                    if neo4j:
                        core_lib_config.setdefault('neo4j', neo4j)
            if elem == 'cache':
                config_cache = get_dict_attr(yaml_data, 'cache')
                if config_cache:
                    for cache in config_cache:
                        cache = dict(cache)
                        cache_name = get_dict_attr(cache, 'key')
                        cache.pop('key', None)
                        caches.setdefault(cache_name, cache)
                    core_lib_config.setdefault('cache', caches)
            if elem == 'jobs':
                config_jobs = get_dict_attr(yaml_data, 'jobs')
                if config_jobs:
                    for job in config_jobs:
                        job = dict(job)
                        job_name = get_dict_attr(job, 'key')
                        job.pop('key', None)
                        jobs.setdefault(job_name, job)
                    core_lib_config.setdefault('jobs', jobs)
        config = OmegaConf.create({'core_lib': {core_lib_name: core_lib_config}})
        return template_content.replace('template', OmegaConf.to_yaml(config))

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/template_core_lib/config/template_core_lib.yaml'
