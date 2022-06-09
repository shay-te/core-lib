from omegaconf import OmegaConf

from core_lib.data_transform.helpers import get_dict_attr
from core_lib_generator.file_generators.template_generator import TemplateGenerator


class ConfigGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        core_lib_config = {}
        data = {}
        cache = {}
        jobs = {}
        for elem in yaml_data:
            if elem == 'connections':
                for db_conn in get_dict_attr(yaml_data, 'connections'):
                    db_conn = dict(db_conn)
                    db_conn_name = get_dict_attr(db_conn, 'key')
                    db_conn.pop('key', None)
                    db_conn.pop('migrate', None)
                    data.setdefault(db_conn_name, db_conn)
                if data:
                    core_lib_config.setdefault('data', data)
            if elem == 'cache':
                for db_conn in get_dict_attr(yaml_data, 'cache'):
                    db_conn = dict(db_conn)
                    db_conn_name = get_dict_attr(db_conn, 'key')
                    db_conn.pop('key', None)
                    cache.setdefault(db_conn_name, db_conn)
                if cache:
                    core_lib_config.setdefault('cache', cache)
            if elem == 'jobs':
                for db_conn in get_dict_attr(yaml_data, 'jobs'):
                    db_conn = dict(db_conn)
                    db_conn_name = get_dict_attr(db_conn, 'key')
                    db_conn.pop('key', None)
                    jobs.setdefault(db_conn_name, db_conn)
                if jobs:
                    core_lib_config.setdefault('jobs', jobs)
        config = OmegaConf.create({'core_lib': {core_lib_name: core_lib_config}})
        return template_content.replace('template', OmegaConf.to_yaml(config))

    def get_template_file(self, yaml_data: dict) -> str:
        return 'core_lib_generator/template_core_lib/template_core_lib/config/template_core_lib.yaml'
