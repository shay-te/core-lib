from core_lib.helpers.string import any_to_camel
from core_lib_generator.file_generators.template_generator import TemplateGenerator


class EntityGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        updated_file = _add_columns_to_entity(template_content, yaml_data['columns'])
        entity_name = file_name
        updated_file = updated_file.replace('template', f'{entity_name.lower()}')
        updated_file = updated_file.replace('Template', f'{any_to_camel(entity_name)}')
        return updated_file

    def get_template_file(self, yaml_data: dict) -> str:
        if yaml_data['is_soft_delete'] and yaml_data['is_soft_delete_token']:
            return f'template_core_lib/template_core_lib/data_layers/data/db/entities/template_soft_delete_token.py'
        elif yaml_data['is_soft_delete'] and not yaml_data['is_soft_delete_token']:
            return f'template_core_lib/template_core_lib/data_layers/data/db/entities/template_soft_delete.py'
        else:
            return f'template_core_lib/template_core_lib/data_layers/data/db/entities/template.py'


def _add_columns_to_entity(template_content: str, columns: dict) -> str:
    import_data_types = ['INTEGER']
    id_str = 'id = Column(INTEGER, primary_key=True, nullable=False)'
    columns_str = [id_str]
    for key in columns:
        import_data_types.append(columns[key]['type'])
        column_type = columns[key]['type']
        default = None if not columns[key]['default'] else columns[key]['default']
        columns_str.append(f'{key:>{len(key) + 4}} = Column({column_type}, nullable=False, default={default})')
    updated_file = template_content.replace('# template_column', '\n'.join(columns_str))
    imports_to_add = ', '.join(set(import_data_types))
    updated_file = updated_file.replace('# template_import', f'from sqlalchemy import Column, {imports_to_add}')
    return updated_file
