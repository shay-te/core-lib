from core_lib.data_transform.helpers import get_dict_attr
from core_lib_generator.file_generators.template_generator import TemplateGenerator

# The core-lib extra (see core-lib's setup.py) needed by each connection and cache the generator can write.
CONNECTION_EXTRAS = {'SolrConnectionFactory': 'solr', 'Neo4jConnectionFactory': 'neo4j'}
PROTOCOL_EXTRAS = {'postgresql': 'postgres', 'mysql': 'mysql'}
CACHE_EXTRAS = {'redis': 'redis', 'memcached': 'memcached'}


def _connection_extras(connection) -> set:
    extras = set()
    connection_type = (get_dict_attr(connection, 'type') or '').split('.')[-1]
    if connection_type in CONNECTION_EXTRAS:
        extras.add(CONNECTION_EXTRAS[connection_type])
    # A YAML file nests the URL under `config`; the interactive generator writes it on the connection.
    protocol = get_dict_attr(connection, 'config.url.protocol') or get_dict_attr(connection, 'url.protocol') or ''
    database = protocol.split('+')[0]  # `postgresql+psycopg2` names the driver after the database
    if database in PROTOCOL_EXTRAS:
        extras.add(PROTOCOL_EXTRAS[database])
    return extras


class RequirementsGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        extras = set()
        for connection in get_dict_attr(yaml_data, 'connections') or []:
            extras |= _connection_extras(connection)
        for cache in get_dict_attr(yaml_data, 'cache') or []:
            if get_dict_attr(cache, 'type') in CACHE_EXTRAS:
                extras.add(CACHE_EXTRAS[get_dict_attr(cache, 'type')])
        if not extras:
            return template_content
        return template_content.replace('core-lib', f'core-lib[{",".join(sorted(extras))}]', 1)

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/requirements.txt'
