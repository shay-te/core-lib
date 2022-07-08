from core_lib.data_transform.helpers import get_dict_attr
from core_lib.helpers.string import any_to_pascal
from core_lib_generator.file_generators.template_generator import TemplateGenerator
from core_lib_generator.generator_utils.formatting_utils import add_tab_spaces


class EntityGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        updated_file = _add_columns_to_entity(template_content, get_dict_attr(yaml_data, 'columns'))
        entity_name = file_name
        updated_file = updated_file.replace('template', f'{entity_name.lower()}')
        updated_file = updated_file.replace('Template', f'{any_to_pascal(entity_name)}')
        return updated_file

    def get_template_file(self, yaml_data: dict) -> str:
        if get_dict_attr(yaml_data, 'is_soft_delete') and get_dict_attr(yaml_data, 'is_soft_delete_token'):
            return f'template_core_lib/template_core_lib/data_layers/data/db/entities/template_soft_delete_token.py'
        elif get_dict_attr(yaml_data, 'is_soft_delete') and not get_dict_attr(yaml_data, 'is_soft_delete_token'):
            return f'template_core_lib/template_core_lib/data_layers/data/db/entities/template_soft_delete.py'
        else:
            return f'template_core_lib/template_core_lib/data_layers/data/db/entities/template.py'


def _add_columns_to_entity(template_content: str, columns: dict) -> str:
    import_data_types = ['INTEGER']
    id_str = 'id = Column(INTEGER, primary_key=True, nullable=False)'
    columns_list = [id_str]
    for column in columns:
        import_data_types.append(get_dict_attr(column, 'type'))
        column_type = column['type']
        column_name = get_dict_attr(column, 'key')
        default = None if not get_dict_attr(column, 'default') else get_dict_attr(column, 'default')
        nullable = get_dict_attr(column, 'nullable')
        columns_str = f'{column_name} = Column({column_type}, nullable={nullable}, default={default})'
        columns_list.append(add_tab_spaces(columns_str))
    updated_file = template_content.replace('# template_column', '\n'.join(columns_list))
    imports_to_add = ', '.join(set(import_data_types))
    updated_file = updated_file.replace('# template_import', f'from sqlalchemy import Column, {imports_to_add}')
    return updated_file
