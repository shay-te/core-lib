import os
import shutil

from core_lib.helpers.string import snake_to_camel
from core_lib_generator.generator_file_utils import replace_file_strings, replace_file_line
from core_lib_generator.file_generators.template_generate import TemplateGenerate


class DataAccessGenerateTemplate(TemplateGenerate):
    def handle(self, template_file: str, yaml_data: dict, core_lib_name: str) -> str:
        new_file = template_file.replace('Template', yaml_data['name'])
        db_conn = yaml_data['db_connection']
        entity = yaml_data['entity']
        new_file = new_file.replace(
            '# template_entity_imports',
            f'from {core_lib_name}.core_lib.data_layers.data.{db_conn}.entities.{entity.lower()} import {entity.title()}'
        )
        new_file = new_file.replace('db_entity', entity.title())
        return new_file

    def get_template_file(self, yaml_data: dict) -> str:
        if 'is_crud_soft_delete_token' in yaml_data:
            return 'template_core_lib/core_lib/data_layers/data_access/template_crud_soft_delete_token_data_access.py'
        elif 'is_crud_soft_delete' in yaml_data:
            return 'template_core_lib/core_lib/data_layers/data_access/template_crud_soft_delete_data_access.py'
        elif 'is_crud' in yaml_data:
            return 'template_core_lib/core_lib/data_layers/data_access/template_crud_data_access.py'
        else:
            return 'template_core_lib/core_lib/data_layers/data_access/template_data_access.py'


class DataAccessGenerateImports(TemplateGenerate):
    def handle(self, template_file: str, yaml_data: dict):
        pass

    def get_template_file(self, yaml_data: dict) -> str:
        pass


class DataAccessGenerateInstances(TemplateGenerate):
    def handle(self, template_file: str, yaml_data: dict):
        pass

    def get_template_file(self, yaml_data: dict) -> str:
        pass


def _create_data_access(file_path: str, data_access_type: str, name: str):
    template_class_name = snake_to_camel(data_access_type).replace('Crud', 'CRUD')
    da_file_name = f'{file_path}'
    if not os.path.isfile(da_file_name):
        shutil.copy(
            f'template_core_lib/core_lib/data_layers/data_access/{data_access_type}.py',
            da_file_name,
        )
        replace_file_strings(
            da_file_name,
            f'{template_class_name}',
            f'{name}',
        )


def add_data_access_instances(da_data: dict, core_lib_name: str):
    inst_list = []
    handler_list = []
    filename = f'{core_lib_name}/core_lib/{core_lib_name}.py'
    replace_file_line(
        filename,
        '# template_data_handlers_imports',
        'from core_lib.data_layers.data.handler.sql_alchemy_data_handler_registry import SqlAlchemyDataHandlerRegistry',
    )
    for name in da_data:
        entity = da_data[name]['entity']
        db_connection = da_data[name]['db_connection']
        inst_str = f'self.{entity.lower()} = {name}({entity.title()}, {db_connection}_session)'
        inst_list.append(inst_str.rjust(len(inst_str) + 8))
        handler_str = f'{db_connection}_session = SqlAlchemyDataHandlerRegistry(self.config.data.{db_connection})'
        handler_list.append(handler_str.rjust(len(handler_str) + 8))
    replace_file_line(filename, '# template_da_instances', '\n'.join(inst_list))
    replace_file_line(filename, '# template_data_handlers', '\n'.join(set(handler_list)))
