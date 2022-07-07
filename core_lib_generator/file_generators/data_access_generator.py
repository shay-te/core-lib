from core_lib.data_transform.helpers import get_dict_attr
from core_lib.helpers.string import any_to_pascal
from core_lib_generator.file_generators.template_generator import TemplateGenerator
from core_lib_generator.generator_utils.formatting_utils import add_tab_spaces, remove_line
from core_lib_generator.generator_utils.helpers import generate_functions


class DataAccessGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        connections = yaml_data['connections']
        updated_file = template_content.replace('Template', file_name)
        conn = get_dict_attr(yaml_data, 'data_access.connection')
        entity = get_dict_attr(yaml_data, 'data_access.entity')
        is_init = False
        if entity:
            updated_file = updated_file.replace(
                '# template_entity_imports',
                f'from {core_lib_name}.data_layers.data.{conn}.entities.{entity.lower()} import {any_to_pascal(entity)}',
            )
            updated_file = updated_file.replace('db_entity', any_to_pascal(entity))
        else:
            updated_file = remove_line('# template_entity_imports', updated_file)
        if conn:
            is_init = True
            conn_data = {}
            for connection in connections:
                if connection.key == conn:
                    conn_data = connection
            conn_type = conn_data.type.split('.')[-1]
            if 'SqlAlchemyConnectionRegistry' in conn_type:
                updated_file = updated_file.replace('# template_connections_imports', 'from core_lib.connection.sql_alchemy_connection_registry import SqlAlchemyConnectionRegistry')
            elif 'SolrConnectionRegistry' in conn_type:
                updated_file = updated_file.replace('# template_connections_imports', 'from core_lib.connection.solr_connection_registry import SolrConnectionRegistry')
            elif 'Neo4jConnectionRegistry' in conn_type:
                updated_file = updated_file.replace('# template_connections_imports', 'from core_lib.connection.neo4j_connection_registry import Neo4jConnectionRegistry')
            init_str_list = [add_tab_spaces(f'def __init__(self, session: {conn_type}):'),
                             add_tab_spaces('self.session = session', 2)]
            updated_file = updated_file.replace('# template_init', '\n'.join(init_str_list))
        else:
            updated_file = remove_line('# template_connections_imports', updated_file)
            updated_file = remove_line('# template_init', updated_file)
        functions = get_dict_attr(yaml_data, 'data_access.functions')
        if functions:
            updated_file = generate_functions(updated_file, functions)
        else:
            if is_init:
                updated_file = remove_line('# template_functions', updated_file)
            else:
                updated_file = updated_file.replace(
                    '# template_functions',
                    add_tab_spaces('pass', 1)
                )
            updated_file = remove_line('# template_function_imports', updated_file)
        return updated_file

    def get_template_file(self, yaml_data: dict) -> str:
        if 'is_crud_soft_delete_token' in yaml_data.get('data_access'):
            return 'template_core_lib/template_core_lib/data_layers/data_access/template_crud_soft_delete_token_data_access.py'
        elif 'is_crud_soft_delete' in yaml_data.get('data_access'):
            return 'template_core_lib/template_core_lib/data_layers/data_access/template_crud_soft_delete_data_access.py'
        elif 'is_crud' in yaml_data.get('data_access'):
            return 'template_core_lib/template_core_lib/data_layers/data_access/template_crud_data_access.py'
        else:
            return (
                'template_core_lib/template_core_lib/data_layers/data_access/template_data_access.py'
            )
